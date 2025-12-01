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
        # 再修复有序列表的编号
        fixed_content = MarkdownFix.fix_ordered_list_numbers(fixed_content)
        
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