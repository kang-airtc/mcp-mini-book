#!/usr/bin/env python3
"""
电商工单数据分析 MCP Server
使用 FastMCP 框架构建，提供 SQLite 数据服务
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("电商工单数据分析服务")

# 数据库路径
DB_PATH = Path("tickets.db")


def init_database():
    """初始化数据库并创建示例数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建工单表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_no TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT,
            issue_type TEXT NOT NULL,
            priority TEXT NOT NULL,  -- high, medium, low
            status TEXT NOT NULL,    -- open, in_progress, resolved, closed
            subject TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            satisfaction_score INTEGER  -- 1-5 满意度评分
        )
    """)

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM tickets")
    if cursor.fetchone()[0] == 0:
        # 插入示例数据
        sample_data = [
            (
                "TK2024001",
                "张三",
                "zhangsan@email.com",
                "退款申请",
                "high",
                "resolved",
                "订单未收到货要求退款",
                "客户在3天前下单但物流显示异常",
                "2024-01-15 09:30:00",
                "2024-01-15 14:20:00",
                5,
            ),
            (
                "TK2024002",
                "李四",
                "lisi@email.com",
                "商品质量问题",
                "medium",
                "in_progress",
                "收到的商品有破损",
                "包装盒完好但内部商品破损",
                "2024-01-15 10:15:00",
                None,
                None,
            ),
            (
                "TK2024003",
                "王五",
                "wangwu@email.com",
                "物流查询",
                "low",
                "open",
                "查询订单物流状态",
                "订单显示已发货但3天未更新物流",
                "2024-01-15 11:00:00",
                None,
                None,
            ),
            (
                "TK2024004",
                "赵六",
                "zhaoliu@email.com",
                "发票申请",
                "medium",
                "resolved",
                "申请开具增值税发票",
                "需要开具公司抬头的专票",
                "2024-01-14 16:45:00",
                "2024-01-15 09:00:00",
                4,
            ),
            (
                "TK2024005",
                "钱七",
                "qianqi@email.com",
                "退货申请",
                "high",
                "in_progress",
                "尺码不合适需要退货",
                "购买的鞋子尺码偏小需要换货",
                "2024-01-15 13:20:00",
                None,
                None,
            ),
            (
                "TK2024006",
                "孙八",
                "sunba@email.com",
                "账户问题",
                "low",
                "closed",
                "无法登录账户",
                "忘记密码且手机号已更换",
                "2024-01-13 10:00:00",
                "2024-01-13 11:30:00",
                5,
            ),
            (
                "TK2024007",
                "周九",
                "zhoujiu@email.com",
                "退款申请",
                "medium",
                "open",
                "重复扣款问题",
                "同一订单被扣款两次",
                "2024-01-15 15:00:00",
                None,
                None,
            ),
            (
                "TK2024008",
                "吴十",
                "wushi@email.com",
                "商品咨询",
                "low",
                "resolved",
                "询问商品规格",
                "想了解某款手机的详细参数",
                "2024-01-15 08:00:00",
                "2024-01-15 08:30:00",
                5,
            ),
            (
                "TK2024009",
                "郑一",
                "zhengyi@email.com",
                "投诉建议",
                "high",
                "in_progress",
                "客服态度投诉",
                "对上次客服处理结果不满意",
                "2024-01-15 16:00:00",
                None,
                None,
            ),
            (
                "TK2024010",
                "陈二",
                "chener@email.com",
                "物流查询",
                "medium",
                "resolved",
                "快递显示已签收但未收到",
                "可能是快递柜或代收点",
                "2024-01-14 14:20:00",
                "2024-01-15 10:00:00",
                4,
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO tickets 
            (ticket_no, customer_name, customer_email, issue_type, priority, status, 
             subject, description, created_at, resolved_at, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sample_data,
        )

        conn.commit()
        print(f"✅ 已创建示例数据库，包含 {len(sample_data)} 条工单记录")

    conn.close()


@mcp.tool()
def query_tickets_by_status(status: str) -> str:
    """
    按状态查询工单

    Args:
        status: 工单状态 (open:待处理, in_progress:处理中, resolved:已解决, closed:已关闭)

    Returns:
        JSON格式的工单列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

    return json.dumps(tickets, ensure_ascii=False, indent=2)


