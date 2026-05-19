# MCP 示例项目 - 电商工单数据分析

## 项目说明

这是一个使用 MCP (Model Context Protocol) 构建的示例项目，演示了两种通信方式：

### 版本对比

| 文件 | 通信方式 | 适用场景 |
|------|----------|----------|
| `mcp_server.py` + `mcp_client.py` | **stdio** (标准输入输出) | 本地工具、命令行应用 |
| `mcp_server_http.py` + `mcp_client_http.py` | **HTTP/SSE** | Web 服务、远程调用、多客户端支持 |

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

---

## 方式一：stdio 模式（本地进程通信）

### 运行 Server

```bash
python mcp_server.py
```

Server 启动后会自动创建 SQLite 数据库并等待连接。

### 运行 Client

在另一个终端窗口：

```bash
python mcp_client.py
```

Client 通过 stdio 启动 Server 子进程并通信。

---

## 方式二：HTTP/SSE 模式（网络服务）

### 启动 HTTP Server

```bash
python mcp_server_http.py
```

Server 会在 `http://localhost:8000` 启动：
- MCP Endpoint: `http://localhost:8000/mcp` (支持 GET/SSE 和 POST)

### 运行 HTTP Client

在另一个终端窗口：

```bash
python mcp_client_http.py
```

Client 通过 HTTP/SSE 连接到 Server。

---

## 功能说明

两个版本的 Server 提供相同的功能：

### Tools (工具)

- `get_ticket_statistics` - 获取工单统计概览
- `query_tickets_by_status` - 按状态查询工单
- `query_tickets_by_type` - 按类型查询工单
- `get_ticket_detail` - 获取工单详情
- `analyze_resolution_time` - 分析解决时间

### Resources (资源)

- `tickets://list` - 所有工单列表（JSON）
- `tickets://report` - 数据汇总报告（Markdown）

### Prompts (提示)

- `analyze_priority_tickets` - 高优先级工单分析模板
- `customer_satisfaction_analysis` - 满意度分析模板

---

## 示例数据

数据库包含 10 条示例工单，涵盖：
- 退款申请
- 商品质量问题
- 物流查询
- 发票申请
- 退货申请
- 账户问题
- 投诉建议

---

## 通信方式对比

### stdio 模式

```
┌─────────┐     stdin/stdout      ┌─────────┐
│ Client  │◄────────────────────►│ Server  │
└─────────┘   (子进程通信)         └─────────┘

特点：
✓ 简单易用，适合本地工具
✓ 自动启动/停止 Server
✗ 仅支持单机
✗ 不支持多客户端
```

### HTTP/SSE 模式

```
┌─────────┐     HTTP POST     ┌─────────┐
│ Client1 │◄────────────────►│         │
├─────────┤     SSE Stream    │  Server │
│ Client2 │◄────────────────►│  :8000  │
├─────────┤                   │         │
│ Client3 │◄────────────────►│         │
└─────────┘                   └─────────┘

特点：
✓ 支持多客户端同时连接
✓ 可远程部署
✓ 支持流式推送（SSE）
✓ 适合 Web 应用
✗ 需要单独启动 Server
```

---

## 技术栈

- **Python 3.8+**
- **FastMCP** - MCP Server 框架
- **MCP Python SDK** - MCP Client/Server 库
- **Starlette** - HTTP 服务框架（HTTP 版本）
- **Uvicorn** - ASGI 服务器（HTTP 版本）
- **SQLite** - 本地数据库

---

## 调试

### stdio 模式问题

```bash
# 先单独启动 Server 看是否正常
python mcp_server.py

# 检查依赖
pip list | grep -E "(mcp|fastmcp)"
```

### HTTP 模式问题

```bash
# 检查 Server 是否运行在 8000 端口
curl http://localhost:8000/sse

# 查看 Server 日志
python mcp_server_http.py
```

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `mcp_server.py` | stdio 模式 MCP Server |
| `mcp_client.py` | stdio 模式 MCP Client |
| `mcp_server_http.py` | HTTP/SSE 模式 MCP Server |
| `mcp_client_http.py` | HTTP/SSE 模式 MCP Client |
| `tickets.db` | SQLite 数据库（自动创建） |
| `requirements.txt` | Python 依赖 |
| `学习笔记.md` | MCP 学习笔记 |

---

## 参考

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/modelcontextprotocol/python-sdk)
- [SSE (Server-Sent Events)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
