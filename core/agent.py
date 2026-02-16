"""
DeepContext Agent 核心引擎
原来的 client.py (包含大模型调用和 ReAct 循环)
"""

import asyncio
import json
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from config import DEEPSEEK_API_KEY, BASE_URL, MAX_TURNS
from core.prompt import DEFAULT_USER_QUERY, SYSTEM_PROMPT


class DeepContextAgent:
    """DeepContext 自主 Agent 类"""
    
    def __init__(self):
        self.llm_client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=BASE_URL
        )
        self.server_params = StdioServerParameters(command="python", args=["server.py"])
    
    async def run(self, user_query=None):
        """运行 DeepContext Agent"""
        if user_query is None:
            user_query = DEFAULT_USER_QUERY
            
        print("🚀 启动 DeepContext 自主 Agent...\n")
        
        async with stdio_client(self.server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # 1. 动态加载所有技能 (包括读取和写入)
                mcp_tools = await session.list_tools()
                qwen_tools = [{
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema
                    }
                } for t in mcp_tools.tools]
                
                # 2. 设置系统提示词和用户查询
                print(f"🧑‍💻 [用户指令]:\n{user_query}\n")
                
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_query}
                ]
                
                # ==========================================================
                # 3. 核心升级：引入 Agent 状态机循环 (ReAct Loop)
                # ==========================================================
                
                for turn in range(MAX_TURNS):
                    print(f"🔄 [Agent 思考轮次 {turn + 1}]...")
                    
                    response = await self.llm_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages,
                        tools=qwen_tools
                    )
                    
                    assistant_message = response.choices[0].message
                    messages.append(assistant_message) # 压栈：记录神探的决定
                    
                    # 情况 A：模型决定调用工具
                    if assistant_message.tool_calls:
                        for tool_call in assistant_message.tool_calls:
                            func_name = tool_call.function.name
                            func_args = json.loads(tool_call.function.arguments)
                            
                            print(f"  ⚡ [执行动作]: 正在调用 `{func_name}` \n  参数: {func_args}")
                            
                            # 执行本地 MCP 工具
                            mcp_result = await session.call_tool(func_name, arguments=func_args)
                            tool_result_text = mcp_result.content[0].text
                            print(f"  📦 [工具返回]: {tool_result_text}")
                            
                            # 压栈：记录工具的执行结果
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": func_name,
                                "content": tool_result_text
                            })
                        print("-" * 40)
                        # 工具执行完后，进行下一次 for 循环，让大模型继续思考
                        
                    # 情况 B：模型没有调用工具，输出了普通文本，说明任务完成了！
                    else:
                        print(f"\n✅ [Agent 最终总结]:\n{assistant_message.content}")
                        break # 跳出循环，任务结束
                
                if turn == MAX_TURNS - 1:
                    print("⚠️ 警告：达到了最大循环次数，Agent 可能陷入了死循环。")


# 兼容性函数，保持与原始代码的接口一致
async def run_deepcontext_agent():
    """兼容性函数，创建并运行 Agent"""
    agent = DeepContextAgent()
    await agent.run()