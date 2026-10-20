# -*- coding: utf-8 -*-
"""
验证本次修复的回归测试

覆盖 issue #155 (UnicodeEncodeError: 'gbk' codec can't encode character '\xa0')
及本次 PR 修复的其他崩溃点。

运行：python test/test_regression.py
"""
import io
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.covert import JsonConvert, YoudaoNoteConvert
from pull import YoudaoNotePull


class FilenameSanitizeTest(unittest.TestCase):
    """文件名清洗：Windows 非法字符 / 保留设备名"""

    def setUp(self):
        self.pull = YoudaoNotePull.__new__(YoudaoNotePull)

    def test_control_chars_removed(self):
        """控制字符（\\r \\t）必须被清除，否则 Windows 写入时报 Permission denied"""
        self.assertEqual(self.pull._optimize_file_name("abc\r\ndef"), "abcdef")

    def test_reserved_device_names(self):
        """CON / PRN / AUX / NUL / COM1 等 Windows 保留设备名不能作为文件名"""
        for name in ["CON", "con.txt", "PRN", "AUX", "NUL", "COM1", "LPT1"]:
            cleaned = self.pull._optimize_file_name(name)
            self.assertNotEqual(
                cleaned.upper().split(".")[0],
                name.upper().split(".")[0],
                "保留设备名未被处理：%s -> %s" % (name, cleaned),
            )

    def test_empty_name_fallback(self):
        """清洗后为空的名字必须有兜底"""
        self.assertTrue(self.pull._optimize_file_name("///"))

    def test_illegal_symbols_removed(self):
        """原有的非法符号清洗行为不能被破坏"""
        self.assertNotIn(":", self.pull._optimize_file_name("a:b"))
        self.assertNotIn("*", self.pull._optimize_file_name("a*b"))


class LogEncodingTest(unittest.TestCase):
    """日志编码：GBK 控制台下的 \\xa0 / emoji 不能抛 UnicodeEncodeError"""

    def test_safe_stdout_forces_utf8(self):
        from core.log import _safe_stdout

        fake = Mock()
        fake.buffer = io.BytesIO()
        # 直接验证返回值可用 UTF-8 写出 \xa0 和 emoji
        real = sys.stdout
        try:
            sys.stdout = fake
            wrapped = _safe_stdout()
            wrapped.write("nbsp:\xa0 emoji:\U0001f3b1")
            wrapped.flush()
        finally:
            sys.stdout = real
        data = fake.buffer.getvalue()
        self.assertIn("nbsp:".encode("utf-8"), data)
        self.assertIn("\U0001f3b1".encode("utf-8"), data)

    def test_file_handler_uses_replace(self):
        """FileHandler 必须带 errors='replace'，否则写日志时同样会抛异常"""
        import inspect

        from core import log

        src = inspect.getsource(log.init_logging)
        self.assertIn('errors="replace"', src)


class ConvertRobustnessTest(unittest.TestCase):
    """格式转换健壮性"""

    def test_subtitle_heading_does_not_raise(self):
        """标题 l 字段为 'subtitle' 时不能抛 ValueError"""
        content = {"4": {"l": "subtitle"}, "5": [{"2": "1"}]}
        # 不应抛异常
        result = JsonConvert().convert_h_func(content)
        self.assertIsInstance(result, str)

    def test_json_missing_content_key(self):
        """json 根节点缺少 '5' 字段时不能抛 KeyError"""
        import json
        import tempfile

        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"2": "1", "3": "x", "4": {}}, f)
            path = f.name
        try:
            result = YoudaoNoteConvert._covert_json_to_markdown_content(path)
            self.assertEqual(result, "")
        finally:
            os.unlink(path)

    def test_json_bad_block_is_skipped(self):
        """单个内容块结构异常时跳过该块，不中断整篇"""
        import json
        import tempfile

        payload = {
            "5": [
                {"6": "t", "4": {}},  # 正常文本块
                {"6": "im"},  # 缺字段的图片块 -> 会抛异常
                {"6": "t", "4": {}},
            ]
        }
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(payload, f)
            path = f.name
        try:
            result = YoudaoNoteConvert._covert_json_to_markdown_content(path)
            self.assertIsInstance(result, str)
        finally:
            os.unlink(path)


class RecursionRobustnessTest(unittest.TestCase):
    """递归遍历健壮性"""

    def test_bad_dir_name_does_not_abort(self):
        """目录名非法导致创建失败时，应跳过该目录而不是中断整轮"""
        pull = YoudaoNotePull.__new__(YoudaoNotePull)
        pull.youdaonote_api = Mock()
        pull.youdaonote_api.get_dir_info_by_id.return_value = {
            "entries": [
                {"fileEntry": {"id": "1", "name": "bad\x00name", "dir": True}},
                {
                    "fileEntry": {
                        "id": "2",
                        "name": "ok.md",
                        "dir": False,
                        "modifyTimeForSort": 1,
                        "createTimeForSort": 1,
                    }
                },
            ]
        }
        pull._add_or_update_file = Mock()

        with patch("os.makedirs", side_effect=OSError("invalid name")):
            with tempfile_dir() as tmp:
                pull.pull_dir_by_id_recursively("root", tmp)

        # 坏目录被跳过，后续条目仍被处理
        self.assertTrue(pull._add_or_update_file.called)


class tempfile_dir:
    """简易临时目录上下文管理器（避免依赖 tempfile.TemporaryDirectory 的清理时机）"""

    def __enter__(self):
        import tempfile

        self._tmp = tempfile.mkdtemp()
        return self._tmp

    def __exit__(self, *args):
        import shutil

        shutil.rmtree(self._tmp, ignore_errors=True)
        return False


if __name__ == "__main__":
    unittest.main(verbosity=2)
