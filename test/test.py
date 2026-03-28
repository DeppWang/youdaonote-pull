# -*- coding:utf-8 -*-

from __future__ import absolute_import

import os
import sys
import unittest
from unittest.mock import Mock, mock_open, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.api import YoudaoNoteApi
from core.config import AppConfig, import_config_from_picgo
from core.covert import YoudaoNoteConvert
from core.image import ImageUpload
from pull import YoudaoNotePull

TEST_COOKIES_PATH = "test_cookies.json"
TEST_CONFIG_PATH = "test_config.json"


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class YoudaoNoteApiTest(unittest.TestCase):
    def test_cookies_login(self):
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        message = youdaonote_api.login_by_cookies()
        self.assertTrue("No such file or directory" in message)

        cookies_json_str = """{
            "cookies":
                ["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"],
                ["YNOTE_LOGIN", "3||1591964671668", ".note.youdao.com", "/"],
                ["YNOTE_SESS", "***", ".note.youdao.com", "/"]
        }"""
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch("builtins.open", mock_open(read_data=cookies_json_str.encode("utf-8"))):
            message = youdaonote_api.login_by_cookies()
            self.assertEqual(message, "转换「{}」为字典时出现错误".format(TEST_COOKIES_PATH))

        cookies_json_str = """{
            "cookies": [
                ["YNOTE_LOGIN", "3||1591964671668", ".note.youdao.com", "/"],
                ["YNOTE_SESS", "***", ".note.youdao.com", "/"]
            ]
        }"""
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch("builtins.open", mock_open(read_data=cookies_json_str.encode("utf-8"))):
            message = youdaonote_api.login_by_cookies()
            self.assertEqual(message, "YNOTE_CSTK 字段为空")

        cookies_json_str = """{
            "cookies": [
                ["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"],
                ["YNOTE_LOGIN", "3||1591964671668", ".note.youdao.com", "/"],
                ["YNOTE_SESS", "***", ".note.youdao.com", "/"]
            ]
        }"""
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch("builtins.open", mock_open(read_data=cookies_json_str.encode("utf-8"))):
            message = youdaonote_api.login_by_cookies()
            self.assertFalse(message)
            self.assertEqual(youdaonote_api.cstk, "fPk5IkDg")

    def test_get_root_dir_info_id(self):
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch(
            "pull.YoudaoNoteApi._covert_cookies",
            return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]],
        ):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        youdaonote_api.http_post = Mock(
            return_value=MockResponse(
                {"fileEntry": {"id": "test_root_id", "name": "ROOT"}}, 200
            )
        )
        root_dir_info = youdaonote_api.get_root_dir_info_id()
        self.assertEqual(root_dir_info["fileEntry"]["id"], "test_root_id")

    def test_get_dir_info_by_id(self):
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch(
            "pull.YoudaoNoteApi._covert_cookies",
            return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]],
        ):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        youdaonote_api.http_get = Mock(
            return_value=MockResponse(
                {
                    "count": 2,
                    "entries": [
                        {
                            "fileEntry": {
                                "id": "test_dir_id",
                                "name": "test_dir",
                                "dir": True,
                            }
                        },
                        {
                            "fileEntry": {
                                "id": "test_note_id",
                                "name": "test_note",
                                "dir": False,
                            }
                        },
                    ],
                },
                200,
            )
        )
        dir_info = youdaonote_api.get_dir_info_by_id(dir_id="test_dir_id")
        self.assertEqual(dir_info["count"], 2)
        self.assertTrue(dir_info["entries"][0]["fileEntry"]["dir"])
        self.assertFalse(dir_info["entries"][1]["fileEntry"]["dir"])

    def test_get_file_by_id(self):
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch(
            "pull.YoudaoNoteApi._covert_cookies",
            return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]],
        ):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        youdaonote_api.http_post = Mock(return_value=MockResponse({}, 200))
        file = youdaonote_api.get_file_by_id(file_id="test_note_id")
        self.assertTrue(file)


