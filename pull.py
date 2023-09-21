#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from enum import Enum
from urllib import parse
from urllib.parse import urlparse
from datetime import datetime

import yaml
import frontmatter
import requests

__author__ = 'Depp Wang (deppwxq@gmail.com)'
__github__ = 'https//github.com/DeppWang/youdaonote-pull'

REGEX_SYMBOL = re.compile(r'[\\/:\*\?"<>\|]')  # 符号：\ / : * ? " < > |
REGEX_IMAGE_URL = re.compile(r'!\[.*?\]\((.*?note\.youdao\.com.*?)\)')
REGEX_ATTACH = re.compile(r'\[(.*?)\]\(((http|https)://note\.youdao\.com.*?)\)')
MARKDOWN_SUFFIX = '.md'
NOTE_SUFFIX = '.note'
# 有道云笔记的图片地址
IMAGES = 'images'
# 有道云笔记的附件地址
ATTACH = 'attachments'


class FileActionEnum(Enum):
    CONTINUE = "跳过"
    ADD = "新增"
    UPDATE = "更新"


class XmlElementConvert(object):
    """
    XML Element 转换规则
    """

    @staticmethod
    def convert_para_func(**kwargs):
        # 正常文本
        # 粗体、斜体、删除线、链接
        return kwargs.get('text')

    @staticmethod
    def convert_heading_func(**kwargs):
        # 标题
        level = kwargs.get('element').attrib.get('level', 0)
        level = 1 if level in (['a', 'b']) else level
        text = kwargs.get('text')
        return ' '.join(["#" * int(level), text]) if text else text

    @staticmethod
    def convert_image_func(**kwargs):
        # 图片
        image_url = XmlElementConvert.get_text_by_key(list(kwargs.get('element')), 'source')
        return '![{text}]({image_url})'.format(text=kwargs.get('text'), image_url=image_url)

    @staticmethod
    def convert_attach_func(**kwargs):
        # 附件
        element = kwargs.get('element')
        filename = XmlElementConvert.get_text_by_key(list(element), 'filename')
        resource_url = XmlElementConvert.get_text_by_key(list(element), 'resource')
        return '[{text}]({resource_url})'.format(text=filename, resource_url=resource_url)

    @staticmethod
    def convert_code_func(**kwargs):
        # 代码块
        language = XmlElementConvert.get_text_by_key(list(kwargs.get('element')), 'language')
        return '```{language}\r\n{code}```'.format(language=language, code=kwargs.get('text'))

    @staticmethod
    def convert_todo_func(**kwargs):
        # to-do
        return '- [ ] {text}'.format(text=kwargs.get('text'))

    @staticmethod
    def convert_quote_func(**kwargs):
        # 引用
        return '> {text}'.format(text=kwargs.get('text'))

    @staticmethod
    def convert_horizontal_line_func(**kwargs):
        # 分割线
        return '---'

    @staticmethod
    def convert_list_item_func(**kwargs):
        # 列表
        list_id = kwargs.get('element').attrib['list-id']
        is_ordered = kwargs.get('list_item').get(list_id)
        text = kwargs.get('text')
        if is_ordered == 'unordered':
            return '- {text}'.format(text=text)
        elif is_ordered == 'ordered':
            return '1. {text}'.format(text=text)

    @staticmethod
    def convert_table_func(**kwargs):
        """
        表格转换
        :param kwargs:
        :return:
        """
        element = kwargs.get('element')
        content = XmlElementConvert.get_text_by_key(element, 'content')

        table_data_str = f''  # f-string 多行字符串
        nl = '\r\n'  # 考虑 Windows 系统，换行符设为 \r\n
        table_data = json.loads(content)
        table_data_len = len(table_data['widths'])
        table_data_arr = []
        table_data_line = []

        for cells in table_data['cells']:
            values = cells.get('value')
            if values is None:
                values = ''
            cell_value = XmlElementConvert._encode_string_to_md(values)
            table_data_line.append(cell_value)
            # 攒齐一行放到 table_data_arr 中，并重置 table_data_line
            if len(table_data_line) == table_data_len:
                table_data_arr.append(table_data_line)
                table_data_line = []

        # 如果只有一行，那就给他加一个空白 title 行
        if len(table_data_arr) == 1:
            table_data_arr.insert(0, [ch for ch in (" " * table_data_len)])
            table_data_arr.insert(1, [ch for ch in ("-" * table_data_len)])
        elif len(table_data_arr) > 1:
            table_data_arr.insert(1, [ch for ch in ("-" * table_data_len)])

        for table_line in table_data_arr:
            table_data_str += "|"
            for table_data in table_line:
                table_data_str += f' %s |' % table_data
            table_data_str += f'{nl}'

        return table_data_str

    @staticmethod
    def get_text_by_key(element_children, key='text'):
        """
        获取文本内容
        :return:
        """
        for sub_element in element_children:
            if key in sub_element.tag:
                return sub_element.text if sub_element.text else ''
        return ''

    @staticmethod
    def _encode_string_to_md(original_text):
        """ 将字符串转义 防止 markdown 识别错误 """

        if len(original_text) <= 0 or original_text == " ":
            return original_text

        original_text = original_text.replace('\\', '\\\\')  # \\ 反斜杠
        original_text = original_text.replace('*', '\\*')  # \* 星号
        original_text = original_text.replace('_', '\\_')  # \_ 下划线
        original_text = original_text.replace('#', '\\#')  # \# 井号

        # markdown 中需要转义的字符
        original_text = original_text.replace('&', '&amp;')
        original_text = original_text.replace('<', '&lt;')
        original_text = original_text.replace('>', '&gt;')
        original_text = original_text.replace('“', '&quot;')
        original_text = original_text.replace('‘', '&apos;')

        original_text = original_text.replace('\t', '&emsp;')

        # 换行 <br>
        original_text = original_text.replace('\r\n', '<br>')
        original_text = original_text.replace('\n\r', '<br>')
        original_text = original_text.replace('\r', '<br>')
        original_text = original_text.replace('\n', '<br>')

        return original_text