@mcp.tool()
def query_tickets_by_type(issue_type: str) -> str:
    """
    按问题类型查询工单

    Args:
        issue_type: 问题类型，如：退款申请、商品质量问题、物流查询等

    Returns:
        JSON格式的工单列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

    return json.dumps(tickets, ensure_ascii=False, indent=2)


@mcp.tool()
def get_ticket_statistics() -> str:
    """
    获取工单统计概览

    Returns:
        包含各类统计数据的JSON
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 按状态统计
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM tickets 
        GROUP BY status
    """)
    status_stats = {row[0]: row[1] for row in cursor.fetchall()}

    # 按类型统计
    cursor.execute("""
        SELECT issue_type, COUNT(*) as count 
        FROM tickets 
        GROUP BY issue_type
    """)
    type_stats = {row[0]: row[1] for row in cursor.fetchall()}

    # 按优先级统计
    cursor.execute("""
        SELECT priority, COUNT(*) as count 
        FROM tickets 
        GROUP BY priority
    """)
    priority_stats = {row[0]: row[1] for row in cursor.fetchall()}

    # 平均满意度
    cursor.execute("""
        SELECT AVG(satisfaction_score) 
        FROM tickets 
        WHERE satisfaction_score IS NOT NULL
    """)
    avg_satisfaction = cursor.fetchone()[0] or 0

    # 今日新增
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT COUNT(*) FROM tickets WHERE DATE(created_at) = ?
    """,
        (today,),
    )
    today_count = cursor.fetchone()[0]

    conn.close()

    stats = {
        "总计工单数": sum(status_stats.values()),
        "今日新增": today_count,
        "按状态分布": status_stats,
        "按类型分布": type_stats,
        "按优先级分布": priority_stats,
        "平均满意度": round(avg_satisfaction, 2),
    }

    return json.dumps(stats, ensure_ascii=False, indent=2)


@mcp.tool()
def get_ticket_detail(ticket_no: str) -> str:
    """
    获取单个工单的详细信息

    Args:
        ticket_no: 工单编号，如：TK2024001

    Returns:
        工单详细信息JSON
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM tickets WHERE ticket_no = ?
    """,
        (ticket_no,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return json.dumps(dict(row), ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": f"未找到工单 {ticket_no}"}, ensure_ascii=False)


@mcp.tool()
def analyze_resolution_time() -> str:
    """
    分析工单解决时间（仅统计已解决的工单）

    Returns:
        解决时间分析结果
    """
    conn = sqlite3.connect(DB_PATH)
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
            "已解决工单数": row[3],
            "平均解决时间": f"{row[0] * 24:.1f} 小时",
            "最长解决时间": f"{row[1] * 24:.1f} 小时",
            "最短解决时间": f"{row[2] * 24:.1f} 小时",
        }
    else:
        analysis = {"message": "暂无已解决的工单数据"}

    return json.dumps(analysis, ensure_ascii=False, indent=2)


@mcp.resource("tickets://list")
def get_all_tickets() -> str:
    """
    获取所有工单列表（作为Resource）

    Returns:
        JSON格式的所有工单列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_no, customer_name, issue_type, priority, status, subject, created_at
        FROM tickets 
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    tickets = [dict(row) for row in rows]
    conn.close()

    return json.dumps(tickets, ensure_ascii=False, indent=2)


@mcp.resource("tickets://report")
def get_summary_report() -> str:
    """
    获取工单数据汇总报告（作为Resource）

    Returns:
        Markdown格式的报告
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 统计数据
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
    """
    分析高优先级工单的提示模板
    """
    return """请分析当前所有高优先级工单的情况：

1. 列出所有 status 为 open 或 in_progress 且 priority 为 high 的工单
2. 分析这些工单的主要问题类型
3. 给出处理建议

请使用 query_tickets_by_status 工具获取数据，然后进行分析。"""


@mcp.prompt()
def customer_satisfaction_analysis() -> str:
    """
    客户满意度分析提示模板
    """
    return """请分析客户满意度情况：

1. 查看已解决工单的满意度评分分布
2. 计算平均满意度
3. 分析低满意度工单的原因
4. 提出改进建议

请使用相关工具获取统计数据并进行分析。"""


if __name__ == "__main__":
    # 初始化数据库
    init_database()

    # 启动 MCP Server
    print("🚀 启动电商工单数据分析 MCP Server...")
    print("支持的 Tools:")
    print("  - query_tickets_by_status: 按状态查询工单")
    print("  - query_tickets_by_type: 按类型查询工单")
    print("  - get_ticket_statistics: 获取统计概览")
    print("  - get_ticket_detail: 获取工单详情")
    print("  - analyze_resolution_time: 分析解决时间")
    print("\n支持的 Resources:")
    print("  - tickets://list: 所有工单列表")
    print("  - tickets://report: 数据汇总报告")
    print("\n支持的 Prompts:")
    print("  - analyze_priority_tickets: 高优先级工单分析")
    print("  - customer_satisfaction_analysis: 客户满意度分析")
    print("\n" + "=" * 50)

    mcp.run()
