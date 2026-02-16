"""
DeepContext 数据库操作模块
专门负责 init_db() 和数据库连接操作
"""

import sqlite3
from config import DB_PATH


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
    print(f"数据库初始化完成: {DB_PATH}")


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def add_knowledge_triplet(source_entity: str, relation: str, target_entity: str, source_file: str) -> str:
    """
    将提取到的知识三元组保存到本地知识图谱数据库中。
    当你阅读完笔记，提取出核心概念和它们之间的关系时，调用此工具进行存储。
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_triplets (source_entity, relation, target_entity, source_file)
            VALUES (?, ?, ?, ?)
        ''', (source_entity, relation, target_entity, source_file))
        
        conn.commit()
        conn.close()
        
        return f"成功将知识 [{source_entity} -> {relation} -> {target_entity}] 写入数据库 (来源: {source_file})。"
    except Exception as e:
        return f"❌ 写入数据库失败，底层错误：{str(e)}"


def query_knowledge_graph(sql_query: str) -> str:
    """
    执行 SQL 查询语句，从知识图谱数据库中检索信息。
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
        return "安全拦截：为了保护图谱数据，当前工具仅允许执行 SELECT 查询语句。"
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 2. 执行大模型生成的 SQL 语句
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        # 3. 获取表头列名，方便大模型阅读
        column_names = [description[0] for description in cursor.description]
        conn.close()
        
        if not results:
            return f"SQL执行成功: '{sql_query}'，但数据库中没有找到匹配的数据。"
            
        # 4. 将查询结果格式化为纯文本表格返回给大模型
        output = f"SQL执行成功: '{sql_query}'\n找到 {len(results)} 条记录：\n"
        output += " | ".join(column_names) + "\n"
        output += "-" * 50 + "\n"
        for row in results:
            output += " | ".join(str(item) for item in row) + "\n"
            
        return output
        
    except Exception as e:
        # 如果大模型 SQL 写错了，把错误信息返回给它，它会自动修正！
        return f"SQL语法错误或执行失败：{str(e)}。请检查你的 SQL 语句并重试。"