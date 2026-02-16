"""
DeepContext 文件工具模块
包含 list_my_notes 和 read_note_content 功能
"""

from pathlib import Path


def list_my_notes(directory_path: str) -> str:
    """
    核心技能：列出指定本地目录下的所有 Markdown 笔记文件。
    """
    try:
        path = Path(directory_path)
        
        # 基础的防御性编程：防止大模型幻觉瞎编路径，或者越权访问系统文件
        if not path.exists() or not path.is_dir():
            return f"执行失败：目录 '{directory_path}' 不存在或不是一个有效的文件夹。"
            
        # 筛选 .md 文件
        md_files = [f.name for f in path.iterdir() if f.is_file() and f.suffix == '.md']
        
        if not md_files:
            return f"在目录 '{directory_path}' 中没有找到任何 Markdown (.md) 笔记。"
            
        # 返回格式化的字符串给大模型
        result = f"成功读取目录 '{directory_path}'，包含以下笔记：\n"
        for i, file in enumerate(md_files, 1):
            result += f"{i}. {file}\n"
            
        return result
        
    except Exception as e:
        # 捕获异常并返回给模型，让模型知道调用出错了，而不是直接让服务端崩溃
        return f"读取目录时发生底层系统错误：{str(e)}"


def read_note_content(filepath: str) -> str:
    """
    核心技能：读取指定 Markdown 笔记文件的全部文本内容。
    当用户询问某个具体笔记里写了什么，或者需要提取知识时，调用此工具。
    """
    try:
        path = Path(filepath)
        
        # 1. 防御性编程：检查文件是否存在，以及是不是文件
        if not path.exists():
            return f"执行失败：找不到文件 '{filepath}'。请检查路径是否正确。"
        if not path.is_file():
            return f"执行失败：'{filepath}' 不是一个有效的文件（可能是一个目录）。"
            
        # 2. 防御性编程：限制只能读取 .md 文件，防止大模型越权读取系统密码文件 (如 /etc/passwd)
        if path.suffix.lower() != '.md':
            return f"安全拦截：为了系统安全，当前仅允许读取 Markdown (.md) 文件。"

        # 3. 读取并返回内容 (指定 utf-8 编码防止中文乱码)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return f"文件 '{filepath}' 读取成功，内容如下：\n\n{content}"
        
    except UnicodeDecodeError:
        return f"执行失败：文件 '{filepath}' 不是标准的 UTF-8 文本编码，无法读取。"
    except Exception as e:
        return f"读取文件时发生底层系统错误：{str(e)}"