#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import json
import os
import xml.etree.ElementTree as ET

json_str = '''

{
	"cells": [{
		"verticalAlign": "middle",
		"wrap": true,
		"value": "序号",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 2,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "方法名",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 3,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "类型",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 2,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "作用",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 2,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "01"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "__new__"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "方法"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "创建对象时，会被 自动 调用",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 4,
				"value": true
			}, {
				"from": 9,
				"to": 11,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "02"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "__init__"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "方法"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "对象被初始化时，会被 自动 调用",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 6,
				"value": true
			}, {
				"from": 11,
				"to": 13,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "03"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "__del__"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "方法"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"value": "对象被从内存中销毁前，会被 自动 调用",
		"inlineStyles": {
			"bold": [{
				"from": 0,
				"to": 9,
				"value": true
			}, {
				"from": 14,
				"to": 16,
				"value": true
			}]
		}
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "04"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "__str__"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "方法"
	}, {
		"verticalAlign": "middle",
		"wrap": true,
		"backColor": "rgb(248, 248, 248)",
		"value": "返回对象的描述信息，print 函数输出使用",
		"inlineStyles": {
			"bold": [{
				"from": 2,
				"to": 9,
				"value": true
			}]
		}
	}],
	"heights": [40, 40, 40, 40, 40],
	"widths": [70, 86, 68, 443]
}
'''


def test_covert_xml_to_markdown(file_path) -> None:
    """ 测试 """
    # 如果文件为 null，结束
    if os.path.getsize(file_path) == 0:
        base = os.path.splitext(file_path)[0]
        os.rename(file_path, base + '.md')
        return

    flag = 0  # 用于输出转换提示
    nl = '\r\n'  # 考虑 Windows 系统，换行符设为 \r\n
    new_content = f''  # f-string 多行字符串

    tree = ET.parse(file_path)
    root = tree.getroot()

    for child in root[1]:
        this_text = f''  # f-string 多行字符串
        # 正常文本
        if 'list-item' in child.tag:
            this_text = covert_xml_node_to_has_styles_markdown(child)
            # print(this_text)
        elif 'para' in child.tag:
            this_text = covert_xml_node_to_has_styles_markdown(child)
            # print(this_text)

        # 其他
        else:
            this_text = covert_xml_node_to_has_styles_markdown(child)

        new_content += f'%s{nl}{nl}' % this_text

    base = os.path.splitext(file_path)[0]
    new_file_path = base + '.md'
    # os.rename(file_path, new_file_path)
    with open(new_file_path, 'wb') as f:
        f.write(new_content.encode())


def encode_string_to_md(original_text):
    """ 将字符串转义 防止markdown 识别错误 """

    if len(original_text) <= 0 or original_text == " ":
        return original_text

    # 转义
    # \\ 反斜杠
    # \` 反引号
    # \* 星号
    # \_ 下划线
    # \{\} 大括号
    # \[\] 中括号
    # \(\) 小括号
    # \# 井号
    # \+ 加号
    # \- 减号
    # \. 英文句号
    # \! 感叹号
    # 换行 <br> 感叹号

    if original_text.find('javacode2018') >= 0:
        print(original_text)
    original_text = original_text.replace('\\', '\\\\')
    original_text = original_text.replace('*', '\\*')
    original_text = original_text.replace('_', '\\_')
    original_text = original_text.replace('#', '\\#')

    # markdown中需要转义的字符
    original_text = original_text.replace('&', '&amp;')
    original_text = original_text.replace('<', '&lt;')
    original_text = original_text.replace('>', '&gt;')
    original_text = original_text.replace('“', '&quot;')
    original_text = original_text.replace('‘', '&apos;')

    original_text = original_text.replace('\t', '&emsp;')
    original_text = original_text.replace('\r\n', '<br>')
    original_text = original_text.replace('\n\r', '<br>')
    original_text = original_text.replace('\r', '<br>')
    original_text = original_text.replace('\n', '<br>')

    return original_text


