"""
DeepContext 数据持久层
负责数据库连接和操作
"""

from .sqlite_db import init_db

__all__ = ['init_db']