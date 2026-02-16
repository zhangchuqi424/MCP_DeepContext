# DeepContext - 智能知识管理系统

DeepContext 是一个基于 MCP (Model Context Protocol) 的智能知识管理系统，能够自动读取本地 Markdown 笔记，提取知识三元组，并构建可查询的知识图谱。

## 🏗️ 项目架构

```
DeepContext/
├── core/                  # 核心引擎层 (The Brain)
│   ├── __init__.py
│   ├── agent.py           # 原来的 client.py (包含大模型调用和 ReAct 循环)
│   └── prompt.py          # 专门用来存放系统提示词和大段的指令字符串
├── tools/                 # 业务逻辑层 (The Skills)
│   ├── __init__.py
│   ├── file_tools.py      # 将 list_my_notes 和 read_note_content 放在这里
│   └── graph_tools.py     # 将 add_knowledge_triplet 和 query_knowledge_graph 放在这里
├── database/              # 数据持久层 (The Memory)
│   ├── __init__.py
│   └── sqlite_db.py       # 专门负责 init_db() 和数据库连接操作
├── config/                # 配置中心
│   ├── __init__.py
│   └── settings.py        # 集中管理所有的变量，比如 DEEPSEEK_API_KEY, DB_PATH
├── main.py                # 程序的唯一启动入口 (启动 MCP Server 或 Agent Client)
├── server.py              # MCP Server 实现
├── requirements.txt       # 依赖清单 (pip freeze > requirements.txt)
└── README.md              # 项目的门面，介绍架构和运行方式
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `config/settings.py` 中配置你的 DeepSeek API Key：

```python
DEEPSEEK_API_KEY = "your-api-key-here"
```

### 3. 运行项目

#### 启动 Agent 客户端（默认模式）

```bash
python main.py
# 或者
python main.py --mode agent
```

#### 启动 MCP Server

```bash
python main.py --mode server
```

#### 使用自定义查询

```bash
python main.py --mode agent --query "你的问题"
```

## 🔧 核心功能

### 1. 智能笔记读取
- 自动扫描指定目录下的 Markdown 文件
- 安全读取文件内容（仅限 .md 文件）
- 支持中文编码

### 2. 知识提取与存储
- 从笔记中自动提取知识三元组（实体-关系-实体）
- 存储到 SQLite 知识图谱数据库
- 支持知识溯源（记录来源文件）

### 3. 智能查询
- 支持自然语言查询
- 自动生成 SQL 查询语句
- 安全的查询限制（仅允许 SELECT）

### 4. ReAct 循环引擎
- 思考-行动循环机制
- 多步推理能力
- 防死循环保护

## 🧠 技术原理

### ReAct (Reasoning and Acting) 循环

DeepContext 采用 ReAct 模式，让大模型能够：

1. **思考 (Reasoning)**: 分析当前情况，决定下一步行动
2. **行动 (Acting)**: 调用相应工具执行具体操作
3. **观察 (Observation)**: 获取工具执行结果
4. **循环**: 基于观察结果继续思考，直到任务完成

### MCP (Model Context Protocol)

使用 MCP 协议实现：
- 标准化的工具接口
- 进程间安全通信
- 可扩展的工具生态

## 📊 数据结构

### 知识三元组表 (knowledge_triplets)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| source_entity | TEXT | 实体 A |
| relation | TEXT | 关系 |
| target_entity | TEXT | 实体 B |
| source_file | TEXT | 来源文件 |
| created_at | TIMESTAMP | 创建时间 |

## 🔒 安全特性

1. **文件访问限制**: 仅允许读取 .md 文件
2. **SQL 注入防护**: 仅允许 SELECT 查询
3. **路径验证**: 防止目录遍历攻击
4. **循环保护**: MAX_TURNS 限制防止死循环

## 📝 使用示例

### 查询已学习的协议

```python
# 用户查询
"我之前学习了什么协议？这个协议有什么用？"

# Agent 会自动：
# 1. 查询知识图谱
# 2. 找到相关协议信息
# 3. 总结回答用户
```

### 添加新知识

```python
# Agent 读取新笔记后自动提取：
# (MCP协议) -> (作用于) -> (大模型与本地环境的解耦)
# (ReAct循环) -> (实现) -> (多步推理能力)
```

## 🛠️ 开发指南

### 添加新工具

1. 在 `tools/` 目录下创建新模块
2. 实现工具函数
3. 在 `server.py` 中注册工具
4. 更新 `tools/__init__.py` 导出

### 修改配置

所有配置项集中在 `config/settings.py`：
- API 配置
- 数据库路径
- 运行参数

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**DeepContext - 让知识管理更智能** 🧠✨