class YoudaoNoteConvert(object):
    """
    有道云笔记 xml 内容转换为 markdown 内容
    """

    @staticmethod
    def covert_html_to_markdown(file_path):
        """
        转换 HTML 为 MarkDown
        :param file_path:
        :return:
        """
        with open(file_path, 'rb') as f:
            content_str = f.read().decode('utf-8')
        from markdownify import markdownify as md
        # 如果换行符丢失，使用 md(content_str.replace('<br>', '<br><br>').replace('</div>', '</div><br><br>')).rstrip()
        new_content = md(content_str)
        base = os.path.splitext(file_path)[0]
        new_file_path = ''.join([base, MARKDOWN_SUFFIX])
        os.rename(file_path, new_file_path)
        with open(new_file_path, 'wb') as f:
            f.write(new_content.encode())

    @staticmethod
    def covert_xml_to_markdown_content(file_path):
        # 使用 xml.etree.ElementTree 将 xml 文件转换为对象
        element_tree = ET.parse(file_path)
        note_element = element_tree.getroot()  # note Element

        # list_item 的 id 与 type 的对应
        list_item = {}
        for child in note_element[0]:
            if 'list' in child.tag:
                list_item[child.attrib['id']] = child.attrib['type']

        body_element = note_element[1]  # Element
        new_content_list = []
        for element in list(body_element):
            text = XmlElementConvert.get_text_by_key(list(element))
            name = element.tag.replace('{http://note.youdao.com}', '').replace('-', '_')
            convert_func = getattr(XmlElementConvert, 'convert_{}_func'.format(name), None)
            # 如果没有转换，只保留文字
            if not convert_func:
                new_content_list.append(text)
                continue
            line_content = convert_func(text=text, element=element, list_item=list_item)
            new_content_list.append(line_content)
        return f'\r\n\r\n'.join(new_content_list)  # 换行 1 行

    @staticmethod
    def covert_xml_to_markdown(file_path) -> bool:
        """
        转换 XML 为 MarkDown
        :param file_path:
        :return:
        """
        base = os.path.splitext(file_path)[0]
        new_file_path = ''.join([base, MARKDOWN_SUFFIX])
        # 如果文件为空，结束
        if os.path.getsize(file_path) == 0:
            os.rename(file_path, new_file_path)
            return False

        new_content = YoudaoNoteConvert.covert_xml_to_markdown_content(file_path)
        os.rename(file_path, new_file_path)
        with open(new_file_path, 'wb') as f:
            f.write(new_content.encode('utf-8'))
        return True


