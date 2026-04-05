#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
note2md.py — 有道云笔记 XML → 带样式 Markdown 转换器
支持：颜色、背景色、加粗、下划线、斜体、字号、缩进、有序/无序列表、图片
输出：内嵌 HTML span 标签的 Markdown（Obsidian/Typora 均可渲染）

用法：
  python3 note2md.py <input.note> [output.md]
  python3 note2md.py --dir <目录>   # 批量转换目录下所有 .note 文件
"""

import sys
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://note.youdao.com"


def tag(name):
    return f"{{{NS}}}{name}"


# ── 样式区间解析 ───────────────────────────────────────────────

def parse_style_ranges(inline_styles_el, text):
    """
    把 <inline-styles> 里的各类样式区间解析成:
    {char_index: {attr: value, ...}, ...}
    """
    if inline_styles_el is None:
        return {}

    char_styles = {}  # index -> {attr: value}

    def apply(attr, from_i, to_i, value):
        for i in range(from_i, to_i):
            if i not in char_styles:
                char_styles[i] = {}
            char_styles[i][attr] = value

    style_tags = {
        "bold":       ("bold",       lambda v: v == "true"),
        "italic":     ("italic",     lambda v: v == "true"),
        "underline":  ("underline",  lambda v: v == "true"),
        "strikethrough": ("strikethrough", lambda v: v == "true"),
        "color":      ("color",      lambda v: v.lower()),
        "back-color": ("back-color", lambda v: v.lower()),
        "font-size":  ("font-size",  lambda v: int(v)),
    }

    for child in inline_styles_el:
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if local not in style_tags:
            continue
        attr_name, parser = style_tags[local]
        from_el = child.find(tag("from"))
        to_el   = child.find(tag("to"))
        val_el  = child.find(tag("value"))
        if from_el is None or to_el is None or val_el is None:
            continue
        try:
            from_i = int(from_el.text)
            to_i   = int(to_el.text)
            value  = parser(val_el.text.strip())
            apply(attr_name, from_i, to_i, value)
        except Exception:
            pass

    return char_styles


# ── 把带样式的文本渲染成 HTML span ────────────────────────────

def render_styled_text(text, char_styles):
    """
    将字符级样式合并成连续区间，输出带 <span> 标签的字符串
    """
    if not text:
        return ""
    if not char_styles:
        return escape_md(text)

    # 把字符按样式组合分组
    segments = []
    prev_style = None
    seg_start  = 0

    for i, ch in enumerate(text):
        s = char_styles.get(i, {})
        if s != prev_style:
            if i > seg_start:
                segments.append((text[seg_start:i], prev_style or {}))
            seg_start  = i
            prev_style = s
    segments.append((text[seg_start:], prev_style or {}))

    result = []
    for seg_text, styles in segments:
        if not seg_text:
            continue
        html = escape_md(seg_text)
        html = apply_inline_styles(html, styles)
        result.append(html)

    return "".join(result)


def apply_inline_styles(text, styles):
    """把样式字典应用到文本上，返回带 HTML 标签的字符串"""
    if not styles:
        return text

    css_parts = []
    bg = styles.get("back-color", "")
    fg = styles.get("color", "")
    bold = styles.get("bold", False)
    italic = styles.get("italic", False)
    underline = styles.get("underline", False)
    strike = styles.get("strikethrough", False)
    font_size = styles.get("font-size", None)

    # 背景色（忽略白色）、前景色（忽略黑色）、字号 → 放进 span style
    if bg and bg not in ("#ffffff", "#fff", ""):
        css_parts.append(f"background-color:{bg}")
    if fg and fg not in ("#000000", "#000", ""):
        css_parts.append(f"color:{fg}")
    if font_size:
        css_parts.append(f"font-size:{font_size}px")

    # 先用 span 包颜色/字号（最内层）
    if css_parts:
        style_str = ";".join(css_parts)
        text = f'<span style="{style_str}">{text}</span>'

    # 再从内到外套语义标签（Obsidian 识别外层标签更可靠）
    if bold:
        text = f"<strong>{text}</strong>"
    if italic:
        text = f"<em>{text}</em>"
    if underline:
        text = f"<u>{text}</u>"
    if strike:
        text = f"<s>{text}</s>"

    return text





def escape_md(text):
    """转义 Markdown 特殊字符（不转义在 span 内部的情况）"""
    # 只转义可能干扰 Markdown 结构的字符
    # 不转义 * _ ` 等，因为它们套在 span 里不会影响
    return text


# ── 缩进 → 空格缩进 ──────────────────────────────────────────

INDENT_PX = 28  # 每级缩进像素（模拟有道笔记视觉效果）


# ── 主转换函数 ────────────────────────────────────────────────

def convert_note_to_md(note_path: str) -> str:
    with open(note_path, "rb") as f:
        raw = f.read()

    root = ET.fromstring(raw)
    body = root.find(tag("body"))
    if body is None:
        return ""

    lines = []

    for el in body:
        local = el.tag.split("}")[-1] if "}" in el.tag else el.tag

        if local == "para":
            lines.append(convert_para(el))

        elif local == "list-item":
            lines.append(convert_list_item(el))

        elif local == "image":
            lines.append(convert_image(el))

        else:
            # 未知节点，跳过
            pass

    return "\n".join(lines)


def convert_para(el):
    text_el = el.find(tag("text"))
    text = (text_el.text or "") if text_el is not None else ""

    inline_el = el.find(tag("inline-styles"))
    char_styles = parse_style_ranges(inline_el, text)

    styles_el = el.find(tag("styles"))
    indent = get_indent(styles_el)

    # 空段落 → 返回空字符串，join 时自然产生空行（Markdown 段落分隔）
    if not text.strip():
        return ""

    rendered = render_styled_text(text, char_styles)

    if indent > 0:
        px = indent * INDENT_PX
        return f'<div style="margin-left:{px}px">{rendered}</div>'
    return rendered



def convert_list_item(el):
    level = int(el.get("level", "1"))

    text_el = el.find(tag("text"))
    text = (text_el.text or "") if text_el is not None else ""

    inline_el = el.find(tag("inline-styles"))
    char_styles = parse_style_ranges(inline_el, text)

    styles_el = el.find(tag("styles"))
    extra_indent = get_indent(styles_el)

    rendered = render_styled_text(text, char_styles)

    # 用 margin-left 控制层级缩进，bullet 用 • 符号
    total_level = (level - 1) + extra_indent
    px = total_level * INDENT_PX
    bullet = "•"
    if px > 0:
        return f'<div style="margin-left:{px}px">{bullet} {rendered}</div>'
    return f"{bullet} {rendered}"


def convert_image(el):
    source_el = el.find(tag("source"))
    if source_el is None or not source_el.text:
        return ""
    url = source_el.text.strip()
    # 输出标准 Markdown 图片语法，image.py 的迁移逻辑才能识别并下载到本地
    return f"![]({url})"


def get_indent(styles_el):
    """从 <styles> 中读取 text-indent 级别"""
    if styles_el is None:
        return 0
    indent_el = styles_el.find(tag("text-indent"))
    if indent_el is not None and indent_el.text:
        try:
            return int(indent_el.text)
        except ValueError:
            pass
    return 0


# ── 入口 ─────────────────────────────────────────────────────

def process_file(input_path, output_path=None):
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".md"))

    md = convert_note_to_md(input_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ {input_path} → {output_path}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--dir":
        if len(args) < 2:
            print("用法: python3 note2md.py --dir <目录>")
            sys.exit(1)
        d = args[1]
        for root_dir, _, files in os.walk(d):
            for fn in files:
                if fn.endswith(".note"):
                    inp = os.path.join(root_dir, fn)
                    process_file(inp)
    else:
        inp = args[0]
        out = args[1] if len(args) > 1 else None
        process_file(inp, out)


if __name__ == "__main__":
    main()