class YoudaoNoteConvertTest(unittest.TestCase):
    def test_covert_xml_to_markdown_content(self):
        content = YoudaoNoteConvert._covert_xml_to_markdown_content("test/test.note")
        with open("test/test.md", "rb") as f:
            content_target = f.read().decode()
        self.assertEqual(
            content.replace("\r\n", "\n"),
            content_target.replace("\r\n", "\n"),
        )

    def test_html_to_markdown(self):
        from markdownify import markdownify as md

        new_content = md(
            """<div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: \"Monaco\",\"Consolas\",\"Lucida Console\",\"Courier New\",\"serif\"; font-size: 12px; background-color: rgb(247, 247, 247);'><a href=\"http://bbs.pcbeta.com/viewthread-1095891-1-1.html\">http://bbs.pcbeta.com/viewthread-1095891-1-1.html</a></span></div>"""
        )
        expected_content = """<http://bbs.pcbeta.com/viewthread-1095891-1-1.html>"""
        self.assertEqual(new_content, expected_content)

    def test_covert_json_to_markdown_content(self):
        content = YoudaoNoteConvert._covert_json_to_markdown_content("test/test.json")
        with open("test/test-json.md", "rb") as f:
            content_target = f.read().decode()
        self.assertEqual(
            content.replace("\r\n", "\n"),
            content_target.replace("\r\n", "\n"),
        )

    def test_covert_json_to_markdown_single_line(self):
        line = YoudaoNoteConvert._covert_json_to_markdown_content("test/test-convert.json")
        with open("test/test-convert.md", "rb") as f:
            target = f.read().decode()
        self.assertEqual(line.replace("\r\n", "\n"), target)


class YoudaoNotePullTest(unittest.TestCase):
    def test_covert_config_json(self):
        youdaonote_pull = YoudaoNotePull()

        config_json_str = """
            "local_dir": "",
            "ydnote_dir": "",
            "smms_secret_token": "",
            "is_relative_path": true
        }
        """
        with patch("builtins.open", mock_open(read_data=config_json_str.encode("utf-8"))):
            config_dict, error_msg = youdaonote_pull._covert_config(TEST_CONFIG_PATH)
            self.assertFalse(config_dict["local_dir"])
            self.assertEqual(
                error_msg,
                "请检查「config.json」格式是否为 utf-8 格式的 json！建议使用 Sublime 编辑「config.json」",
            )

        config_json_str = """{
            "local_dir": "",
            "ydnote_dir": "",
            "smms_secret_token2": "",
            "is_relative_path": true
        }
        """
        with patch("builtins.open", mock_open(read_data=config_json_str.encode("utf-8"))):
            config_dict, error_msg = youdaonote_pull._covert_config(TEST_CONFIG_PATH)
            self.assertEqual(config_dict["image_uploader"], "local")
            self.assertEqual(
                error_msg,
                "请检查「config.json」的 key 是否至少包含 local_dir, ydnote_dir, smms_secret_token, is_relative_path",
            )

        config_json_str = """{
            "local_dir": "",
            "ydnote_dir": "",
            "smms_secret_token": "token",
            "is_relative_path": true
        }
        """
        with patch("builtins.open", mock_open(read_data=config_json_str.encode("utf-8"))):
            config_dict, error_msg = youdaonote_pull._covert_config(TEST_CONFIG_PATH)
            self.assertFalse(error_msg)
            self.assertEqual(config_dict["image_uploader"], "smms")
            self.assertIn("aliyun_oss", config_dict)

        config_json_str = """{
            "local_dir": "",
            "ydnote_dir": "",
            "smms_secret_token": "",
            "is_relative_path": true,
            "image_uploader": "aliyun_oss",
            "aliyun_oss": {
                "endpoint": "https://oss-cn-shanghai.aliyuncs.com",
                "bucket": "test-bucket",
                "access_key_id": "ak",
                "access_key_secret": "sk",
                "path": "notes",
                "custom_domain": "",
                "use_https": true
            }
        }
        """
        with patch("builtins.open", mock_open(read_data=config_json_str.encode("utf-8"))):
            config_dict, error_msg = youdaonote_pull._covert_config(TEST_CONFIG_PATH)
            self.assertFalse(error_msg)
            self.assertEqual(config_dict["image_uploader"], "aliyun_oss")
            self.assertEqual(config_dict["aliyun_oss"]["bucket"], "test-bucket")

    def test_check_local_dir(self):
        youdaonote_pull = YoudaoNotePull()
        test_default_dir = "test/test_youdaonote"

        local_dir, error_msg = youdaonote_pull._check_local_dir(
            local_dir="", test_default_dir=test_default_dir
        )
        self.assertEqual(local_dir, "./test/test_youdaonote")
        self.assertTrue(os.path.exists(test_default_dir))
        self.assertEqual(error_msg, "")

        local_dir, error_msg = youdaonote_pull._check_local_dir(local_dir="test/test")
        self.assertEqual(local_dir, "test/test")
        self.assertEqual(error_msg, "")

        local_dir, error_msg = youdaonote_pull._check_local_dir(local_dir=test_default_dir)
        self.assertEqual(local_dir, test_default_dir)
        self.assertEqual(error_msg, "")

        try:
            os.removedirs(test_default_dir)
        except Exception:
            pass

    def test_get_dir_id(self):
        youdaonote_api = YoudaoNoteApi(cookies_path=TEST_COOKIES_PATH)
        with patch(
            "pull.YoudaoNoteApi._covert_cookies",
            return_value=[["YNOTE_CSTK", "fPk5IkDg", ".note.youdao.com", "/"]],
        ):
            error_msg = youdaonote_api.login_by_cookies()
            self.assertFalse(error_msg)

        youdaonote_pull = YoudaoNotePull()
        youdaonote_pull.youdaonote_api = youdaonote_api
        return_value_json = {
            "fileEntry": {"id": "test_root_id"},
            "entries": [
                {"fileEntry": {"id": "test_dir_id", "name": "test_dir"}},
                {"fileEntry": {"id": "test_dir_2_id", "name": "test_dir_2"}},
            ],
        }

        youdaonote_api.http_post = Mock(return_value=MockResponse(return_value_json, 200))
        dir_id, error_msg = youdaonote_pull._get_ydnote_dir_id(ydnote_dir="")
        self.assertEqual(dir_id, "test_root_id")

        youdaonote_api.http_post = Mock(return_value=MockResponse(return_value_json, 200))
        youdaonote_api.http_get = Mock(return_value=MockResponse(return_value_json, 200))
        dir_id, error_msg = youdaonote_pull._get_ydnote_dir_id(ydnote_dir="test_dir_3")
        self.assertEqual(dir_id, "")
        self.assertEqual(error_msg, "有道云笔记指定顶层目录不存在")

        youdaonote_api.http_post = Mock(return_value=MockResponse(return_value_json, 200))
        youdaonote_api.http_get = Mock(return_value=MockResponse(return_value_json, 200))
        dir_id, error_msg = youdaonote_pull._get_ydnote_dir_id(ydnote_dir="test_dir")
        self.assertEqual(dir_id, "test_dir_id")