class ImageUpload(object):
    """
    图片上传到指定图床
    """

    @staticmethod
    def upload_to_smms(youdaonote_api, image_url, smms_secret_token) -> (str, str):
        """
        上传图片到 sm.ms
        :param image_url:
        :param smms_secret_token:
        :return: url, error_msg
        """
        try:
            smfile = youdaonote_api.http_get(image_url).content
        except:
            error_msg = '下载「{}」失败！图片可能已失效，可浏览器登录有道云笔记后，查看图片是否能正常加载'.format(image_url)
            return '', error_msg
        files = {'smfile': smfile}
        upload_api_url = 'https://sm.ms/api/v2/upload'
        headers = {'Authorization': smms_secret_token}

        error_msg = 'SM.MS 免费版每分钟限额 20 张图片，每小时限额 100 张图片，大小限制 5 M，上传失败！「{}」未转换，' \
                    '将下载图片到本地'.format(image_url)
        try:
            res_json = requests.post(upload_api_url, headers=headers, files=files, timeout=5).json()
        except requests.exceptions.ProxyError as err:
            error_msg = '网络错误，上传「{}」到 SM.MS 失败！将下载图片到本地。错误提示：{}'.format(image_url, format(err))
            return '', error_msg
        except Exception:
            return '', error_msg

        if res_json.get('success'):
            url = res_json['data']['url']
            print('已将图片「{}」转换为「{}」'.format(image_url, url))
            return url, ''
        if res_json.get('code') == 'image_repeated':
            url = res_json['images']
            print('已将图片「{}」转换为「{}」'.format(image_url, url))
            return url, ''
        if res_json.get('code') == 'flood':
            return '', error_msg

        error_msg = '上传「{}」到 SM.MS 失败，请检查图片 url 或 smms_secret_token（{}）是否正确！将下载图片到本地'.format(
            image_url, smms_secret_token)
        return '', error_msg


class YoudaoNoteApi(object):
    """
    有道云笔记 API 封装
    原理：https://depp.wang/2020/06/11/how-to-find-the-api-of-a-website-eg-note-youdao-com/
    """

    ROOT_ID_URL = 'https://note.youdao.com/yws/api/personal/file?method=getByPath&keyfrom=web&cstk={cstk}'
    DIR_MES_URL = 'https://note.youdao.com/yws/api/personal/file/{dir_id}?all=true&f=true&len=1000&sort=1' \
                  '&isReverse=false&method=listPageByParentId&keyfrom=web&cstk={cstk}'
    FILE_URL = 'https://note.youdao.com/yws/api/personal/sync?method=download&_system=macos&_systemVersion=&' \
               '_screenWidth=1280&_screenHeight=800&_appName=ynote&_appuser=0123456789abcdeffedcba9876543210&' \
               '_vendor=official-website&_launch=16&_firstTime=&_deviceId=0123456789abcdef&_platform=web&' \
               '_cityCode=110000&_cityName=&sev=j1&keyfrom=web&cstk={cstk}'

    def __init__(self, cookies_path=None):
        """
        初始化
        :param cookies_path:
        """
        self.session = requests.session()  # 使用 session 维持有道云笔记的登陆状态
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/100.0.4896.88 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        self.cookies_path = cookies_path if cookies_path else 'cookies.json'
        self.cstk = None

    def login_by_cookies(self) -> str:
        """
        使用 Cookies 登录，其实就是设置 Session 的 Cookies
        :return: error_msg
        """
        try:
            cookies = self._covert_cookies()
        except Exception as err:
            return format(err)
        for cookie in cookies:
            self.session.cookies.set(name=cookie[0], value=cookie[1], domain=cookie[2], path=cookie[3])
        self.cstk = cookies[0][1] if cookies[0][0] == 'YNOTE_CSTK' else None  # cstk 用于请求时接口验证
        if not self.cstk:
            return 'YNOTE_CSTK 字段为空'
        print('本次使用 Cookies 登录')

    def _covert_cookies(self) -> list:
        """
        读取 cookies 文件的 cookies，并转换为字典
        :return: cookies
        """
        with open(self.cookies_path, 'rb') as f:
            json_str = f.read().decode('utf-8')

        try:
            cookies_dict = json.loads(json_str)  # 将字符串转换为字典
            cookies = cookies_dict['cookies']
        except Exception:
            raise Exception('转换「{}」为字典时出现错误'.format(self.cookies_path))
        return cookies

    def http_post(self, url, data=None, files=None):
        """
        封装 post 请求
        :param url:
        :param data:
        :param files:
        :return: response
        """
        return self.session.post(url, data=data, files=files)

    def http_get(self, url):
        """
        封装 get 请求
        :param url:
        :return: response
        """
        return self.session.get(url)

    def get_root_dir_info_id(self) -> dict:
        """
        获取有道云笔记根目录信息
        :return: {
            'fileEntry': {'id': 'test_root_id', 'name': 'ROOT', ...},
            ...
        }
        """
        data = {'path': '/', 'entire': 'true', 'purge': 'false', 'cstk': self.cstk}
        return self.http_post(self.ROOT_ID_URL.format(cstk=self.cstk), data=data).json()

    def get_dir_info_by_id(self, dir_id) -> dict:
        """
        根据目录 ID 获取目录下所有文件信息
        :return: {
            'count': 3,
            'entries': [
                 {'fileEntry': {'id': 'test_dir_id', 'name': 'test_dir', 'dir': true, ...}},
                 {'fileEntry': {'id': 'test_note_id', 'name': 'test_note', 'dir': false, ...}}
                 ...
            ]
        }
        """
        url = self.DIR_MES_URL.format(dir_id=dir_id, cstk=self.cstk)
        return self.http_get(url).json()

    def get_file_by_id(self, file_id):
        """
        根据文件 ID 获取文件内容
        :param file_id:
        :return: response，内容为笔记字节码
        """
        data = {'fileId': file_id, 'version': -1, 'convert': 'true', 'editorType': 1, 'cstk': self.cstk}
        url = self.FILE_URL.format(cstk=self.cstk)
        return self.http_post(url, data=data)


