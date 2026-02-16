import asyncio
import json
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# 初始化 API 客户端 (使用 OpenAI 兼容模式)
API_KEY = "sk-e3bb89eb98484d31ad2ec9ae2784ac83" 

llm_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

async def run_deepcontext_agent():
    print("🚀 正在启动 DeepContext 真实智能 Agent 客户端...\n")

    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("✅ 成功连接到本地 MCP Server！")
            
            # 1. 获取 MCP Server 提供的工具，并将其转换为 大模型 能懂的 JSON Schema 格式
            mcp_tools = await session.list_tools()
            qwen_tools = []
            for t in mcp_tools.tools:
                qwen_tools.append({
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema # MCP 自动生成的标准 JSON Schema
                    }
                })
            
            # 2. 准备对话历史 (Memory)
            user_query = "帮我看看当前 '.' 目录下有哪些 md 笔记文件？"
            print(f"🧑‍💻 [用户提问]: {user_query}\n")
            
            messages = [{"role": "user", "content": user_query}]
            
            # =====================================================================
            # 3. 第一次请求大模型 (大脑开始推理与路由)
            # =====================================================================
            print("🧠 [大模型思考中...]")
            response = await llm_client.chat.completions.create(
                model="deepseek-chat", 
                messages=messages,
                tools=qwen_tools # 把工具说明书“喂”给模型
            )
            
            assistant_message = response.choices[0].message
            
            # 判断大模型是否决定调用工具
            if assistant_message.tool_calls:
                # =====================================================================
                # 4. 截获工具调用指令，并在本地执行 (Action)
                # =====================================================================
                tool_call = assistant_message.tool_calls[0]
                func_name = tool_call.function.name
                # 解析大模型生成的参数 JSON
                func_args = json.loads(tool_call.function.arguments) 
                
                print(f"⚡ [触发执行]: Qwen 决定调用工具 `{func_name}`, 提取到的参数: {func_args}")
                
                # 真正向本地的 MCP Server 发起调用请求
                mcp_result = await session.call_tool(func_name, arguments=func_args)
                tool_result_text = mcp_result.content[0].text
                print(f"📦 [本地文件系统返回]:\n{tool_result_text}\n")
                
                # =====================================================================
                # 5. 将执行结果拼接到上下文中，发起第二次请求 (Observation & 总结)
                # =====================================================================
                # 重点：必须把大模型刚才的“调用动作”也加进历史记录，维持对话链的完整性
                messages.append(assistant_message) 
                # 把本地工具执行的结果告诉大模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": tool_result_text
                })
                
                print("🧠 [大模型阅读本地数据并总结中...]")
                final_response = await llm_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                
                print(f"🤖 [Agent 最终回答]:\n{final_response.choices[0].message.content}")
                
            else:
                # 如果大模型认为不需要调用工具，直接输出了普通文本
                print(f"🤖 [Agent 直接回答]:\n{assistant_message.content}")

if __name__ == "__main__":
    asyncio.run(run_deepcontext_agent())