class ConfigImportTest(unittest.TestCase):
    def test_import_config_from_picgo_prefers_current_uploader(self):
        picgo_json_str = """{
            "picBed": {
                "current": "aliyun",
                "aliyun": {
                    "accessKeyId": "ak",
                    "accessKeySecret": "sk",
                    "bucket": "bucket-demo",
                    "area": "oss-cn-shanghai",
                    "path": "notes",
                    "customUrl": "cdn.example.com"
                },
                "smms": {
                    "token": "smms-token"
                }
            }
        }"""
        with patch("builtins.open", mock_open(read_data=picgo_json_str)):
            imported, error_msg = import_config_from_picgo(
                "C:/Users/test/AppData/Roaming/picgo/data.json"
            )
        self.assertFalse(error_msg)
        self.assertEqual(imported["image_uploader"], "aliyun_oss")
        self.assertEqual(imported["aliyun_oss"]["bucket"], "bucket-demo")
        self.assertEqual(
            imported["aliyun_oss"]["endpoint"],
            "https://oss-cn-shanghai.aliyuncs.com",
        )

    def test_build_oss_url_with_custom_domain(self):
        config = AppConfig.from_dict(
            {
                "local_dir": "",
                "ydnote_dir": "",
                "smms_secret_token": "",
                "is_relative_path": True,
                "image_uploader": "aliyun_oss",
                "aliyun_oss": {
                    "endpoint": "https://oss-cn-shanghai.aliyuncs.com",
                    "bucket": "bucket-demo",
                    "access_key_id": "ak",
                    "access_key_secret": "sk",
                    "path": "notes",
                    "custom_domain": "cdn.example.com",
                    "use_https": True,
                },
            }
        )
        url = ImageUpload._build_oss_file_url(config.aliyun_oss, "notes/demo.png")
        self.assertEqual(url, "https://cdn.example.com/notes/demo.png")


if __name__ == "__main__":
    unittest.main()
