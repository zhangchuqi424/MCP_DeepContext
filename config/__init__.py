"""
DeepContext 配置中心
集中管理所有配置项和常量
"""

from .settings import *

__all__ = [
    'DEEPSEEK_API_KEY',
    'DB_PATH',
    'MAX_TURNS',
    'BASE_URL'
]