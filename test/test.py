# -*- coding:utf-8 -*-

from __future__ import absolute_import

import os
import unittest
from unittest.mock import patch, mock_open, Mock

from pull import YoudaoNoteApi, YoudaoNotePull, YoudaoNoteConvert

# 使用 test_cookies.json 作为 cookies 地址，避免 cookies.json 数据在运行测试用例时被错误覆盖
TEST_COOKIES_PATH = 'test_cookies.json'


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class YoudaoNoteApiTest(unittest.TestCase):
    """
    测试有道云笔记 API
    python test.py YoudaoNoteApiTest
    """

    # 使用 test_cookies.json 作为 cookies 地址，避免 cookies.json 数据在运行测试用例时被错误覆盖
    TEST_COOKIES_PATH = 'test_cookies.json'

    def test_cookies_login(self):
        """
        测试 cookies 登录
        python test.py YoudaoNoteApiTest.test_cookies_login
        """

        # 如果 cookies 文件不存在。期待：登录失败
        youdaonote_api = YoudaoNoteApi(cookies_path=self.TEST_COOKIES_PATH)
        message = youdaonote_api.login_by_cookies()
        self.assertTrue('No such file or directory' in message)

        # 如果 cookies 格式不对（少了一个 [）。期待：登录失败
        cookies_json_str = """{
                "cookies": 
                    ["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"],
                    ["YNOTE_LOGIN", "3||1591964671668", ".note.youdao.com", "/"],
                    ["YNOTE_SESS", "***", ".note.youdao.com", "/"],
                }"""

        youdaonote_api = YoudaoNoteApi(cookies_path=self.TEST_COOKIES_PATH)
        with patch('builtins.open', mock_open(read_data=cookies_json_str.encode('utf-8'))):
            message = youdaonote_api.login_by_cookies()
            self.assertEqual(message, '转换「{}」为字典时出现错误'.format(self.TEST_COOKIES_PATH))

        # 如果 cookies 格式正确，但少了 YNOTE_CSTK。期待：登录失败
        cookies_json_str = """{"cookies": [
                                    ["YNOTE_LOGIN", "3||1591964671668", ".note.youdao.com", "/"],
                                    ["YNOTE_SESS", "***", ".note.youdao.com", "/"]
                                ]}"""
        youdaonote_api = YoudaoNoteApi(cookies_path=self.TEST_COOKIES_PATH)
        with patch('builtins.open', mock_open(read_data=cookies_json_str.encode('utf-8'))):
            message = youdaonote_api.login_by_cookies()
            self.assertEqual(message, 'YNOTE_CSTK 字段为空')

        # 如果 cookies 格式正确，并包含 YNOTE_CSTK。期待：登录成功
        cookies_json_str = """{"cookies": [
                                    ["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"],
                                    ["YNOTE_LOGIN", "3||1591964671668", ".note.youdao.com", "/"],
                                    ["YNOTE_SESS", "***", ".note.youdao.com", "/"]
                                ]}"""
        youdaonote_api = YoudaoNoteApi(cookies_path=self.TEST_COOKIES_PATH)
        with patch('builtins.open', mock_open(read_data=cookies_json_str.encode('utf-8'))):
            message = youdaonote_api.login_by_cookies()
            self.assertFalse(message)
            self.assertEqual(youdaonote_api.cstk, "fPk5IkDg")

    def test_get_root_dir_info_id(self):
        """
        测试获取有道云笔记根目录信息
        python test.py YoudaoNoteApiTest.test_get_root_dir_info_id
        """

        # 先 mock 登录一下
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch('pull.YoudaoNoteApi._covert_cookies',
                   return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]]):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        # 接口返回正常时。期待：根目录信息中有根目录 ID
        youdaonote_api.http_post = Mock(
            return_value=MockResponse({'fileEntry': {'id': 'test_root_id', 'name': 'ROOT'}}, 200))
        root_dir_info = youdaonote_api.get_root_dir_info_id()
        self.assertEqual(root_dir_info['fileEntry']['id'], 'test_root_id')

    def test_get_dir_info_by_id(self):
        """
        测试根据目录 ID 获取目录下所有文件信息
        python test.py YoudaoNoteApiTest.test_get_dir_info_by_id
        """

        # 先 mock 登录一下
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch('pull.YoudaoNoteApi._covert_cookies',
                   return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]]):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        # 当目录 ID 存在时。期待获取正常
        youdaonote_api.http_get = Mock(return_value=MockResponse({'count': 2, 'entries': [
            {'fileEntry': {'id': 'test_dir_id', 'name': 'test_dir', 'dir': True}},
            {'fileEntry': {'id': 'test_note_id', 'name': 'test_note', 'dir': False}}]}, 200))
        dir_info = youdaonote_api.get_dir_info_by_id(dir_id='test_dir_id')
        self.assertEqual(dir_info['count'], 2)
        self.assertTrue(dir_info['entries'][0]['fileEntry']['dir'])
        self.assertFalse(dir_info['entries'][1]['fileEntry']['dir'])

    def test_get_file_by_id(self):
        """
        测试根据文件 ID 获取文件内容
        python test.py YoudaoNoteApiTest.test_get_file_by_id
        """

        # 先 mock 登录一下
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch('pull.YoudaoNoteApi._covert_cookies',
                   return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]]):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        # 当文件 ID 存在时。期待获取正常
        youdaonote_api.http_post = Mock(return_value=MockResponse({}, 200))
        file = youdaonote_api.get_file_by_id(file_id='test_note_id')
        self.assertTrue(file)