def covert_xml_node_to_has_styles_markdown(child_element) -> str:
    """ 转换 xml节点 为 样式的 Markdown """
    # 文本
    this_text = f''  # f-string 多行字符串
    # 文本加工后的文本
    this_text_styles = f''  # f-string 多行字符串
    # 行内样式 加粗
    bold_arr = []
    # 行内样式 颜色
    color_arr = []
    # 文本缩进
    indent = 0
    # 将this_text 转换字典
    this_text_dict = collections.OrderedDict()
    dict_interval = int(10)

    for child2 in child_element:
        # 文本
        if 'text' in child2.tag:
            # 将 None 转为 "
            if child2.text is None:
                child2.text = ''
            this_text = child2.text

        # 行内样式
        elif 'inline-styles' in child2.tag:
            for child3 in child2:
                # 背景颜色
                if 'back-color' in child3.tag:
                    pass

                # 颜色
                elif 'color' in child3.tag:
                    color_from = None
                    color_to = None
                    color_value = None
                    for child4 in child3:
                        if 'from' in child4.tag:
                            color_from = child4.text
                        if 'to' in child4.tag:
                            color_to = child4.text
                        if 'value' in child4.tag:
                            color_value = child4.text
                    if color_from is not None:
                        color_arr.append([int(color_from), int(color_to), color_value])

                # 加粗
                elif 'bold' in child3.tag:
                    bold_from = None
                    bold_to = None
                    for child4 in child3:
                        if 'from' in child4.tag:
                            bold_from = child4.text
                        if 'to' in child4.tag:
                            bold_to = child4.text
                    if bold_from is not None:
                        bold_arr.append([int(bold_from), int(bold_to)])

        # 本行整体样式
        elif 'styles' in child2.tag:
            for child3 in child2:
                # 缩进
                if 'text-indent' in child3.tag:
                    indent = round(float(child3.text))
                    break
                elif 'indent' in child3.tag:
                    indent = round(float(child3.text))
                    break

    if len(bold_arr) <= 0 and len(color_arr) <= 0 and indent <= 0:
        # 转义
        return encode_string_to_md(this_text)

    if len(this_text) <= 0 or this_text.isspace():
        return this_text

    for index in range(len(this_text)):
        this_text_dict[int(index * dict_interval)] = this_text[index]
        # print(this_text[index])

    # 颜色
    if len(color_arr) > 0:
        for entry in color_arr:
            if len(this_text) < entry[0] - 1:
                break
            # 有道云空白字符也加样式 但是 markdown不能 ，所以需要将第一个字符不为空的的下标
            first_key = entry[0] * dict_interval
            while this_text_dict[first_key].isspace() and first_key < (entry[1] - 1) * dict_interval:
                first_key += dict_interval

            this_text_dict[first_key - 2] = '<span style=\'color:%s\'>' % entry[2]
            this_text_dict[int((entry[1] - 1) * dict_interval + 2)] = '</span>'
        # print(this_text_dict)

    # 加粗
    if len(bold_arr) > 0:
        for entry in bold_arr:
            # 有道云空白字符也加样式 但是 markdown不能 ，所以需要将第一个字符不为空的的下标
            first_key = entry[0] * dict_interval
            while this_text_dict[first_key].isspace() and first_key < (entry[1] - 1) * dict_interval:
                first_key += dict_interval

            this_text_dict[first_key - 1] = '**'
            this_text_dict[(entry[1] - 1) * dict_interval + 1] = '**'

    # 行内缩进 暂时不可用
    # this_text_styles = ("  " * indent) + this_text_styles
    this_text_styles = ("&emsp;" * indent) + this_text_styles

    # 将普通字典的keys提取出来 作为有序
    this_text_dict_keys = sorted(this_text_dict.keys())
    # 拼接 加样式后的 字符串
    for text_ordered_key in this_text_dict_keys:
        # 拼接转义
        if text_ordered_key % dict_interval == 0:
            this_text_styles += encode_string_to_md(this_text_dict[text_ordered_key])
        else:  # 自己加的符号不转义
            this_text_styles += this_text_dict[text_ordered_key]

    # print(this_text)
    # print(this_text_styles)
    # print(bold_arr)
    # print(color_arr)
    # print(this_text_dict)
    # print(indent)
    return this_text_styles


def covert_json_to_markdown_table(table_data_json_str):
    table_data_str = f''  # f-string 多行字符串
    nl = '\r\n'  # 考虑 Windows 系统，换行符设为 \r\n

    table_data = json.loads(table_data_json_str)
    table_data_len = len(table_data['widths'])
    table_data_arr = []
    table_data_arr_tmp = []

    for cells in table_data['cells']:
        cell_value = encode_string_to_md(cells['value'])
        table_data_arr_tmp.append(cell_value)
        # 攒齐一行放到table_data_arr中，并重置table_data_arr_tmp
        if len(table_data_arr_tmp) == table_data_len:
            table_data_arr.append(table_data_arr_tmp)
            table_data_arr_tmp = []

    # print(table_data_len)
    # print(type(table_data['cells']))
    # print(table_data_arr)

    # 规范数组
    # table_data_arr = [["dsdf","fdsf"],["aaa","bbb"]]
    # table_data_len = len(table_data_arr[0])
    # 规范表格 md最小2*2
    # 如果只有一行，那就给他加一个空白title行
    if len(table_data_arr) == 1:
        table_data_arr.insert(0, [ch for ch in (" " * table_data_len)])
        table_data_arr.insert(1, [ch for ch in ("-" * table_data_len)])
    elif len(table_data_arr) > 1:
        table_data_arr.insert(1, [ch for ch in ("-" * table_data_len)])

    for table_data in table_data_arr:
        table_data_str += "|"
        for table_data in table_data:
            table_data_str += f' %s |' % table_data
        table_data_str += f'{nl}'

    # print(table_data_arr)
    # print(len(table_data_arr))
    # print(table_data_str)
    return table_data_str


def main():
    # test_covert_xml_to_markdown('test/test.note')
    covert_json_to_markdown_table(json_str)


if __name__ == '__main__':
    main()
