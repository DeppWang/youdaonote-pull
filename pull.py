#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import platform
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from enum import Enum
from typing import Tuple

import requests
from win32_setctime import setctime

from core import log
from core.api import YoudaoNoteApi
from core.common import get_script_directory
from core.covert import YoudaoNoteConvert
from core.image import ImagePull

__author__ = "Depp Wang (deppwxq@gmail.com)"
__github__ = "https//github.com/DeppWang/youdaonote-pull"

REGEX_SYMBOL = re.compile(r'[\\/:\*\?"<>\|]')  # 符号：\ / : * ? " < > |
MARKDOWN_SUFFIX = ".md"


class FileType(Enum):
    OTHER = 0
    MARKDOWN = 1
    XML = 2
    JSON = 3


class FileActionEnum(Enum):
    CONTINUE = "跳过"
    ADD = "新增"
    UPDATE = "更新"


class YoudaoNotePull(object):
    """
    有道云笔记 Pull 封装
    """

    def __init__(self):
        self.root_local_dir = None  # 本地文件根目录
        self.youdaonote_api = None
        self.smms_secret_token = None
        self.is_relative_path = None  # 是否使用相对路径

    def _covert_config(self, config_path=None) -> Tuple[dict, str]:
        """
        转换配置文件为 dict
        :param config_path: config 文件路径
        :return: (config_dict, error_msg)
        """

        config_path = (
            config_path
            if config_path
            else os.path.join(get_script_directory(), "config.json")
        )
        with open(config_path, "rb") as f:
            config_str = f.read().decode("utf-8")

        try:
            config_dict = json.loads(config_str)
        except:
            return (
                {},
                "请检查「config.json」格式是否为 utf-8 格式的 json！建议使用 Sublime 编辑「config.json」",
            )

        key_list = ["local_dir", "ydnote_dir", "smms_secret_token", "is_relative_path"]
        if key_list != list(config_dict.keys()):
            return (
                {},
                "请检查「config.json」的 key 是否分别为 local_dir, ydnote_dir, smms_secret_token, is_relative_path",
            )
        return config_dict, ""

    def _check_local_dir(self, local_dir, test_default_dir=None) -> Tuple[str, str]:
        """
        检查本地文件夹
        :param local_dir: 本地文件夹名（绝对路径）
        :return: local_dir, error_msg
        """
        # 如果没有指定本地文件夹，当前目录新增 youdaonote 目录
        if not local_dir:
            add_dir = test_default_dir if test_default_dir else "youdaonote"
            # 兼容 Windows 系统，将路径分隔符（\\）替换为 /
            local_dir = os.path.join(get_script_directory(), add_dir).replace("\\", "/")

        # 如果指定的本地文件夹不存在，创建文件夹
        if not os.path.exists(local_dir):
            try:
                os.mkdir(local_dir)
            except:
                return "", "请检查「{}」上层文件夹是否存在，并使用绝对路径！".format(local_dir)
        return local_dir, ""

    def _get_ydnote_dir_id(self, ydnote_dir) -> Tuple[str, str]:
        """
        获取指定有道云笔记指定目录 ID
        :param ydnote_dir: 指定有道云笔记指定目录
        :return: dir_id, error_msg
        """
        root_dir_info = self.youdaonote_api.get_root_dir_info_id()
        root_dir_id = root_dir_info["fileEntry"]["id"]

        # 如果不指定文件夹，取根目录 ID
        if not ydnote_dir:
            return root_dir_id, ""

        dir_info = self.youdaonote_api.get_dir_info_by_id(root_dir_id)
        for entry in dir_info["entries"]:
            file_entry = entry["fileEntry"]
            if file_entry["name"] == ydnote_dir:
                return file_entry["id"], ""

        return "", "有道云笔记指定顶层目录不存在"

    def get_ydnote_dir_id(self) -> Tuple[str, str]:
        """
        获取有道云笔记根目录或指定目录 ID
        :return:
        """
        config_dict, error_msg = self._covert_config()
        if error_msg:
            return "", error_msg
        local_dir, error_msg = self._check_local_dir(local_dir=config_dict["local_dir"])
        if error_msg:
            return "", error_msg
        self.root_local_dir = local_dir
        self.youdaonote_api = YoudaoNoteApi()
        error_msg = self.youdaonote_api.login_by_cookies()
        logging.info("本次使用 Cookies 登录")
        if error_msg:
            return "", error_msg
        self.smms_secret_token = config_dict["smms_secret_token"]
        self.is_relative_path = config_dict["is_relative_path"]
        return self._get_ydnote_dir_id(ydnote_dir=config_dict["ydnote_dir"])

    def _judge_type(self, file_id, youdao_file_suffix) -> Enum:
        """
        判断笔记类型
        :param file_id:
        :param youdao_file_suffix:
        :return:
        """
        file_type = FileType.OTHER
        # 1、如果文件是 .md 类型
        if youdao_file_suffix == MARKDOWN_SUFFIX:
            file_type = FileType.MARKDOWN
            return file_type
        elif (
            youdao_file_suffix == ".note"
            or youdao_file_suffix == ".clip"
            or youdao_file_suffix == ""
        ):
            response = self.youdaonote_api.get_file_by_id(file_id)
            # 2、如果文件以 `<?xml` 开头
            if response.content[:5] == b"<?xml":
                file_type = FileType.XML
            # 3、如果文件以 `{` 开头
            elif response.content.startswith(b'{"'):
                file_type = FileType.JSON
        return file_type

    def _get_file_action(self, local_file_path, modify_time) -> Enum:
        """
        获取文件操作行为
        :param local_file_path:
        :param modify_time:
        :return: FileActionEnum
        """
        # 如果不存在，则下载
        if not os.path.exists(local_file_path):
            return FileActionEnum.ADD

        # 如果已经存在，判断是否需要更新
        # 如果有道云笔记文件更新时间小于本地文件时间，说明没有更新，则不下载，跳过
        if modify_time <= os.path.getmtime(local_file_path):
            logging.info("此文件「%s」不更新，跳过", local_file_path)
            return FileActionEnum.CONTINUE
        # 同一目录存在同名 md 和 note 文件时，后更新文件将覆盖另一个
        return FileActionEnum.UPDATE

    def _optimize_file_name(self, name) -> str:
        """
        优化文件名
        :param name:
        :return:
        """
        # 替换下划线
        regex_symbol = re.compile(r"[<]")  # 符号： <
        # 删除特殊字符
        del_regex_symbol = re.compile(r'[\\/":\|\*\?#>]')  # 符号：\ / " : | * ? # >
        # 首尾的空格
        name = name.replace("\n", "")
        # 去除换行符
        name = name.strip()
        # 替换一些特殊符号
        name = regex_symbol.sub("_", name)
        name = del_regex_symbol.sub("", name)
        return name

    def pull_dir_by_id_recursively(self, dir_id, local_dir):
        """
        根据目录 ID 循环遍历下载目录下所有文件
        :param dir_id:
        :param local_dir: 本地目录
        :return: error_msg
        """
        dir_info = self.youdaonote_api.get_dir_info_by_id(dir_id)
        try:
            entries = dir_info["entries"]
        except KeyError:
            raise KeyError("有道云笔记修改了接口地址，此脚本暂时不能使用！请提 issue")
        for entry in entries:
            file_entry = entry["fileEntry"]
            id = file_entry["id"]
            name = file_entry["name"]
            if file_entry["dir"]:
                sub_dir = os.path.join(local_dir, name).replace("\\", "/")
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
                self.pull_dir_by_id_recursively(id, sub_dir)
            else:
                modify_time = file_entry["modifyTimeForSort"]
                create_time = file_entry["createTimeForSort"]
                self._add_or_update_file(id, name, local_dir, modify_time, create_time)

    def _add_or_update_file(
        self, file_id, file_name, local_dir, modify_time, create_time
    ):
        """
        新增或更新文件
        :param file_id:
        :param file_name:
        :param local_dir:
        :param modify_time:
        :param create_time:
        :return:
        """
        file_name = self._optimize_file_name(file_name)
        youdao_file_suffix = os.path.splitext(file_name)[1]  # 笔记后缀
        original_file_path = os.path.join(local_dir, file_name).replace(
            "\\", "/"
        )  # 原后缀路径

        # 所有类型文件均下载，不做处理
        file_type = self._judge_type(file_id, youdao_file_suffix)

        # 「文档」类型本地文件均已 .md 结尾
        local_file_path = (
            os.path.join(
                local_dir, "".join([os.path.splitext(file_name)[0], MARKDOWN_SUFFIX])
            ).replace("\\", "/")
            if file_type != FileType.OTHER
            else original_file_path
        )

        # 如果有有道云笔记是「文档」类型，则提示类型
        tip = (
            "，云笔记原格式为 {}".format(file_type.name) if file_type != FileType.OTHER else ""
        )

        file_action = self._get_file_action(local_file_path, modify_time)
        if file_action == FileActionEnum.CONTINUE:
            return
        if file_action == FileActionEnum.UPDATE:
            # 考虑到使用 f.write() 直接覆盖原文件，在 Windows 下报错（WinError 183），先将其删除
            os.remove(local_file_path)
        try:
            self._pull_file(
                file_id,
                original_file_path,
                local_file_path,
                file_type,
                youdao_file_suffix,
            )
            if file_action == FileActionEnum.CONTINUE:
                logging.debug(
                    "{}「{}」{}".format(file_action.value, local_file_path, tip)
                )
            else:
                logging.info("{}「{}」{}".format(file_action.value, local_file_path, tip))

            # 本地文件时间设置为有道云笔记的时间
            if platform.system() == "Windows":
                setctime(local_file_path, create_time)
            else:
                os.utime(local_file_path, (create_time, modify_time))

        except Exception as error:
            logging.info(
                "{}「{}」可能失败！请检查文件！错误提示：{}".format(
                    file_action.value, original_file_path, format(error)
                )
            )

    def _pull_file(
        self, file_id, file_path, local_file_path, file_type, youdao_file_suffix
    ):
        """
        下载文件
        :param file_id:
        :param file_path:
        :param local_file_path: 本地
        :param file_type:
        :param youdao_file_suffix:
        :return:
        """
        # 1、所有的都先下载
        response = self.youdaonote_api.get_file_by_id(file_id)
        with open(file_path, "wb") as f:
            f.write(response.content)  # response.content 本身就是字节类型

        # 2、如果文件是 note 类型，将其转换为 MarkDown 类型
        if file_type == FileType.XML:
            try:
                YoudaoNoteConvert.covert_xml_to_markdown(file_path)
            except ET.ParseError:
                logging.info("此 note 笔记应该为 17 年以前新建，格式为 html，将转换为 Markdown ...")
                YoudaoNoteConvert.covert_html_to_markdown(file_path)
            except Exception as e:
                logging.info("note 笔记转换 MarkDown 失败，将跳过", repr(e))
        elif file_type == FileType.JSON:
            YoudaoNoteConvert.covert_json_to_markdown(file_path)

        # 3、迁移文本文件里面的有道云笔记图片（链接）
        if file_type != FileType.OTHER or youdao_file_suffix == MARKDOWN_SUFFIX:
            imagePull = ImagePull(
                self.youdaonote_api, self.smms_secret_token, self.is_relative_path
            )
            imagePull.migration_ydnote_url(local_file_path)


