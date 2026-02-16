"""
DeepContext 主程序入口
启动 MCP Server 或 Agent Client
"""

import asyncio
import sys
import argparse
from core.agent import DeepContextAgent


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="DeepContext - 智能知识管理系统")
    parser.add_argument(
        "--mode", 
        choices=["server", "agent"], 
        default="agent",
        help="运行模式: server (启动 MCP Server) 或 agent (启动 Agent Client)"
    )
    parser.add_argument(
        "--query", 
        type=str, 
        help="Agent 模式下的用户查询"
    )
    return parser.parse_args()


async def run_agent(query=None):
    """运行 Agent 客户端"""
    agent = DeepContextAgent()
    await agent.run(query)


def run_server():
    """运行 MCP Server"""
    import subprocess
    print("🚀 启动 DeepContext MCP Server...")
    subprocess.run([sys.executable, "server.py"])


def main():
    """主函数"""
    args = parse_args()
    
    if args.mode == "server":
        run_server()
    elif args.mode == "agent":
        asyncio.run(run_agent(args.query))


if __name__ == "__main__":
    main()