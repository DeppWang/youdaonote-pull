import json
import logging
import os
import xml.etree.ElementTree as ET
from typing import Tuple

MARKDOWN_SUFFIX = ".md"


class XmlElementConvert(object):
    """
    XML Element 转换规则
    """

    @staticmethod
    def convert_para_func(**kwargs):
        """正常文本（粗体、斜体、删除线、链接）"""
        return kwargs.get("text")

    @staticmethod
    def convert_heading_func(**kwargs):
        """标题"""
        level = kwargs.get("element").attrib.get("level", 0)
        level = 1 if level in (["a", "b"]) else level
        text = kwargs.get("text")
        return " ".join(["#" * int(level), text]) if text else text

    @staticmethod
    def convert_image_func(**kwargs):
        """图片"""
        image_url = XmlElementConvert.get_text_by_key(
            list(kwargs.get("element")), "source"
        )
        return "![{text}]({image_url})".format(
            text=kwargs.get("text"), image_url=image_url
        )

    @staticmethod
    def convert_attach_func(**kwargs):
        """附件"""
        element = kwargs.get("element")
        filename = XmlElementConvert.get_text_by_key(list(element), "filename")
        resource_url = XmlElementConvert.get_text_by_key(list(element), "resource")
        return "[{text}]({resource_url})".format(
            text=filename, resource_url=resource_url
        )

    @staticmethod
    def convert_code_func(**kwargs):
        """代码块"""
        language = XmlElementConvert.get_text_by_key(
            list(kwargs.get("element")), "language"
        )
        return "```{language}\r\n{code}```".format(
            language=language, code=kwargs.get("text")
        )

    @staticmethod
    def convert_todo_func(**kwargs):
        """to-do"""
        return "- [ ] {text}".format(text=kwargs.get("text"))

    @staticmethod
    def convert_quote_func(**kwargs):
        """引用"""
        return "> {text}".format(text=kwargs.get("text"))

    @staticmethod
    def convert_horizontal_line_func(**kwargs):
        """分割线"""
        return "---"

    @staticmethod
    def convert_list_item_func(**kwargs):
        """列表"""
        list_id = kwargs.get("element").attrib["list-id"]
        is_ordered = kwargs.get("list_item").get(list_id)
        text = kwargs.get("text")
        if is_ordered == "unordered":
            return "- {text}".format(text=text)
        elif is_ordered == "ordered":
            return "1. {text}".format(text=text)

    @staticmethod
    def convert_table_func(**kwargs):
        """
        表格转换
        :param kwargs:
        :return:
        """
        element = kwargs.get("element")
        content = XmlElementConvert.get_text_by_key(element, "content")

        table_data_str = f""  # f-string 多行字符串
        nl = "\r\n"  # 考虑 Windows 系统，换行符设为 \r\n
        table_data = json.loads(content)
        table_data_len = len(table_data["widths"])
        table_data_arr = []
        table_data_line = []

        for cells in table_data["cells"]:
            values = cells.get("value")
            if values is None:
                values = ""
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
                table_data_str += f" %s |" % table_data
            table_data_str += f"{nl}"

        return table_data_str

    @staticmethod
    def get_text_by_key(element_children, key="text"):
        """
        获取文本内容
        :return:
        """
        for sub_element in element_children:
            if key in sub_element.tag:
                return sub_element.text if sub_element.text else ""
        return ""

    @staticmethod
    def _encode_string_to_md(original_text):
        """将字符串转义防止 markdown 识别错误"""
        if len(original_text) <= 0 or original_text == " ":
            return original_text

        original_text = original_text.replace("\\", "\\\\")  # \\ 反斜杠
        original_text = original_text.replace("*", "\\*")  # \* 星号
        original_text = original_text.replace("_", "\\_")  # \_ 下划线
        original_text = original_text.replace("#", "\\#")  # \# 井号

        # markdown 中需要转义的字符
        original_text = original_text.replace("&", "&amp;")
        original_text = original_text.replace("<", "&lt;")
        original_text = original_text.replace(">", "&gt;")
        original_text = original_text.replace("“", "&quot;")
        original_text = original_text.replace("‘", "&apos;")

        original_text = original_text.replace("\t", "&emsp;")

        # 换行 <br>
        original_text = original_text.replace("\r\n", "<br>")
        original_text = original_text.replace("\n\r", "<br>")
        original_text = original_text.replace("\r", "<br>")
        original_text = original_text.replace("\n", "<br>")

        return original_text


