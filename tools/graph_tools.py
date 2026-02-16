"""
DeepContext 知识图谱工具模块
包含 add_knowledge_triplet 和 query_knowledge_graph 功能
"""

from database.sqlite_db import add_knowledge_triplet as db_add_triplet, query_knowledge_graph as db_query


def add_knowledge_triplet(source_entity: str, relation: str, target_entity: str, source_file: str) -> str:
    """
    核心技能：将提取到的知识三元组保存到本地知识图谱数据库中。
    当你阅读完笔记，提取出核心概念和它们之间的关系时，调用此工具进行存储。
    """
    return db_add_triplet(source_entity, relation, target_entity, source_file)


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
    return db_query(sql_query)