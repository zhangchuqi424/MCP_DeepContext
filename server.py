"""
DeepContext MCP Server
提供工具和资源给 Agent 使用
"""

from mcp.server.fastmcp import FastMCP
from tools.file_tools import list_my_notes, read_note_content
from tools.graph_tools import add_knowledge_triplet, query_knowledge_graph
from database import init_db

# 1. 初始化 MCP Server，命名为 DeepContext
mcp = FastMCP("DeepContext")

# 2. 在启动前先建好数据库
init_db()

# 3. 注册文件相关工具
@mcp.tool()
def list_my_notes_tool(directory_path: str) -> str:
    """
    核心技能：列出指定本地目录下的所有 Markdown 笔记文件。
    """
    return list_my_notes(directory_path)

@mcp.tool()
def read_note_content_tool(filepath: str) -> str:
    """
    核心技能：读取指定 Markdown 笔记文件的全部文本内容。
    当用户询问某个具体笔记里写了什么，或者需要提取知识时，调用此工具。
    """
    return read_note_content(filepath)

# 4. 注册知识图谱相关工具
@mcp.tool()
def add_knowledge_triplet_tool(source_entity: str, relation: str, target_entity: str, source_file: str) -> str:
    """
    核心技能：将提取到的知识三元组保存到本地知识图谱数据库中。
    当你阅读完笔记，提取出核心概念和它们之间的关系时，调用此工具进行存储。
    """
    return add_knowledge_triplet(source_entity, relation, target_entity, source_file)

@mcp.tool()
def query_knowledge_graph_tool(sql_query: str) -> str:
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
    return query_knowledge_graph(sql_query)

if __name__ == "__main__":
    # 5. 启动 Server
    # 默认使用 stdio（标准输入输出）进行进程间通信 (IPC)，这是最安全、最轻量的本地 Agent 通信方式
    mcp.run()