class JsonConvert(object):
    """
    json 转换规则
    """

    def _get_common_text(self, content: dict) -> Tuple[list, str]:
        """获取通常文本
        :return
            text(text): 文本内容
        """
        all_text = ""
        # 5 内容
        five_contents = content.get("5")
        # 判断是否是普通文本
        if five_contents:
            seven_contents = five_contents[0].get("7")
            if not seven_contents:
                return all_text
            for seven_content in seven_contents:
                # 8 文本
                text = seven_content.get("8")
                # 9 文本属性
                text_attrs = seven_content.get("9")
                if text and text_attrs:
                    text = self._convert_text_attribute(text, text_attrs)
                all_text += text
        return all_text

    def _convert_text_attribute(self, text: str, text_attrs: list):
        """文本属性"""

        if isinstance(text_attrs, list) and text_attrs and text:
            for attr in text_attrs:
                if attr["2"] == "b":
                    # 粗体
                    text = f"**{text}**"
                elif attr["2"] == "i":
                    # 斜体
                    text = f"*{text}*"

        return text

    def convert_text_func(self, content) -> str:
        """正常文本、粗体、斜体、删除线、链接"""
        all_text = ""
        one_five_contents = content.get("5")
        if one_five_contents:
            for one_five_content in one_five_contents:
                # 包含 6 和 7
                two_five_contents = one_five_content.get("5")
                # 文本类型
                text_type = one_five_content.get("6")
                # 文本和属性
                seven_contents = one_five_content.get("7")

                # 获取文本和属性
                if seven_contents and not two_five_contents:
                    text = ""
                    for seven_content in seven_contents:
                        # 8 文本
                        raw = seven_content.get("8")
                        # 9 文本属性
                        text_attrs = seven_content.get("9")
                        if raw and text_attrs:
                            raw = self._convert_text_attribute(raw, text_attrs)
                        text += raw

                # 链接类型
                elif text_type == "li" and two_five_contents:
                    source_text = self._get_common_text(one_five_content)
                    # 附加信息
                    four_contents = one_five_content.get("4")
                    if four_contents:
                        hf = four_contents.get("hf")
                        text = f"[{source_text}]({hf})"
                    else:
                        text = ""
                else:
                    text = ""
                if text:
                    all_text += text
        return all_text

    def convert_h_func(self, content) -> str:
        """标题"""
        type_name = content.get("4").get("l")
        text = self._get_common_text(content=content)
        if text and type_name:
            level_str = type_name.replace("h", "")
            level = int(level_str)
            text = " ".join(["#" * int(level), text])
        return text

    def convert_im_func(self, content):
        """图片"""
        image_url = content["4"]["u"]
        return "![]({image_url})".format(image_url=image_url)

    def convert_a_func(self, content):
        """附件"""
        fn = content["4"]["fn"]
        fl = content["4"]["re"]
        return "[{text}]({resource_url})".format(text=fn, resource_url=fl)

    def convert_cd_func(self, content):
        """代码块"""
        language = content.get("4").get("la")
        codes: list = content.get("5")
        code_block = ""
        for code in codes:
            text = self._get_common_text(code)
            code_block += text + "\n"

        return "```{language}\r\n{code_block}```".format(
            language=language, code_block=code_block
        )

    def convert_la_func(self, content):
        """高亮块"""
        lines: list = content.get("5")
        highlight_block = ""
        for line in lines:
            text = self._get_common_text(line)
            highlight_block += text + "\n"

        return "```\r\n{highlight_block}```".format(highlight_block=highlight_block)

    def convert_q_func(self, content):
        """引用"""
        q_text_list = content["5"]
        text = ""
        for q_text_dict in q_text_list:
            q_text = self._get_common_text(q_text_dict)
            # 去除第一行的换行
            q_text = q_text.replace("\n", "")
            text += "> {q_text}\n".format(q_text=q_text)
        return text

    def convert_l_func(self, content):
        """有序列表和无序列表，有序列表转成无序列表"""
        text = self._get_common_text(content=content)
        is_ordered = content.get("4").get("lt")
        if is_ordered == "unordered":
            level = content.get("4").get("ll")
            return "\t" * (level - 1) + "- {text}".format(text=text)
        elif is_ordered == "ordered":
            # 有序列表都设置为 1，有些 MD 编辑自动转为有序列表
            return "1. {text}".format(text=text)

    def convert_t_func(self, content):
        """
        表格转换
        """
        nl = "\r\n"  # 考虑 Windows 系统，换行符设为 \r\n
        tr_list = content["5"]
        table_lines = ""

        for index, tc in enumerate(tr_list):
            table_content_list = tc["5"]
            table_content_len = len(table_content_list)
            if index == 1:
                table_line = "| -- " * table_content_len + "|\n| "
            else:
                table_line = "| "
            for table_content in table_content_list:
                table_text_list = table_content.get("5")[0].get("5")[0].get("7")
                if table_text_list:
                    table_text = table_text_list[0]["8"]
                else:
                    table_text = " "
                table_line = table_line + table_text + " | "
            table_lines = table_lines + table_line + f"{nl}"
        return table_lines


