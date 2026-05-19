#!/usr/bin/env python3
"""
电商工单数据分析 MCP Server (JSON 格式版本)
使用 FastMCP 框架，Tool 返回格式: {"code": 200, "msg": "...", "data": ...}
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("电商工单数据分析服务-JSON格式")

# 数据库路径
DB_PATH = Path("tickets.db")


def make_response(code: int = 200, msg: str = "success", data: Any = None) -> str:
    """统一响应格式"""
    return json.dumps(
        {"code": code, "msg": msg, "data": data}, ensure_ascii=False, indent=2
    )


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def query_tickets_by_status(status: str) -> str:
    """按状态查询工单

    Args:
        status: 工单状态 (open, in_progress, resolved, closed)

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": [...]}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT ticket_no, customer_name, issue_type, priority, status, subject, created_at
            FROM tickets 
            WHERE status = ?
            ORDER BY created_at DESC
        """,
            (status,),
        )

        rows = cursor.fetchall()
        tickets = [dict(row) for row in rows]
        conn.close()

        return make_response(
            code=200,
            msg=f"找到 {len(tickets)} 个状态为 '{status}' 的工单",
            data=tickets,
        )
    except Exception as e:
        return make_response(code=500, msg=f"查询失败: {str(e)}", data=None)


@mcp.tool()
def query_tickets_by_type(issue_type: str) -> str:
    """按问题类型查询工单

    Args:
        issue_type: 问题类型 (如: 退款申请, 商品质量问题等)

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": [...]}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT ticket_no, customer_name, priority, status, subject, created_at
            FROM tickets 
            WHERE issue_type = ?
            ORDER BY created_at DESC
        """,
            (issue_type,),
        )

        rows = cursor.fetchall()
        tickets = [dict(row) for row in rows]
        conn.close()

        return make_response(
            code=200,
            msg=f"找到 {len(tickets)} 个类型为 '{issue_type}' 的工单",
            data=tickets,
        )
    except Exception as e:
        return make_response(code=500, msg=f"查询失败: {str(e)}", data=None)


@mcp.tool()
def get_ticket_statistics() -> str:
    """获取工单统计概览

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": {...}}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
        status_stats = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT issue_type, COUNT(*) FROM tickets GROUP BY issue_type")
        type_stats = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
        priority_stats = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(
            "SELECT AVG(satisfaction_score) FROM tickets WHERE satisfaction_score IS NOT NULL"
        )
        avg_satisfaction = cursor.fetchone()[0] or 0

        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE DATE(created_at) = ?", (today,)
        )
        today_count = cursor.fetchone()[0]

        conn.close()

        stats = {
            "total": sum(status_stats.values()),
            "today_new": today_count,
            "by_status": status_stats,
            "by_type": type_stats,
            "by_priority": priority_stats,
            "avg_satisfaction": round(avg_satisfaction, 2),
        }

        return make_response(code=200, msg="获取统计信息成功", data=stats)
    except Exception as e:
        return make_response(code=500, msg=f"获取统计信息失败: {str(e)}", data=None)


