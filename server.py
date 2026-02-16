from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path

# 1. 初始化 MCP Server，命名为 DeepContext
mcp = FastMCP("DeepContext")

# 2. 注册第一个 Skill (Tool)
# 使用 @mcp.tool() 装饰器，SDK 会自动将函数的类型提示和 docstring 转化为大模型能懂的 JSON Schema
@mcp.tool()
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

if __name__ == "__main__":
    # 3. 启动 Server
    # 默认使用 stdio（标准输入输出）进行进程间通信 (IPC)，这是最安全、最轻量的本地 Agent 通信方式
    mcp.run()