class YoudaoNoteConvert(object):
    """
    有道云笔记 note 内容转换为 markdown 内容
    """

    @staticmethod
    def covert_html_to_markdown(file_path):
        """
        转换 HTML 为 MarkDown
        :param file_path:
        :return:
        """
        with open(file_path, "rb") as f:
            content_str = f.read().decode("utf-8")
        from markdownify import markdownify as md

        # 如果换行符丢失，使用 md(content_str.replace('<br>', '<br><br>').replace('</div>', '</div><br><br>')).rstrip()
        new_content = md(content_str)
        base = os.path.splitext(file_path)[0]
        new_file_path = "".join([base, MARKDOWN_SUFFIX])
        os.rename(file_path, new_file_path)
        with open(new_file_path, "wb") as f:
            f.write(new_content.encode())

    @staticmethod
    def _covert_xml_to_markdown_content(file_path):
        # 使用 xml.etree.ElementTree 将 xml 文件转换为对象
        element_tree = ET.parse(file_path)
        note_element = element_tree.getroot()  # note Element

        # list_item 的 id 与 type 的对应
        list_item = {}
        for child in note_element[0]:
            if "list" in child.tag:
                list_item[child.attrib["id"]] = child.attrib["type"]

        body_element = note_element[1]  # Element
        new_content_list = []
        for element in list(body_element):
            text = XmlElementConvert.get_text_by_key(list(element))
            name = element.tag.replace("{http://note.youdao.com}", "").replace("-", "_")
            convert_func = getattr(
                XmlElementConvert, "convert_{}_func".format(name), None
            )
            # 如果没有转换，只保留文字
            if not convert_func:
                new_content_list.append(text)
                continue
            line_content = convert_func(text=text, element=element, list_item=list_item)
            new_content_list.append(line_content)
        return f"\r\n\r\n".join(new_content_list)  # 换行 1 行

    @staticmethod
    def covert_xml_to_markdown(file_path) -> bool:
        """
        转换 XML 为 MarkDown
        :param file_path:
        :return:
        """
        base = os.path.splitext(file_path)[0]
        new_file_path = "".join([base, MARKDOWN_SUFFIX])
        # 如果文件为空，结束
        if os.path.getsize(file_path) == 0:
            os.rename(file_path, new_file_path)
            return False

        new_content = YoudaoNoteConvert._covert_xml_to_markdown_content(file_path)
        os.rename(file_path, new_file_path)
        with open(new_file_path, "wb") as f:
            f.write(new_content.encode("utf-8"))
        return True

    @staticmethod
    def _covert_json_to_markdown_content(file_path):
        new_content_list = []
        # 加载 json 文件
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                json_data = json.load(f)
            except Exception as e:
                logging.error(e)
                json_data = {}

        json_contents = json_data["5"]  # 3 代表 id，4 代表信息，5 代表内容，6 代表类型
        for content in json_contents:
            type = content.get("6")
            # 根据类型处理，无类型的为普通文本
            if type:
                convert_func = getattr(
                    JsonConvert(), "convert_{}_func".format(type), None
                )
                # 如果类型没有对应转换函数，只保留文字
                if not convert_func:
                    line_content = JsonConvert().convert_text_func(content)
                else:
                    line_content = convert_func(content)
            else:
                line_content = JsonConvert().convert_text_func(content)

            # 判断是否有内容
            if line_content:
                new_content_list.append(line_content)
        return f"\r\n\r\n".join(new_content_list)  # 换行 1 行

    @staticmethod
    def covert_json_to_markdown(file_path) -> str:
        """
        转换 Json 为 MarkDown
        :param file_path:
        :return:
        """
        base = os.path.splitext(file_path)[0]
        new_file_path = "".join([base, MARKDOWN_SUFFIX])
        # 如果文件为空，结束
        if os.path.getsize(file_path) == 0:
            os.rename(file_path, new_file_path)
            return False
        new_content = YoudaoNoteConvert._covert_json_to_markdown_content(file_path)
        with open(new_file_path, "wb") as f:
            f.write(new_content.encode("utf-8"))
        # 删除旧文件
        if os.path.exists(file_path):
            os.remove(file_path)
        return new_file_path