@mcp.tool()
def get_ticket_detail(ticket_no: str) -> str:
    """获取单个工单的详细信息

    Args:
        ticket_no: 工单编号

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": {...}}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets WHERE ticket_no = ?", (ticket_no,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return make_response(code=200, msg="获取工单详情成功", data=dict(row))
        else:
            return make_response(code=404, msg=f"未找到工单 {ticket_no}", data=None)
    except Exception as e:
        return make_response(code=500, msg=f"查询失败: {str(e)}", data=None)


@mcp.tool()
def analyze_resolution_time() -> str:
    """分析工单解决时间

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": {...}}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                AVG(julianday(resolved_at) - julianday(created_at)) as avg_days,
                MAX(julianday(resolved_at) - julianday(created_at)) as max_days,
                MIN(julianday(resolved_at) - julianday(created_at)) as min_days,
                COUNT(*) as resolved_count
            FROM tickets 
            WHERE resolved_at IS NOT NULL
        """)

        row = cursor.fetchone()
        conn.close()

        if row and row[3] > 0:
            analysis = {
                "resolved_count": row[3],
                "avg_hours": round(row[0] * 24, 1),
                "max_hours": round(row[1] * 24, 1),
                "min_hours": round(row[2] * 24, 1),
            }
            return make_response(code=200, msg="解决时间分析成功", data=analysis)
        else:
            return make_response(
                code=200,
                msg="暂无已解决的工单数据",
                data={"resolved_count": 0, "message": "暂无数据"},
            )
    except Exception as e:
        return make_response(code=500, msg=f"分析失败: {str(e)}", data=None)


@mcp.tool()
def get_all_tickets() -> str:
    """获取所有工单列表

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": [...]}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ticket_no, customer_name, issue_type, priority, status, subject, created_at
            FROM tickets 
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        tickets = [dict(row) for row in rows]
        conn.close()

        return make_response(
            code=200, msg=f"获取工单列表成功，共 {len(tickets)} 条", data=tickets
        )
    except Exception as e:
        return make_response(code=500, msg=f"获取工单列表失败: {str(e)}", data=None)


@mcp.resource("tickets://list")
def get_all_tickets_resource() -> str:
    """获取所有工单列表 (Resource)

    Returns:
        JSON字符串: {"code": 200, "msg": "...", "data": [...]}
    """
    return get_all_tickets()


@mcp.resource("tickets://report")
def get_summary_report() -> str:
    """获取工单数据汇总报告 (Resource)

    Returns:
        Markdown格式的报告
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tickets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    status_data = cursor.fetchall()

    cursor.execute("SELECT issue_type, COUNT(*) FROM tickets GROUP BY issue_type")
    type_data = cursor.fetchall()

    conn.close()

    report = f"""# 电商工单数据分析报告

## 数据概览
- **总工单数**: {total} 个

## 工单状态分布
"""

    for status, count in status_data:
        percentage = (count / total) * 100
        status_label = {
            "open": "待处理",
            "in_progress": "处理中",
            "resolved": "已解决",
            "closed": "已关闭",
        }.get(status, status)
        report += f"- {status_label}: {count} 个 ({percentage:.1f}%)\n"

    report += "\n## 问题类型分布\n"
    for issue_type, count in type_data:
        report += f"- {issue_type}: {count} 个\n"

    report += """
## 分析建议
- 关注高优先级工单的处理效率
- 退款和质量问题占比较高，建议优化商品质量和退款流程
- 物流相关问题较多，建议与物流公司沟通改进
"""

    return report


@mcp.prompt()
def analyze_priority_tickets() -> str:
    """分析高优先级工单的提示模板"""
    return """请分析当前所有高优先级工单的情况：

1. 列出所有 status 为 open 或 in_progress 且 priority 为 high 的工单
2. 分析这些工单的主要问题类型
3. 给出处理建议

请使用 query_tickets_by_status 工具获取数据，然后进行分析。"""


@mcp.prompt()
def customer_satisfaction_analysis() -> str:
    """客户满意度分析提示模板"""
    return """请分析客户满意度情况：

1. 查看已解决工单的满意度评分分布
2. 计算平均满意度
3. 分析低满意度工单的原因
4. 提出改进建议

请使用相关工具获取统计数据并进行分析。"""


if __name__ == "__main__":
    print("🚀 启动电商工单数据分析 MCP Server (JSON 格式)...")
    print('\n返回格式: {"code": 200, "msg": "...", "data": ...}')
    print("\n可用 Tools:")
    print("  • query_tickets_by_status")
    print("  • query_tickets_by_type")
    print("  • get_ticket_statistics")
    print("  • get_ticket_detail")
    print("  • analyze_resolution_time")
    print("  • get_all_tickets")
    print("\n" + "=" * 50)

    mcp.run(transport="streamable-http", port=8001, path="/mcp")
