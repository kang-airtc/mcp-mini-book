#!/usr/bin/env python3
"""
MCP Client 示例 - 调用电商工单数据分析服务
演示如何连接 MCP Server 并调用 Tools、Resources 和 Prompts
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_client():
    """运行 MCP Client 示例"""

    print("=" * 60)
    print("🚀 MCP Client 演示 - 电商工单数据分析")
    print("=" * 60)

    # 配置 Server 参数（通过 stdio 启动 server）
    server_params = StdioServerParameters(
        command="python3", args=["mcp_server.py"], env=None
    )

    # 建立连接
    print("\n📡 正在连接 MCP Server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            print("✅ 连接成功！\n")

            # 获取 Server 能力信息
            print("-" * 60)
            print("📋 Server 能力概览")
            print("-" * 60)

            # 列出可用 Tools
            print("\n🔧 可用 Tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")

            # 列出可用 Resources
            print("\n📁 可用 Resources:")
            resources = await session.list_resources()
            for resource in resources.resources:
                print(f"  • {resource.uri}: {resource.name}")

            # 列出可用 Prompts
            print("\n💬 可用 Prompts:")
            prompts = await session.list_prompts()
            for prompt in prompts.prompts:
                print(f"  • {prompt.name}: {prompt.description}")

            # ========================================
            # 1. 调用 Tool: 获取工单统计
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 1: 调用 Tool - 获取工单统计概览")
            print("=" * 60)

            result = await session.call_tool("get_ticket_statistics", {})
            print("\n📊 调用结果:")
            for content in result.content:
                if content.type == "text":
                    stats = json.loads(content.text)
                    print(json.dumps(stats, ensure_ascii=False, indent=2))

            # ========================================
            # 2. 调用 Tool: 查询特定状态的工单
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 2: 调用 Tool - 查询 '处理中' 状态的工单")
            print("=" * 60)

            result = await session.call_tool(
                "query_tickets_by_status", {"status": "in_progress"}
            )
            print("\n📋 查询结果:")
            for content in result.content:
                if content.type == "text":
                    tickets = json.loads(content.text)
                    print(f"找到 {len(tickets)} 个处理中的工单:\n")
                    for ticket in tickets:
                        print(f"  工单号: {ticket['ticket_no']}")
                        print(f"  客户: {ticket['customer_name']}")
                        print(f"  问题: {ticket['subject']}")
                        print(f"  优先级: {ticket['priority']}")
                        print("-" * 40)

            # ========================================
            # 3. 调用 Tool: 查询特定类型的工单
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 3: 调用 Tool - 查询 '退款申请' 类型工单")
            print("=" * 60)

            result = await session.call_tool(
                "query_tickets_by_type", {"issue_type": "退款申请"}
            )
            print("\n📋 查询结果:")
            for content in result.content:
                if content.type == "text":
                    tickets = json.loads(content.text)
                    print(f"找到 {len(tickets)} 个退款申请工单:\n")
                    for ticket in tickets:
                        print(f"  工单号: {ticket['ticket_no']}")
                        print(f"  客户: {ticket['customer_name']}")
                        print(f"  状态: {ticket['status']}")
                        print(f"  主题: {ticket['subject']}")
                        print()

            # ========================================
            # 4. 调用 Tool: 获取工单详情
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 4: 调用 Tool - 获取单个工单详情 (TK2024001)")
            print("=" * 60)

            result = await session.call_tool(
                "get_ticket_detail", {"ticket_no": "TK2024001"}
            )
            print("\n📄 工单详情:")
            for content in result.content:
                if content.type == "text":
                    detail = json.loads(content.text)
                    print(json.dumps(detail, ensure_ascii=False, indent=2))

            # ========================================
            # 5. 调用 Tool: 分析解决时间
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 5: 调用 Tool - 分析工单解决时间")
            print("=" * 60)

            result = await session.call_tool("analyze_resolution_time", {})
            print("\n⏱️  解决时间分析:")
            for content in result.content:
                if content.type == "text":
                    analysis = json.loads(content.text)
                    print(json.dumps(analysis, ensure_ascii=False, indent=2))

            # ========================================
            # 6. 读取 Resource: 工单列表
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 6: 读取 Resource - 获取所有工单列表")
            print("=" * 60)

            resource = await session.read_resource("tickets://list")
            print("\n📁 资源内容 (前3条):")
            if resource.contents:
                content = resource.contents[0]
                if hasattr(content, "text"):
                    tickets = json.loads(content.text)
                    for i, ticket in enumerate(tickets[:3], 1):
                        print(f"\n  [{i}] 工单 {ticket['ticket_no']}")
                        print(f"      客户: {ticket['customer_name']}")
                        print(f"      类型: {ticket['issue_type']}")
                        print(f"      状态: {ticket['status']}")

            # ========================================
            # 7. 读取 Resource: 汇总报告
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 7: 读取 Resource - 获取数据汇总报告")
            print("=" * 60)

            resource = await session.read_resource("tickets://report")
            print("\n📊 报告内容:")
            if resource.contents:
                content = resource.contents[0]
                if hasattr(content, "text"):
                    print(content.text)

            # ========================================
            # 8. 获取 Prompt: 高优先级工单分析
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 8: 获取 Prompt - 高优先级工单分析模板")
            print("=" * 60)

            prompt = await session.get_prompt("analyze_priority_tickets", {})
            print("\n💬 Prompt 内容:")
            if prompt.messages:
                for msg in prompt.messages:
                    print(f"\n角色: {msg.role}")
                    if hasattr(msg.content, "text"):
                        print(f"内容:\n{msg.content.text}")

            # ========================================
            # 9. 获取 Prompt: 满意度分析
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 9: 获取 Prompt - 客户满意度分析模板")
            print("=" * 60)

            prompt = await session.get_prompt("customer_satisfaction_analysis", {})
            print("\n💬 Prompt 内容:")
            if prompt.messages:
                for msg in prompt.messages:
                    print(f"\n角色: {msg.role}")
                    if hasattr(msg.content, "text"):
                        print(f"内容:\n{msg.content.text}")

            print("\n" + "=" * 60)
            print("✅ 所有示例执行完毕！")
            print("=" * 60)


if __name__ == "__main__":
    # 运行异步客户端
    asyncio.run(run_client())
