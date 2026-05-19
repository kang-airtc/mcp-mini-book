# 第07章 Resource与Prompt实现

<!-- status: writing -->

上一章把 5 个 Tool 接上后,Server 已具备执行动作的能力。本章给 Server 补上数据资源(2 个 Resource)与提示模板(2 个 Prompt)两类能力,完成整个 Server 的能力面。

Resource 与 Prompt 在实现复杂度上比 Tool 简单,但设计层面的考量更多,同一份数据,做成 Tool 还是 Resource?同一类分析任务,Prompt 是否要点名具体 Tool?这些选择直接影响 Agent 工作流的稳定性与灵活性。

读完本章,读者将理解 Resource 的 URI 设计原则、`@mcp.resource()` 与 `@mcp.prompt()` 装饰器的工作机制,以及 Prompt 模板的两种典型形态。

## 7.1 Resource的URI设计

为什么有些能力适合做成 Tool、有些适合做成 Resource?核心区分点在触发方与内容性质。Tool 由模型自动调用,语义偏向动作;Resource 由用户主动选择,语义偏向数据。一份汇总报告,既可以做成 Tool(让模型自动生成),也可以做成 Resource(让用户主动附加到对话)。两种实现的 SQL 与业务逻辑甚至完全相同,差别只在装饰器和心智模型。

本书示例选择把“工单列表”与“汇总报告”做成 Resource,理由有二。其一,这两类内容更像参考资料而非动作产出,在 Agent 工作流中,用户可能希望主动决定何时把它们带入上下文,而非由模型自行触发。其二,工单列表数据量较大,若做成 Tool 会被频繁拉取,占用大量上下文 token;做成 Resource 则把“何时引入”的决策权交回用户,模型只在用户明确附加时才看到这份数据。

Resource 通过 URI 标识。URI scheme 可以借用通用约定(`file://`、`https://`),也可以自定义业务化 scheme。本书使用 `tickets://`,自定义 scheme 的好处是:URI 在 Client 端展示时一目了然,不会与文件资源混淆;同时给 Server 内部留出灵活路由的空间,同一个 `tickets://` 前缀下可以挂载多种格式的资源。本书示例提供两个 Resource:

- `tickets://list`,以 JSON 格式输出全部工单列表,作为结构化数据
- `tickets://report`,以 Markdown 格式输出汇总报告,作为人类可读资料

这一拆分把结构化数据与分析报告两类内容分开,模型与用户都能按需取用。

> 注意:Resource 不会被模型自动调用。Client 在初始化时通过 `resources/list` 拿到 Resource 清单后,通常显示在宿主程序的“附加上下文”按钮里供用户挑选。如果希望某份数据由模型主动获取,应该实现为 Tool,而不是 Resource。

## 7.2 实现tickets://list资源

`@mcp.resource(uri)` 装饰器把函数注册为 Resource。URI 作为装饰器的位置参数,函数返回字符串作为该 URI 的内容。`tickets://list` 的实现先连接数据库,执行一次全量查询:

```python
@mcp.resource("tickets://list")
def get_all_tickets() -> str:
    """获取所有工单列表(作为 Resource)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_no, customer_name, issue_type, priority, status, subject, created_at
        FROM tickets
        ORDER BY created_at DESC
    """)
```

SELECT 字段与第 06 章的 `query_tickets_by_status` 完全一致,同样省略 `description` 等大文本字段,只返回列表场景需要的核心元信息。查询完成后把结果序列化为 JSON 返回:

```python
    rows = cursor.fetchall()
    tickets = [dict(row) for row in rows]
    conn.close()

    return json.dumps(tickets, ensure_ascii=False, indent=2)
```

对比第 06 章 Tool 的实现,Resource 的代码几乎只是把 `@mcp.tool()` 换成 `@mcp.resource(uri)`,业务函数本身完全一致。这种刻意的对称是 FastMCP 的设计哲学:同一份业务函数,改一行装饰器就能切换能力类型。开发者在初期可以先把所有能力都写成 Tool,后续根据使用反馈再把不应由模型自动调用的能力迁移为 Resource,迁移成本极低。

有一点需要提醒:本书的 `tickets://list` 是全量副本式资源,每次调用都把工单全部内容序列化返回。对于大量数据的生产场景,应该考虑分页或链接式资源(返回的内容是子资源 URI 而非数据本身)。MCP 协议在这方面尚有演进空间,本书示例不展开。

## 7.3 实现tickets://report报告资源

