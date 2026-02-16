"""
DeepContext 配置文件
集中管理所有的变量和配置项
"""

# API 配置
DEEPSEEK_API_KEY = "sk-e3bb89eb98484d31ad2ec9ae2784ac83"
BASE_URL = "https://api.deepseek.com"

# 数据库配置
DB_PATH = "deepcontext_graph.db"

# Agent 配置
MAX_TURNS = 20  # 防御性编程：防止大模型死循环，最多允许执行20步

# 日志配置
LOG_LEVEL = "INFO"