class YoudaoNoteCovert(unittest.TestCase):
    """
    python test.py YoudaoNoteCovert
    """

    def test_covert_xml_to_markdown_content(self):
        """
        测试 xml 转换 markdown
        python test.py YoudaoNoteCovert.test_covert_xml_to_markdown_content
        """
        content = YoudaoNoteConvert.covert_xml_to_markdown_content('test.note')
        with open('test.md', 'rb') as f:
            content_target = f.read().decode()
        # CRLF => \r\n, LF => \n
        self.assertEqual(content.replace('\r\n', '\n'), content_target)

    def test_html_to_markdown(self):
        """
        测试 html 转换 markdown
        :return:
        """
        from markdownify import markdownify as md
        new_content = md(
            f"""<div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: "Monaco","Consolas","Lucida Console","Courier New","serif"; font-size: 12px; background-color: rgb(247, 247, 247);'><a href="http://bbs.pcbeta.com/viewthread-1095891-1-1.html">http://bbs.pcbeta.com/viewthread-1095891-1-1.html</a><br></span></div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: "Monaco","Consolas","Lucida Console","Courier New","serif"; font-size: 12px; background-color: rgb(247, 247, 247);'><div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: "Monaco","Consolas","Lucida Console","Courier New","serif"; font-size: 12px; background-color: rgb(247, 247, 247);'><br></span></div>sudo perl -pi -e 's|\x75\x30\x89\xd8|\xeb\x30\x89\xd8|' /System/Library/Extensions/AppleRTC.kext/Contents/MacOS/AppleRTC</span>
""")
        expected_content = """<http://bbs.pcbeta.com/viewthread-1095891-1-1.html>  
  
sudo perl -pi -e 's|u0Ø|ë0Ø|' /System/Library/Extensions/AppleRTC.kext/Contents/MacOS/AppleRTC """
        self.assertEqual(new_content, expected_content)