class AdditionalArgs(object):
    """
    支持简单的命令行配置
    """
    PATCH_MARKDOWN_FRONT_MATTER  = False
    RETRY_DOWNLOAD_MARKDOWN_URL  = False


class YoudaoNotePull(object):
    """
    有道云笔记 Pull 封装
    """
    CONFIG_PATH = 'config.json'

    def __init__(self):
        self.root_local_dir = None  # 本地文件根目录
        self.youdaonote_api = None
        self.smms_secret_token = None
        self.is_relative_path = None  # 是否使用相对路径

    def get_ydnote_dir_id(self):
        """
        获取有道云笔记根目录或指定目录 ID
        :return:
        """
        config_dict, error_msg = self._covert_config()
        if error_msg:
            return '', error_msg
        local_dir, error_msg = self._check_local_dir(local_dir=config_dict['local_dir'])
        if error_msg:
            return '', error_msg
        self.root_local_dir = local_dir
        self.youdaonote_api = YoudaoNoteApi()
        error_msg = self.youdaonote_api.login_by_cookies()
        if error_msg:
            return '', error_msg
        self.smms_secret_token = config_dict['smms_secret_token']
        self.is_relative_path = config_dict['is_relative_path']
        return self._get_ydnote_dir_id(ydnote_dir=config_dict['ydnote_dir'])

    def pull_dir_by_id_recursively(self, dir_id, local_dir):
        """
        根据目录 ID 循环遍历下载目录下所有文件
        :param dir_id:
        :param local_dir: 本地目录
        :return: error_msg
        """
        dir_info = self.youdaonote_api.get_dir_info_by_id(dir_id)
        try:
            entries = dir_info['entries']
        except KeyError:
            raise KeyError('有道云笔记修改了接口地址，此脚本暂时不能使用！请提 issue')
        for entry in entries:
            file_entry = entry['fileEntry']
            id = file_entry['id']
            name = file_entry['name']
            if file_entry['dir']:
                sub_dir = os.path.join(local_dir, name).replace('\\', '/')
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
                self.pull_dir_by_id_recursively(id, sub_dir)
            else:
                modify_time = file_entry['modifyTimeForSort']
                self._add_or_update_file(id, name, local_dir, modify_time, entry)

    def _covert_config(self, config_path=None) -> (dict, str):
        """
        转换配置文件为 dict
        :param config_path: config 文件路径
        :return: (config_dict, error_msg)
        """
        config_path = config_path if config_path else self.CONFIG_PATH
        with open(config_path, 'rb') as f:
            config_str = f.read().decode('utf-8')

        try:
            config_dict = json.loads(config_str)
        except:
            return {}, '请检查「config.json」格式是否为 utf-8 格式的 json！建议使用 Sublime 编辑「config.json」'

        key_list = ['local_dir', 'ydnote_dir', 'smms_secret_token', 'is_relative_path']
        if key_list != list(config_dict.keys()):
            return {}, '请检查「config.json」的 key 是否分别为 local_dir, ydnote_dir, smms_secret_token, is_relative_path'
        return config_dict, ''

    def _check_local_dir(self, local_dir, test_default_dir=None) -> (str, str):
        """
        检查本地文件夹
        :param local_dir: 本地文件夹名（绝对路径）
        :return: local_dir, error_msg
        """
        # 如果没有指定本地文件夹，当前目录新增 youdaonote 目录
        if not local_dir:
            add_dir = test_default_dir if test_default_dir else 'youdaonote'
            # 兼容 Windows 系统，将路径分隔符（\\）替换为 /
            local_dir = os.path.join(os.getcwd(), add_dir).replace('\\', '/')

        # 如果指定的本地文件夹不存在，创建文件夹
        if not os.path.exists(local_dir):
            try:
                os.mkdir(local_dir)
            except:
                return '', '请检查「{}」上层文件夹是否存在，并使用绝对路径！'.format(local_dir)
        return local_dir, ''

    def _get_ydnote_dir_id(self, ydnote_dir) -> (str, str):
        """
        获取指定有道云笔记指定目录 ID
        :param ydnote_dir: 指定有道云笔记指定目录
        :return: dir_id, error_msg
        """
        root_dir_info = self.youdaonote_api.get_root_dir_info_id()
        root_dir_id = root_dir_info['fileEntry']['id']
        # 如果不指定文件夹，取根目录 ID
        if not ydnote_dir:
            return root_dir_id, ''

        dir_info = self.youdaonote_api.get_dir_info_by_id(root_dir_id)
        for entry in dir_info['entries']:
            file_entry = entry['fileEntry']
            if file_entry['name'] == ydnote_dir:
                return file_entry['id'], ''

        return '', '有道云笔记指定顶层目录不存在'

    def _additional_file_action(self, local_file_path, entry):
        """
        对本地文件额外操作, 支持多次运行重试.

        Args:
            local_file_path (_type_): _description_
            entry (_type_): _description_
        """
        if not os.path.exists(local_file_path):
            return

        # 添加 markdown frontmatter 参数
        if AdditionalArgs.PATCH_MARKDOWN_FRONT_MATTER:
            self._patch_markdown_front_matter(local_file_path, entry)
        
        # 额外重试下载失败的图片和附件链接 (失败的链接仍然保持youdao.com的标记, 可以直接重试)
        if AdditionalArgs.RETRY_DOWNLOAD_MARKDOWN_URL:
            self._migration_ydnote_url(local_file_path)

    def _add_or_update_file(self, file_id, file_name, local_dir, modify_time, entry):
        """
        新增或更新文件
        :param file_id:
        :param file_name:
        :param local_dir:
        :param modify_time:
        :return:
        """
        file_name = self._optimize_file_name(file_name)
        youdao_file_suffix = os.path.splitext(file_name)[1]  # 笔记后缀
        original_file_path = os.path.join(local_dir, file_name).replace('\\', '/')  # 原后缀路径
        is_note = self._judge_is_note(file_id, youdao_file_suffix)
        # 「note」类型本地文件均已 .md 结尾
        local_file_path = os.path.join(local_dir, ''.join([os.path.splitext(file_name)[0], MARKDOWN_SUFFIX])).replace(
            '\\', '/') if is_note else original_file_path
        # 如果有有道云笔记是「note」类型，则提示类型
        tip = '，云笔记原格式为 note' if is_note else ''
        file_action = self._get_file_action(local_file_path, modify_time)
        self._additional_file_action(local_file_path, entry)
        if file_action == FileActionEnum.CONTINUE:
            return
        if file_action == FileActionEnum.UPDATE:
            # 考虑到使用 f.write() 直接覆盖原文件，在 Windows 下报错（WinError 183），先将其删除
            os.remove(local_file_path)
        try:
            self._pull_file(file_id, original_file_path, local_file_path, is_note, youdao_file_suffix, entry)
            print('{}「{}」{}'.format(file_action.value, local_file_path, tip))
        except Exception as error:
            print('{}「{}」失败！请检查文件！错误提示：{}'.format(file_action.value, original_file_path, format(error)))

    def _judge_is_note(self, file_id, youdao_file_suffix):
        """
        判断是否是 note 类型
        :param file_id:
        :param youdao_file_suffix:
        :return:
        """
        is_note = False
        # 1、如果文件是 .note 类型
        if youdao_file_suffix == NOTE_SUFFIX:
            is_note = True
        # 2、如果文件没有类型后缀，但以 `<?xml` 开头
        if not youdao_file_suffix:
            response = self.youdaonote_api.get_file_by_id(file_id)
            content = response.content[:5]
            is_note = True if content == b"<?xml" else False
        return is_note

    def _pull_file(self, file_id, file_path, local_file_path, is_note, youdao_file_suffix, entry):
        """
        下载文件
        :param file_id:
        :param file_path:
        :param local_file_path: 本地
        :param is_note:
        :param youdao_file_suffix:
        :return:
        """
        # 1、所有的都先下载
        response = self.youdaonote_api.get_file_by_id(file_id)
        with open(file_path, 'wb') as f:
            f.write(response.content)  # response.content 本身就是字节类型

        # 2、如果文件是 note 类型，将其转换为 MarkDown 类型
        if is_note:
            try:
                YoudaoNoteConvert.covert_xml_to_markdown(file_path)
            except ET.ParseError:
                print('此 note 笔记应该为 17 年以前新建，格式为 html，将转换为 Markdown ...')
                YoudaoNoteConvert.covert_html_to_markdown(file_path)
            except Exception as e:
                print('note 笔记转换 MarkDown 失败，将跳过', repr(e))

        # 3、迁移文本文件里面的有道云笔记链接
        if is_note or youdao_file_suffix == MARKDOWN_SUFFIX:
            self._migration_ydnote_url(local_file_path)
        
        # 4、增加markdown frontmatter信息
        if AdditionalArgs.PATCH_MARKDOWN_FRONT_MATTER:
            self._patch_markdown_front_matter(local_file_path, entry)

    def _patch_markdown_front_matter(self, local_file_path, file_params):
        """
        将有道云笔记的参数做为markdown的frontmatter记录, 主要用于记录创建时间和修改时间.

        Args:
            local_file_path (_type_): _description_
            file_params (_type_): _description_
        """
        
        if not local_file_path.endswith(".md"):
            print(f"非markdown文件, 不需要处理markdown frontmatter: {local_file_path}")
            return
        
        file_entry =  file_params["fileEntry"]
        with open(local_file_path, "r") as f:
            try:
                fm = frontmatter.load(f)
            except yaml.scanner.ScannerError as ex:
                print(f"识别 markdown frontmatter错误, 忽略. file {f} except: {ex}")
                return
            remote_modified_time = file_entry["modifyTimeForSort"]
            stored_update_time = fm.metadata.get("noteMeta", {}).get("modifyTimeForSort", -1)
            if stored_update_time >= remote_modified_time:
                return
            fm.metadata["noteMeta"] = {
                "id": file_entry["id"],
                "name":  file_entry["name"],
                "parentId":  file_entry["parentId"],
                "version": file_entry["version"],
                "fileSize": file_entry["fileSize"],
                "checksum": file_entry["checksum"],
                "createTimeForSort":  file_entry["createTimeForSort"],
                "modifyTimeForSort":  file_entry["modifyTimeForSort"]
            }
            fm.metadata["createTime"] = datetime.fromtimestamp(file_entry["createTimeForSort"]).isoformat()
            fm.metadata["modifyTime"] = datetime.fromtimestamp(file_entry["modifyTimeForSort"]).isoformat()
            print(f"update metadata: {file_entry['name']} modified at {fm.metadata['modifyTime']}")
        frontmatter.dump(fm, local_file_path)           

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
        if modify_time < os.path.getmtime(local_file_path):
            logging.info('此文件「%s」不更新，跳过', local_file_path)
            return FileActionEnum.CONTINUE
        # 同一目录存在同名 md 和 note 文件时，后更新文件将覆盖另一个
        return FileActionEnum.UPDATE

    def _optimize_file_name(self, name) -> str:
        """
        优化文件名，替换特殊符号为下划线
        :param name:
        :return:
        """
        name = REGEX_SYMBOL.sub('_', name)
        return name

    def _migration_ydnote_url(self, file_path):
        """
        迁移有道云笔记文件 URL
        :param file_path:
        :return:
        """
        
        # 有道笔记后来支持直接上传excel等附件, 这类文件不需要迁移url
        # 不然下方会报错 /youdao-backup/abc.xlsx 'utf-8' codec can't decode byte 0x87 in position 10: invalid start byte
        if not file_path.endswith(".md"):
            print(f"非markdown文件, 不需要处理markdown链接: {file_path}")
            return
        
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8')

        # 图片
        image_urls = REGEX_IMAGE_URL.findall(content)
        if len(image_urls) > 0:
            print('正在转换有道云笔记「{}」中的有道云图片链接...'.format(file_path))
        for image_url in image_urls:
            image_path = self._get_new_image_path(file_path, image_url)
            if image_url == image_path:
                continue
            #将绝对路径替换为相对路径，实现满足 Obsidian 格式要求
            #将 image_path 路径中 images 之前的路径去掉，只保留以 images 开头的之后的路径
            if self.is_relative_path:
                image_path = image_path[image_path.find(IMAGES):]
            # 其实 image 与附件的正则表达式差不多, 不过这里先处理了图片, 就不会继续尝试附件下载了
            content = content.replace(image_url, image_path)

        # 附件
        attach_name_and_url_list = REGEX_ATTACH.findall(content)
        if len(attach_name_and_url_list) > 0:
            print('正在转换有道云笔记「{}」中的有道云附件链接...'.format(file_path))
        for attach_name_and_url in attach_name_and_url_list:
            attach_url = attach_name_and_url[1]
            attach_path = self._download_ydnote_url(file_path, attach_url, attach_name_and_url[0])
            if not attach_path:
                continue
            # 将 attach_path 路径中 attachments 之前的路径去掉，只保留以 attachments 开头的之后的路径
            if self.is_relative_path:
                attach_path = attach_path[attach_path.find(ATTACH):]
            content = content.replace(attach_url, attach_path)

        with open(file_path, 'wb') as f:
            f.write(content.encode())
        return

    def _get_new_image_path(self, file_path, image_url) -> str:
        """
        将图片链接转换为新的链接
        :param file_path:
        :param image_url:
        :return: new_image_path
        """
        # 当 smms_secret_token 为空（不上传到 SM.MS），下载到图片到本地
        if not self.smms_secret_token:
            image_path = self._download_ydnote_url(file_path, image_url)
            return image_path or image_url

        # smms_secret_token 不为空，上传到 SM.MS
        new_file_url, error_msg = ImageUpload.upload_to_smms(youdaonote_api=self.youdaonote_api, image_url=image_url,
                                                             smms_secret_token=self.smms_secret_token)
        # 如果上传失败，仍下载到本地
        if not error_msg:
            return new_file_url
        print(error_msg)
        image_path = self._download_ydnote_url(file_path, image_url)
        return image_path or image_url

    def _download_ydnote_url(self, file_path, url, attach_name=None) -> str:
        """
        下载文件到本地，返回本地路径
        :param file_path:
        :param url:
        :param attach_name:
        :return:  path
        """
        
        # patch for: requests.exceptions.MissingSchema: Invalid URL '//note.youdao.com/src/xxxx
        if url.startswith("//note.youdao.com"):
            url = "https:" + url

        try:            
            response = self.youdaonote_api.http_get(url)
        except requests.exceptions.ProxyError as err:
            error_msg = '网络错误，「{}」下载失败。错误提示：{}'.format(url, format(err))
            print(error_msg)
            return ''

        content_type = response.headers.get('Content-Type')
        file_type = '附件' if attach_name else '图片'
        if response.status_code != 200 or not content_type:
            error_msg = f'下载「{url}」失败！{file_type}可能已失效，可浏览器登录有道云笔记后，查看{file_type}是否能正常加载: statusCode: {response.status_code}, content_type: {content_type}'
            print(error_msg)
            return ''

        if attach_name:
            # 默认下载附件到 attachments 文件夹
            file_dirname = ATTACH
            file_suffix = attach_name
        else:
            # 默认下载图片到 images 文件夹
            file_dirname = IMAGES
            # 后缀 png 和 jpeg 后可能出现 ; `**.png;`, 原因未知
            content_type_arr = content_type.split('/')
            file_suffix = '.' + content_type_arr[1].replace(';', '') if len(content_type_arr) == 2 else "jpg"

        local_file_dir = None
        #如果 file_name 中不包含 . 号
        if file_path.find('.') == -1:
            local_file_dir = os.path.join(self.root_local_dir, file_dirname).replace('\\', '/')
        else :
            #截取字符串 file_path 中文件夹全路径(即实现在具体文件夹目录下再生成图片文件夹路径，而非在根目录生成图片文件夹路径)
            local_file_dir = os.path.join(file_path[:file_path.rfind('/')], file_dirname).replace('\\', '/')

        if not os.path.exists(local_file_dir):
            os.mkdir(local_file_dir)
        file_basename = os.path.basename(urlparse(url).path)
        #请求后的真实的URL中才有东西
        realUrl = parse.parse_qs(urlparse(response.url).query)
        if realUrl:
            urlname = 'filename'
            if 'download' in realUrl:
                urlname = 'download'
            # dict 不为空再去取 download
            file_name = file_basename + realUrl[urlname][0]
        else:
            file_name = ''.join([file_basename, file_suffix])
        local_file_path = os.path.join(local_file_dir, file_name).replace('\\', '/')
        try:
            with open(local_file_path, 'wb') as f:
                f.write(response.content)  # response.content 本身就为字节类型
            print('已将{}「{}」转换为「{}」'.format(file_type, url, local_file_path))
        except:
            error_msg = '{} {}有误！'.format(url, file_type)
            print(error_msg)
            return ''

        # relative_file_path = self._set_relative_file_path(file_path, file_name, local_file_dir)
        return local_file_path

    def _set_relative_file_path(self, file_path, file_name, local_file_dir) -> str:
        """
        图片/附件设置为相对地址
        :param file_path:
        :param file_name:
        :param local_file_dir:
        :return:
        """
        note_file_dir = os.path.dirname(file_path)
        rel_file_dir = os.path.relpath(local_file_dir, note_file_dir)
        rel_file_path = os.path.join(rel_file_dir, file_name)
        new_file_path = rel_file_path.replace('\\', '/')
        return new_file_path


