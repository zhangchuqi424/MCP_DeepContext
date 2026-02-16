import asyncio
import json
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

DEEPSEEK_API_KEY = "sk-e3bb89eb98484d31ad2ec9ae2784ac83" 
llm_client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com" 
)

async def run_deepcontext_agent():
    print("🚀 启动 DeepContext 自主 Agent...\n")
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read_stream, write_stream):
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
            
            # 2. 极其关键的 Prompt Engineering：给 Agent 下达多步指令
            user_query = """
            请帮我查阅知识图谱数据库，回答以下问题：
            我之前学习了什么协议？这个协议有什么用？
            请写出正确的 SQL 语句查询数据库，然后用一句话总结答案告诉我。
            """
            print(f"🧑‍💻 [用户指令]:\n{user_query}\n")
            
            messages = [{"role": "user", "content": user_query}]
            
            # ==========================================================
            # 3. 核心升级：引入 Agent 状态机循环 (ReAct Loop)
            # ==========================================================
            MAX_TURNS = 20  # 防御性编程：防止大模型死循环，最多允许执行20步
            
            for turn in range(MAX_TURNS):
                print(f"🔄 [Agent 思考轮次 {turn + 1}]...")
                
                response = await llm_client.chat.completions.create(
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

if __name__ == "__main__":
    asyncio.run(run_deepcontext_agent())