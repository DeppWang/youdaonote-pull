#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
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
from core.config import AppConfig, load_config
from core.covert import YoudaoNoteConvert
from core.image import ImagePull

__author__ = "Depp Wang (deppwxq@gmail.com)"
__github__ = "https//github.com/DeppWang/youdaonote-pull"

REGEX_SYMBOL = re.compile(r'[\\/:\*\?"<>\|]')
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
    """有道云笔记 Pull 封装。"""

    def __init__(self):
        self.root_local_dir = None
        self.youdaonote_api = None
        self.is_relative_path = None
        self.config = AppConfig()

    def _covert_config(self, config_path=None) -> Tuple[dict, str]:
        """兼容历史测试与调用，返回 dict。"""
        config, error_msg = load_config(config_path)
        return config.to_dict(), error_msg

    def _check_local_dir(self, local_dir, test_default_dir=None) -> Tuple[str, str]:
        """检查并创建导出根目录。"""
        if not local_dir:
            add_dir = test_default_dir if test_default_dir else "youdaonote"
            local_dir = os.path.join(".", add_dir).replace("\\", "/")

        if not os.path.exists(local_dir):
            try:
                os.mkdir(local_dir)
            except Exception:
                return "", "请检查“{}”上层文件夹是否存在，并使用绝对路径".format(local_dir)
        return local_dir, ""

    def _get_ydnote_dir_id(self, ydnote_dir) -> Tuple[str, str]:
        """获取有道云笔记根目录或指定目录 ID。"""
        root_dir_info = self.youdaonote_api.get_root_dir_info_id()
        root_dir_id = root_dir_info["fileEntry"]["id"]
        if not ydnote_dir:
            return root_dir_id, ""

        dir_info = self.youdaonote_api.get_dir_info_by_id(root_dir_id)
        for entry in dir_info["entries"]:
            file_entry = entry["fileEntry"]
            if file_entry["name"] == ydnote_dir:
                return file_entry["id"], ""

        return "", "有道云笔记指定顶层目录不存在"

    def get_ydnote_dir_id(self, config_path=None) -> Tuple[str, str]:
        """读取配置并初始化运行时状态。"""
        config, error_msg = load_config(config_path)
        if error_msg:
            return "", error_msg

        local_dir, error_msg = self._check_local_dir(local_dir=config.local_dir)
        if error_msg:
            return "", error_msg

        self.config = config
        self.root_local_dir = local_dir
        self.youdaonote_api = YoudaoNoteApi()
        error_msg = self.youdaonote_api.login_by_cookies()
        logging.info("本次使用 Cookies 登录")
        if error_msg:
            return "", error_msg
        self.is_relative_path = config.is_relative_path
        return self._get_ydnote_dir_id(ydnote_dir=config.ydnote_dir)

    def _judge_type(self, file_id, youdao_file_suffix) -> Enum:
        """判断笔记类型。"""
        file_type = FileType.OTHER
        if youdao_file_suffix == MARKDOWN_SUFFIX:
            return FileType.MARKDOWN
        if youdao_file_suffix in (".note", ".clip", ""):
            response = self.youdaonote_api.get_file_by_id(file_id)
            if response.content[:5] == b"<?xml":
                file_type = FileType.XML
            elif response.content.startswith(b'{"'):
                file_type = FileType.JSON
        return file_type

    def _get_file_action(self, local_file_path, modify_time) -> Enum:
        """判断文件需要新增、更新还是跳过。"""
        if not os.path.exists(local_file_path):
            return FileActionEnum.ADD

        if modify_time <= os.path.getmtime(local_file_path):
            logging.info("此文件“%s”无更新，跳过", local_file_path)
            return FileActionEnum.CONTINUE
        return FileActionEnum.UPDATE

    def _optimize_file_name(self, name) -> str:
        """清理 Windows 不允许的文件名字符。"""
        regex_symbol = re.compile(r"[<]")
        del_regex_symbol = re.compile(r'[\\/":\|\*\?#>]')
        name = name.replace("\n", "")
        name = name.strip()
        name = regex_symbol.sub("_", name)
        name = del_regex_symbol.sub("", name)
        return name

    def pull_dir_by_id_recursively(self, dir_id, local_dir):
        """递归下载目录下所有文件。"""
        dir_info = self.youdaonote_api.get_dir_info_by_id(dir_id)
        try:
            entries = dir_info["entries"]
        except KeyError:
            raise KeyError("有道云笔记修改了接口地址，此脚本暂时不能使用，请提 issue")
        for entry in entries:
            file_entry = entry["fileEntry"]
            file_id = file_entry["id"]
            name = file_entry["name"]
            if file_entry["dir"]:
                sub_dir = os.path.join(local_dir, name).replace("\\", "/")
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
                self.pull_dir_by_id_recursively(file_id, sub_dir)
            else:
                modify_time = file_entry["modifyTimeForSort"]
                create_time = file_entry["createTimeForSort"]
                self._add_or_update_file(
                    file_id,
                    name,
                    local_dir,
                    modify_time,
                    create_time,
                )

    def _add_or_update_file(
        self, file_id, file_name, local_dir, modify_time, create_time
    ):
        """新增或更新单个文件。"""
        file_name = self._optimize_file_name(file_name)
        youdao_file_suffix = os.path.splitext(file_name)[1]
        original_file_path = os.path.join(local_dir, file_name).replace("\\", "/")

        file_type = self._judge_type(file_id, youdao_file_suffix)
        local_file_path = (
            os.path.join(
                local_dir, "".join([os.path.splitext(file_name)[0], MARKDOWN_SUFFIX])
            ).replace("\\", "/")
            if file_type != FileType.OTHER
            else original_file_path
        )

        tip = (
            "，云笔记原格式为 {}".format(file_type.name)
            if file_type != FileType.OTHER
            else ""
        )

        file_action = self._get_file_action(local_file_path, modify_time)
        if file_action == FileActionEnum.CONTINUE:
            return
        if file_action == FileActionEnum.UPDATE:
            os.remove(local_file_path)
        try:
            self._pull_file(
                file_id,
                original_file_path,
                local_file_path,
                file_type,
                youdao_file_suffix,
            )
            logging.info("{}“{}”{}".format(file_action.value, local_file_path, tip))

            if platform.system() == "Windows":
                setctime(local_file_path, create_time)
            else:
                os.utime(local_file_path, (create_time, modify_time))
        except Exception as error:
            logging.info(
                "{}“{}”可能失败，请检查文件。错误提示：{}".format(
                    file_action.value, original_file_path, format(error)
                )
            )

    def _pull_file(
        self, file_id, file_path, local_file_path, file_type, youdao_file_suffix
    ):
        """下载文件并在需要时转 Markdown。"""
        response = self.youdaonote_api.get_file_by_id(file_id)
        with open(file_path, "wb") as f:
            f.write(response.content)

        if file_type == FileType.XML:
            try:
                YoudaoNoteConvert.covert_xml_to_markdown(file_path)
            except ET.ParseError:
                logging.info("旧版 note 识别为 HTML，转为 Markdown")
                YoudaoNoteConvert.covert_html_to_markdown(file_path)
            except Exception as error:
                logging.info("note 转换 Markdown 失败，将跳过 %r", error)
        elif file_type == FileType.JSON:
            YoudaoNoteConvert.covert_json_to_markdown(file_path)

        if file_type != FileType.OTHER or youdao_file_suffix == MARKDOWN_SUFFIX:
            image_pull = ImagePull(self.youdaonote_api, self.config)
            image_pull.migration_ydnote_url(local_file_path)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", action="store_true", help="打开配置界面")
    parser.add_argument("--config", dest="config_path", help="指定配置文件路径")
    return parser.parse_args(argv)


