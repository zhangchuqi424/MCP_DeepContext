from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path
import sqlite3  # 引入原生 SQLite 库


# 1. 初始化 MCP Server，命名为 DeepContext
mcp = FastMCP("DeepContext")


# ---------------------------------------------------------
# 新增：数据库初始化逻辑
# ---------------------------------------------------------
DB_PATH = "deepcontext_graph.db"

def init_db():
    """初始化知识图谱数据库，如果表不存在则创建"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 设计核心表结构：知识三元组表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_triplets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_entity TEXT NOT NULL,  -- 实体 A (如: "MCP协议")
            relation TEXT NOT NULL,       -- 关系 (如: "作用于")
            target_entity TEXT NOT NULL,  -- 实体 B (如: "大模型与本地环境的解耦")
            source_file TEXT NOT NULL,    -- 知识来源 (溯源字段：来自哪篇笔记)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 在启动前先建好数据库
init_db()




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

@mcp.tool()
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

# ---------------------------------------------------------
# 新增：第三个 MCP 工具 (赋予模型"写入"记忆的能力)
# ---------------------------------------------------------
@mcp.tool()
def add_knowledge_triplet(source_entity: str, relation: str, target_entity: str, source_file: str) -> str:
    """
    核心技能：将提取到的知识三元组保存到本地知识图谱数据库中。
    当你阅读完笔记，提取出核心概念和它们之间的关系时，调用此工具进行存储。
    """
    try:
        # 注意：SQLite 在多线程并发调用时，最好在函数内部建立连接
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_triplets (source_entity, relation, target_entity, source_file)
            VALUES (?, ?, ?, ?)
        ''', (source_entity, relation, target_entity, source_file))
        
        conn.commit()
        conn.close()
        
        return f"✅ 成功将知识 [{source_entity} -> {relation} -> {target_entity}] 写入数据库 (来源: {source_file})。"
    except Exception as e:
        return f"❌ 写入数据库失败，底层错误：{str(e)}"

# ... 前面的代码保持不变 ...

@mcp.tool()
def query_knowledge_graph(sql_query: str) -> str:
    """
    核心技能：执行 SQL 查询语句，从知识图谱数据库中检索信息。
    当你需要回答用户关于已有知识的问题时，使用此工具。
    
    【重要提示】数据库表结构如下：
    表名: knowledge_triplets
    字段: 
      - id (INTEGER)
      - source_entity (TEXT) 实体A
      - relation (TEXT) 关系
      - target_entity (TEXT) 实体B
      - source_file (TEXT) 来源文件
    
    注意：为了安全，你只能执行 SELECT 查询。
    """
    # 1. 防御性编程：只读限制 (极简版的安全校验)
    if not sql_query.strip().upper().startswith("SELECT"):
        return "❌ 安全拦截：为了保护图谱数据，当前工具仅允许执行 SELECT 查询语句。"
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 2. 执行大模型生成的 SQL 语句
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        # 3. 获取表头列名，方便大模型阅读
        column_names = [description[0] for description in cursor.description]
        conn.close()
        
        if not results:
            return f"✅ SQL执行成功: '{sql_query}'，但数据库中没有找到匹配的数据。"
            
        # 4. 将查询结果格式化为纯文本表格返回给大模型
        output = f"✅ SQL执行成功: '{sql_query}'\n找到 {len(results)} 条记录：\n"
        output += " | ".join(column_names) + "\n"
        output += "-" * 50 + "\n"
        for row in results:
            output += " | ".join(str(item) for item in row) + "\n"
            
        return output
        
    except Exception as e:
        # 如果大模型 SQL 写错了，把错误信息返回给它，它会自动修正！
        return f"❌ SQL语法错误或执行失败：{str(e)}。请检查你的 SQL 语句并重试。"

if __name__ == "__main__":
    # 3. 启动 Server
    # 默认使用 stdio（标准输入输出）进行进程间通信 (IPC)，这是最安全、最轻量的本地 Agent 通信方式
    mcp.run()