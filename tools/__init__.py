"""
DeepContext 业务逻辑层
包含所有工具和技能
"""

from .file_tools import list_my_notes, read_note_content
from .graph_tools import add_knowledge_triplet, query_knowledge_graph

__all__ = [
    'list_my_notes',
    'read_note_content', 
    'add_knowledge_triplet',
    'query_knowledge_graph'
]