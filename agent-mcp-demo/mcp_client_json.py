#!/usr/bin/env python3
"""
MCP Client 示例 (JSON 格式版本 - Streamable HTTP)
调用 MCP Server 并解析 {code, msg, data} 格式的响应
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


def parse_response(text: str) -> dict:
    """解析 {code, msg, data} 格式的 JSON 响应"""
    try:
        result = json.loads(text)
        if isinstance(result, dict) and "code" in result:
            return result
        else:
            # 非标准格式，包装一下
            return {"code": 200, "msg": "success", "data": result}
    except json.JSONDecodeError:
        return {"code": 500, "msg": f"JSON解析失败: {text[:100]}", "data": None}


def print_response(result: dict, title: str = ""):
    """打印标准格式响应"""
    if title:
        print(f"\n{title}")

    code = result.get("code", 0)
    msg = result.get("msg", "")
    data = result.get("data")

    if code == 200:
        print(f"✅ [{code}] {msg}")
        if data:
            if isinstance(data, list):
                print(f"📊 数据条数: {len(data)}")
                for i, item in enumerate(data[:5], 1):  # 只显示前5条
                    print(f"  [{i}] {json.dumps(item, ensure_ascii=False)}")
                if len(data) > 5:
                    print(f"  ... 还有 {len(data) - 5} 条数据")
            elif isinstance(data, dict):
                print(f"📊 数据内容:")
                for key, value in data.items():
                    print(f"  • {key}: {value}")
            else:
                print(f"📊 数据: {data}")
    else:
        print(f"❌ [{code}] {msg}")


async def run_client():
    """运行 MCP Client 示例"""

    print("=" * 60)
    print("🚀 MCP Client 演示 (JSON 格式版本 - Streamable HTTP)")
    print("响应格式: {code, msg, data}")
    print("Server: http://localhost:8001/mcp")
    print("=" * 60)

    # 建立 HTTP 连接
    print("\n📡 正在连接 MCP Server (Streamable HTTP)...")
    async with streamable_http_client(url="http://localhost:8001/mcp") as (
        read,
        write,
        session_id_callback,
    ):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            print("✅ 连接成功！\n")

            # 列出可用 Tools
            print("-" * 60)
            print("📋 可用 Tools (返回 {code, msg, data} 格式):")
            print("-" * 60)
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  • {tool.name}")

            # ========================================
            # 1. 调用 Tool: 获取工单统计
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 1: 调用 Tool - 获取工单统计概览")
            print("=" * 60)

            result = await session.call_tool("get_ticket_statistics", {})
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "📊 统计结果:")

            # ========================================
            # 2. 调用 Tool: 查询特定状态的工单
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 2: 调用 Tool - 查询 'in_progress' 状态的工单")
            print("=" * 60)

            result = await session.call_tool(
                "query_tickets_by_status", {"status": "in_progress"}
            )
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "📋 查询结果:")

            # ========================================
            # 3. 调用 Tool: 查询特定类型的工单
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 3: 调用 Tool - 查询 '退款申请' 类型工单")
            print("=" * 60)

            result = await session.call_tool(
                "query_tickets_by_type", {"issue_type": "退款申请"}
            )
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "📋 查询结果:")

            # ========================================
            # 4. 调用 Tool: 获取工单详情
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 4: 调用 Tool - 获取单个工单详情 (TK2024001)")
            print("=" * 60)

            result = await session.call_tool(
                "get_ticket_detail", {"ticket_no": "TK2024001"}
            )
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "📄 工单详情:")

            # ========================================
            # 5. 调用 Tool: 分析解决时间
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 5: 调用 Tool - 分析工单解决时间")
            print("=" * 60)

            result = await session.call_tool("analyze_resolution_time", {})
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "⏱️  解决时间分析:")

            # ========================================
            # 6. 调用 Tool: 获取所有工单
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 6: 调用 Tool - 获取所有工单列表")
            print("=" * 60)

            result = await session.call_tool("get_all_tickets", {})
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "📋 工单列表:")

            # ========================================
            # 7. 读取 Resource: 工单列表
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 7: 读取 Resource - tickets://list")
            print("=" * 60)

            resource = await session.read_resource("tickets://list")
            if resource.contents:
                content = resource.contents[0]
                if hasattr(content, "text"):
                    response = parse_response(content.text)
                    print_response(response, "📁 资源内容:")

            # ========================================
            # 8. 测试不存在的工单
            # ========================================
            print("\n" + "=" * 60)
            print("🎯 示例 8: 测试 - 查询不存在的工单 (TK9999999)")
            print("=" * 60)

            result = await session.call_tool(
                "get_ticket_detail", {"ticket_no": "TK9999999"}
            )
            for content in result.content:
                if content.type == "text":
                    response = parse_response(content.text)
                    print_response(response, "📄 查询结果:")

            print("\n" + "=" * 60)
            print("✅ 所有示例执行完毕！")
            print("=" * 60)


if __name__ == "__main__":
    # 运行异步客户端
    asyncio.run(run_client())
