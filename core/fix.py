import re

class MarkdownFix(object):
    """
    修复 markdown 文件，转换出来的 markdown 文件可能需要修复
    比如有序列表的编号
    """

    @staticmethod
    def fix_markdown_file(markdown_content):
        # 先修复列表缩进
        fixed_content = MarkdownFix.fix_list_indentation(markdown_content)
        # 修复有序列表的编号
        fixed_content = MarkdownFix.fix_ordered_list_numbers(fixed_content)
        # 修复段落间距
        fixed_content = MarkdownFix.fix_paragraph_spacing(fixed_content)
        
        return fixed_content
    
    @staticmethod
    def fix_ordered_list_numbers(markdown_content):
        """
        修复markdown中有序列表的编号问题
        """
        lines = markdown_content.split('\n')
        fixed_lines = []
        counters = {}  # 用于跟踪各层级的编号
        list_context_stack = []  # 跟踪列表上下文的缩进级别
        in_list_context = False  # 标记是否在列表上下文中
        
        for line in lines:
            # 匹配以制表符开头，后跟"1. "的行
            match = re.match(r'^(\t*)(1\.)\s(.*)', line)

            if match:
                tabs = match.group(1)  # 获取制表符前缀
                content = match.group(3)  # 获取列表项内容
                
                indent_level = len(tabs)  # 制表符数量即为缩进级别
                
                # 如果之前不在列表上下文中，现在进入了，重置状态
                if not in_list_context:
                    counters = {}
                    list_context_stack = []
                    in_list_context = True
                
                # 更新列表上下文栈
                # 移除比当前缩进更深的上下文
                while list_context_stack and list_context_stack[-1] > indent_level:
                    list_context_stack.pop()
                
                # 如果是新的缩进级别，添加到栈中
                if not list_context_stack or list_context_stack[-1] < indent_level:
                    list_context_stack.append(indent_level)
                
                # 清除比当前层级更深的计数器
                keys_to_remove = [k for k in counters.keys() if k > indent_level]
                for key in keys_to_remove:
                    del counters[key]
                
                # 初始化或更新当前层级的计数器
                if indent_level not in counters:
                    counters[indent_level] = 1
                else:
                    counters[indent_level] += 1
                
                # 获取当前层级应该使用的编号
                number = counters[indent_level]
                
                # 构造修正后的行
                fixed_line = f"{tabs}{number}. {content}"
                fixed_lines.append(fixed_line)
            else:
                # 不是有序列表项，直接添加
                fixed_lines.append(line)
                # 检查是否是明显脱离列表上下文的内容（如标题、空行等）
                if not line.strip() or line.strip().startswith('#') or line.strip().startswith('---'):
                    # 重置列表上下文状态
                    in_list_context = False
        
        return '\n'.join(fixed_lines)
    
    @staticmethod
    def fix_list_indentation(markdown_content):
        """
        修复列表中各种内容（图片、代码块等）的缩进问题，确保它们与列表项对齐
        专门处理使用制表符缩进的情况
        """
        lines = markdown_content.split('\n')
        fixed_lines = []
        i = 0
        current_list_stack = []  # 跟踪当前所在的列表层级
        
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是列表项（有序或无序），支持制表符缩进
            list_match = re.match(r'^(\t*)([-\d]+\.|-)\s(.*)', line)
            if list_match:
                tabs = list_match.group(1)  # 获取制表符前缀
                
                # 更新当前列表栈状态
                current_indent_level = len(tabs)
                # 移除比当前缩进级别更深的列表层级
                while current_list_stack and len(current_list_stack[-1]) > current_indent_level:
                    current_list_stack.pop()
                # 如果当前缩进级别不存在于栈中，则添加
                if not current_list_stack or len(current_list_stack[-1]) < current_indent_level:
                    current_list_stack.append(tabs)
                
                fixed_lines.append(line)
                i += 1
                
                # 检查后续行是否有需要调整缩进的内容
                while i < len(lines):
                    next_line = lines[i]
                    
                    # 如果是空行，直接添加
                    if not next_line.strip():
                        fixed_lines.append(next_line)
                        i += 1
                        continue
                    
                    # 检查是否是新的列表项（使用制表符缩进）
                    next_list_match = re.match(r'^(\t*)([-\d]+\.|-)\s(.*)', next_line)
                    if next_list_match:
                        next_tabs = next_list_match.group(1)
                        # 如果下一个列表项缩进更少或相同，说明当前列表项结束
                        if len(next_tabs) <= current_indent_level:
                            break
                        else:
                            # 否则是子列表项，保持原样
                            fixed_lines.append(next_line)
                            current_list_stack.append(next_tabs)
                            i += 1
                            continue
                    
                    # 检查是否是非列表内容（图片、代码块等）
                    if (next_line.strip() and 
                        not re.match(r'^(\t*)([-\d]+\.|-)\s', next_line) and
                        not next_line.strip().startswith('#')):  # 不是标题
                        
                        # 获取当前应该使用的缩进（即当前列表项的缩进）
                        current_list_indent = current_list_stack[-1] if current_list_stack else ""
                        
                        # 检查缩进是否正确
                        if not next_line.startswith(current_list_indent):
                            # 调整缩进使其与列表项对齐
                            adjusted_line = current_list_indent + next_line.lstrip()
                            fixed_lines.append(adjusted_line)
                        else:
                            # 缩进已经正确，直接添加
                            fixed_lines.append(next_line)
                        
                        i += 1
                    else:
                        break
            else:
                fixed_lines.append(line)
                i += 1
                # 重置列表栈状态
                current_list_stack = []
                
        return '\n'.join(fixed_lines)
    
    @staticmethod
    def fix_paragraph_spacing(markdown_content):
        """
        修复段落间距，在连续的普通文本段落之间添加空行
        """
        lines = markdown_content.split('\n')
        fixed_lines = []
        
        in_code_block = False  # 跟踪是否在代码块中
        
        for i in range(len(lines)):
            line = lines[i]
            
            # 检查是否进入或退出代码块
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            
            fixed_lines.append(line)
            
            # 只有不在代码块中时才考虑添加空行
            if not in_code_block:
                # 判断是否需要在当前行后添加空行
                if MarkdownFix._should_add_line_break(lines, i):
                    fixed_lines.append("")  # 添加空行
        
        return '\n'.join(fixed_lines)
    
    @staticmethod
    def _should_add_line_break(lines, current_index):
        """
        判断是否需要在当前行后添加空行分隔段落
        """
        # 如果是最后一行，不需要添加空行
        if current_index >= len(lines) - 1:
            return False
            
        current_line = lines[current_index]
        next_line = lines[current_index + 1]
        
        # 如果当前行为空行，不需要再添加空行
        if not current_line.strip():
            return False
            
        # 如果下一行为空行，说明已经有分隔了，不需要再添加
        if not next_line.strip():
            return False
            
        # 检查当前行和下一行是否都是普通文本行
        if (MarkdownFix._is_plain_text_line(current_line) and 
            MarkdownFix._is_plain_text_line(next_line)):
            return True
            
        return False
    
    @staticmethod
    def _is_plain_text_line(line):
        """
        判断一行是否为普通文本（而不是特殊格式）
        """
        stripped_line = line.strip()
        
        # 空行不是普通文本
        if not stripped_line:
            return False
            
        # 特殊格式的行不是普通文本
        special_patterns = [
            r'^[-*+]\s',           # 无序列表
            r'^\d+\.\s',           # 有序列表
            r'^#{1,6}\s',          # 标题
            r'^!\[.*\]\(.*\)',     # 图片
            r'^\[.*\]\(.*\)',      # 链接
            r'^\[\[.*\]\]',        # 内部链接
            r'^```',               # 代码块开始/结束
            r'^>',                 # 引用
            r'^\s*[-*_]{3,}\s*$',  # 分割线
        ]
        
        for pattern in special_patterns:
            if re.match(pattern, stripped_line):
                return False
                
        return True