if __name__ == '__main__':
    start_time = int(time.time())
    
    # 简化版命令行解析, 支持导出markdown frontmatter, 支持重试文章中的图片和附件链接
    print(f"sys args: {sys.argv}")
    if "--frontmatter" in sys.argv:
        AdditionalArgs.PATCH_MARKDOWN_FRONT_MATTER = True
    if "--retryurl" in sys.argv:
        AdditionalArgs.RETRY_DOWNLOAD_MARKDOWN_URL = True
    print(f"Additional Args: {AdditionalArgs.PATCH_MARKDOWN_FRONT_MATTER}, {AdditionalArgs.RETRY_DOWNLOAD_MARKDOWN_URL}")
    
    try:
        youdaonote_pull = YoudaoNotePull()
        ydnote_dir_id, error_msg = youdaonote_pull.get_ydnote_dir_id()
        if error_msg:
            print(error_msg)
            sys.exit(1)
        print('正在 pull，请稍后 ...')
        youdaonote_pull.pull_dir_by_id_recursively(ydnote_dir_id, youdaonote_pull.root_local_dir)
    except requests.exceptions.ProxyError as proxyErr:
        print('请检查网络代理设置；也有可能是调用有道云笔记接口次数达到限制，请等待一段时间后重新运行脚本，若一直失败，可删除「cookies.json」后重试')
        traceback.print_exc()
        print('已终止执行')
        sys.exit(1)
    except requests.exceptions.ConnectionError as connectionErr:
        print('网络错误，请检查网络是否正常连接。若突然执行中断，可忽略此错误，重新运行脚本')
        traceback.print_exc()
        print('已终止执行')
        sys.exit(1)
    # 链接错误等异常
    except Exception as err:
        print('其他错误：', format(err))
        traceback.print_exc()
        print('已终止执行')
        sys.exit(1)

    end_time = int(time.time())
    print('运行完成！耗时 {} 秒'.format(str(end_time - start_time)))