def run_pull(config_path=None) -> int:
    log.init_logging()
    start_time = int(time.time())

    try:
        youdaonote_pull = YoudaoNotePull()
        ydnote_dir_id, error_msg = youdaonote_pull.get_ydnote_dir_id(config_path)
        if error_msg:
            logging.info(error_msg)
            return 1
        logging.info("正在 pull，请稍后 ...")
        youdaonote_pull.pull_dir_by_id_recursively(
            ydnote_dir_id, youdaonote_pull.root_local_dir
        )
    except requests.exceptions.ProxyError:
        logging.info(
            "请检查网络代理设置；也可能是调用有道云笔记接口次数达到限制，请等待一段时间后重新运行脚本，若一直失败，可删除“cookies.json”后重试"
        )
        traceback.print_exc()
        logging.info("已终止执行")
        return 1
    except requests.exceptions.ConnectionError:
        logging.info("网络错误，请检查网络是否正常连接。若突然执行中断，可忽略此错误，重新运行脚本")
        traceback.print_exc()
        logging.info("已终止执行")
        return 1
    except Exception as err:
        logging.info("Cookies 可能已过期，或出现其他错误：%s", format(err))
        traceback.print_exc()
        logging.info("已终止执行")
        return 1

    end_time = int(time.time())
    logging.info("运行完成，耗时 {} 秒".format(str(end_time - start_time)))
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.ui:
        from core.config_ui import open_config_ui

        return open_config_ui(args.config_path)
    return run_pull(args.config_path)


if __name__ == "__main__":
    sys.exit(main())