class YoudaoNotePullTest(unittest.TestCase):
    TEST_CONFIG_PATH = 'test_config.json'

    def test_covert_config_json(self):
        """
        测试 config.json 文件
        python test.py YoudaoNotePullTest.test_covert_config_json
        """
        youdaonote_pull = YoudaoNotePull()

        # 当格式错误时。期待：转换失败
        config_json_str = """
                "local_dir": "",
                "ydnote_dir": "",
                "smms_secret_token": ""
            }
            """
        with patch('builtins.open', mock_open(read_data=config_json_str.encode('utf-8'))):
            config_dict, error_msg = youdaonote_pull._covert_config(self.TEST_CONFIG_PATH)
            self.assertFalse(config_dict)
            self.assertEqual(error_msg, '请检查「config.json」格式是否为 utf-8 格式的 json！建议使用 Sublime 编辑「config.json」')

        # 当 key 被修改时。期待：转换失败
        config_json_str = """{
                        "local_dir": "",
                        "ydnote_dir": "",
                        "smms_secret_token2": ""
                    }
                    """
        with patch('builtins.open', mock_open(read_data=config_json_str.encode('utf-8'))):
            config_dict, error_msg = youdaonote_pull._covert_config(self.TEST_CONFIG_PATH)
            self.assertFalse(config_dict)
            self.assertEqual(error_msg, '请检查「config.json」的 key 是否分别为 local_dir, ydnote_dir, smms_secret_token')

        # 当格式正确时。期待：转换成功
        config_json_str = """{
                                "local_dir": "",
                                "ydnote_dir": "",
                                "smms_secret_token": ""
                            }
                            """
        with patch('builtins.open', mock_open(read_data=config_json_str.encode('utf-8'))):
            config_dict, error_msg = youdaonote_pull._covert_config(self.TEST_CONFIG_PATH)
            self.assertTrue(config_dict)
            self.assertEqual(len(config_dict), 3)

    def test_check_local_dir(self):
        """
        测试检查本地目录
        python test.py YoudaoNotePullTest.test_check_local_dir
        """
        youdaonote_pull = YoudaoNotePull()
        test_default_dir = 'test_youdaonote'
        local_dir_expect = os.path.join(os.getcwd(), test_default_dir).replace('\\', '/')

        # 当不指定文件夹时。期待：当前目录新增 youdaonote 目录
        local_dir, error_msg = youdaonote_pull._check_local_dir(local_dir='', test_default_dir=test_default_dir)
        self.assertEqual(local_dir, local_dir_expect)
        self.assertTrue(os.path.exists(local_dir_expect))
        self.assertEqual(error_msg, '')

        # 当指定文件不存在时。期待：返回错误提示
        local_dir, error_msg = youdaonote_pull._check_local_dir(local_dir='test/test')
        self.assertEqual(local_dir, '')
        self.assertEqual(error_msg, '请检查「test/test」上层文件夹是否存在，并使用绝对路径！')

        # 当指定文件夹存在时。期待：正常
        local_dir, error_msg = youdaonote_pull._check_local_dir(local_dir=local_dir_expect)
        self.assertEqual(local_dir, local_dir_expect)
        self.assertEqual(error_msg, '')

        try:
            os.removedirs(local_dir_expect)
        except:
            pass

    def test_get_dir_id(self):
        """
        测试获取有道云笔记目录 ID
        python test.py YoudaoNotePullTest.test_get_dir_id
        """

        # 先 mock 登录一下
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch('pull.YoudaoNoteApi._covert_cookies',
                   return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]]):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        youdaonote_pull = YoudaoNotePull()
        youdaonote_pull.youdaonote_api = youdaonote_api
        return_value_json = {
            'fileEntry': {'id': 'test_root_id'},
            'entries': [
                {'fileEntry': {'id': 'test_dir_id', 'name': 'test_dir'}},
                {'fileEntry': {'id': 'test_dir_2_id', 'name': 'test_dir_2'}}
            ]
        }

        # 当不指定有道云笔记指定目录时。期待：返回根目录 ID
        youdaonote_api.http_post = Mock(return_value=MockResponse(return_value_json, 200))
        dir_id, error_msg = youdaonote_pull._get_ydnote_dir_id(ydnote_dir='')
        self.assertEqual(dir_id, 'test_root_id')

        # 指定目录、目录不存在时。期待：返回根目录 ID
        youdaonote_api.http_post = Mock(return_value=MockResponse(return_value_json, 200))
        youdaonote_api.http_get = Mock(return_value=MockResponse(return_value_json, 200))
        dir_id, error_msg = youdaonote_pull._get_ydnote_dir_id(ydnote_dir='test_dir_3')
        self.assertEqual(dir_id, '')
        self.assertEqual(error_msg, '有道云笔记指定顶层目录不存在')

        # 指定目录、目录存在时。期待：返回目录 ID
        youdaonote_api.http_post = Mock(return_value=MockResponse(return_value_json, 200))
        youdaonote_api.http_get = Mock(return_value=MockResponse(return_value_json, 200))
        dir_id, error_msg = youdaonote_pull._get_ydnote_dir_id(ydnote_dir='test_dir')
        self.assertEqual(dir_id, 'test_dir_id')


if __name__ == '__main__':
    unittest.main()