if __name__ == "__main__":
    log.init_logging()

    start_time = int(time.time())

    try:
        youdaonote_pull = YoudaoNotePull()
        ydnote_dir_id, error_msg = youdaonote_pull.get_ydnote_dir_id()
        if error_msg:
            logging.info(error_msg)
            sys.exit(1)
        logging.info("正在 pull，请稍后 ...")
        youdaonote_pull.pull_dir_by_id_recursively(
            ydnote_dir_id, youdaonote_pull.root_local_dir
        )
    except requests.exceptions.ProxyError:
        logging.info(
            "请检查网络代理设置；也有可能是调用有道云笔记接口次数达到限制，请等待一段时间后重新运行脚本，若一直失败，可删除「cookies.json」后重试"
        )
        traceback.print_exc()
        logging.info("已终止执行")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logging.info("网络错误，请检查网络是否正常连接。若突然执行中断，可忽略此错误，重新运行脚本")
        traceback.print_exc()
        logging.info("已终止执行")
        sys.exit(1)
    # 链接错误等异常
    except Exception as err:
        logging.info("Cookies 可能已过期！其他错误：", format(err))
        traceback.print_exc()
        logging.info("已终止执行")
        sys.exit(1)

    end_time = int(time.time())
    logging.info("运行完成！耗时 {} 秒".format(str(end_time - start_time)))
