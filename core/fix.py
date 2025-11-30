import re

class MarkdownFix(object):
    """
    修复 markdown 文件，转换出来的 markdown 文件可能需要修复
    比如有序列表的编号
    """

    @staticmethod
    def fix_markdown_file(file_path):
        fixed_markdown_content = MarkdownFix.fix_ordered_list_numbers(file_path)

        return fixed_markdown_content
    
    @staticmethod
    def fix_ordered_list_numbers(markdown_content):
        """
        修复markdown中有序列表的编号问题
        """
        lines = markdown_content.split('\n')
        fixed_lines = []
        counters = {}  # 用于跟踪各层级的编号
        in_ordered_list = False  # 标记是否在有序列表中
        
        for line in lines:
            # 匹配以制表符开头，后跟"1. "的行
            match = re.match(r'^(\t*)(1\.)\s(.*)', line)

            if match:
                tabs = match.group(1)  # 获取制表符前缀
                content = match.group(3)  # 获取列表项内容
                
                indent_level = len(tabs)  # 制表符数量即为缩进级别
                
                # 如果之前不在有序列表中，现在进入了，重置计数器
                if not in_ordered_list:
                    counters = {}
                    in_ordered_list = True
                
                # 清除比当前层级更深的计数器（退出嵌套时重置子层级）
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
                # 标记离开有序列表
                in_ordered_list = False
        
        return '\n'.join(fixed_lines)