`tickets://report` 与 `tickets://list` 的关键差异在内容性质:前者是 Markdown 格式的人类可读报告,后者是 JSON 结构化数据。这一对比有助于读者理解 `mimeType` 字段在 MCP 中的作用,Client 拿到资源后会根据 mimeType 决定渲染方式(JSON 进结构化视图,Markdown 进富文本视图)。`tickets://report` 的实现先做三次聚合查询,把数据准备好:

```python
@mcp.resource("tickets://report")
def get_summary_report() -> str:
    """获取工单数据汇总报告(作为 Resource)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tickets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    status_data = cursor.fetchall()

    cursor.execute("SELECT issue_type, COUNT(*) FROM tickets GROUP BY issue_type")
    type_data = cursor.fetchall()

    conn.close()
```

三次聚合分别取总数、按状态分布、按类型分布,所有 SQL 在函数内一次性完成后立即关闭连接,避免长连接占用。接下来用普通字符串拼接生成 Markdown 报告:

```python
    report = "# 电商工单数据分析报告\n\n## 数据概览\n"
    report += f"- **总工单数**: {total} 个\n\n## 工单状态分布\n"

    status_label = {
        "open": "待处理", "in_progress": "处理中",
        "resolved": "已解决", "closed": "已关闭",
    }
    for status, count in status_data:
        percentage = (count / total) * 100
        report += f"- {status_label.get(status, status)}: {count} 个 ({percentage:.1f}%)\n"

    # 类型分布与分析建议部分略,完整代码见 agent-mcp-demo/mcp_server.py
    return report
```

字符串拼接的写法适合本书这种小报告。生产场景中如果报告结构复杂、维度繁多,建议改用 Jinja2 模板把内容与展示分离;本书示例为了让读者一目了然,选择不引入额外模板依赖。`status_label` 字典把数据库字段的英文枚举翻译成中文标签,这一步对最终读者(用户或模型)的可读性影响显著,Resource 输出涉及枚举值时通常都要做这层映射。

## 7.4 Prompt模板的两种典型形态

本书示例提供两个 Prompt:`analyze_priority_tickets`(高优先级工单分析)与 `customer_satisfaction_analysis`(客户满意度分析)。两者的提示词模式不同,代表 Prompt 设计的两种典型形态,指令型与探索型。先看第一个,采用指令型写法:

```python
@mcp.prompt()
def analyze_priority_tickets() -> str:
    """分析高优先级工单的提示模板"""
    return """请分析当前所有高优先级工单的情况:

1. 列出所有 status 为 open 或 in_progress 且 priority 为 high 的工单
2. 分析这些工单的主要问题类型
3. 给出处理建议

请使用 query_tickets_by_status 工具获取数据,然后进行分析。"""
```

这段 Prompt 有三个值得注意的设计要点。其一,把多步指令明确编号,便于模型按顺序执行;其二,直接点名要用 `query_tickets_by_status` 这一具体 Tool,降低模型在 Tool 选择上的不确定性;其三,最后一句“获取数据,然后进行分析”明确切分“读”与“想”两个阶段,避免模型在拿到数据前先编结论。

第二个 Prompt 采用探索型写法,不点名具体 Tool:

```python
@mcp.prompt()
def customer_satisfaction_analysis() -> str:
    """客户满意度分析提示模板"""
    return """请分析客户满意度情况:

1. 查看已解决工单的满意度评分分布
2. 计算平均满意度
3. 分析低满意度工单的原因
4. 提出改进建议

请使用相关工具获取统计数据并进行分析。"""
```

第二个 Prompt 与第一个的差异:文末改为“请使用相关工具”。这是有意为之,本任务所需的 Tool 组合并不固定,可能是 `get_ticket_statistics` 与 `analyze_resolution_time` 组合,也可能再加上 `get_ticket_detail` 来看某条低分工单的具体描述。硬指定具体 Tool 反而会限制模型的决策空间。

两种写法对应两类 Prompt 设计哲学。指令型 Prompt 适合工作流单一、Tool 链路固定的场景,精度高、稳定;探索型 Prompt 适合工作流可变、需要模型自行编排的场景,灵活、覆盖广。一个成熟的 MCP Server 通常会同时提供这两类 Prompt,前者作为“标准操作流程”,后者作为“开放式分析入口”,由用户按业务诉求选择。

至此 5 个 Tool、2 个 Resource、2 个 Prompt 全部实现完毕,Server 端的能力面已经齐全。但能力只是“声明”,只有当 Client 把这些能力调起来,整套链路才真正闭环。下一章进入 Client 端实战,演示从会话初始化、能力发现到具体调用的完整流程。
