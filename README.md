# Agent MCP 实战小册

作者：**亢AIRTC**

请关注 B站 [光谷老亢](https://space.bilibili.com/394612055) 视频教程，学习更多 AI、RTC 等知识。

---

## 简介

本书以「电商工单分析服务」为贯穿案例，用 FastMCP 与 SQLite 从零构建一个可被 OpenCode 直接接入的 MCP Server，把 MCP 协议从「概念听过」推进到「真的能跑起来」：

- MCP 协议的定位、价值与 Function Calling 的关系
- Resources、Tools、Prompts 三大核心能力
- stdio、HTTP/SSE 与 JSON-RPC 三种传输模式
- FastMCP 框架的核心抽象与工程目录约定
- SQLite 工单库设计、5 个 Tool、2 个 Resource、2 个 Prompt
- stdio 与 HTTP/SSE 两种客户端实战
- 接入 OpenCode 与真实 AI 工作流，并完成调试排错

读者跟随章节动手，最终得到一份能在终端 AI 助手里被自动调用的 MCP Server。

## 目录

| 章节 | 标题 | 内容简介 |
|------|------|---------|
| 第01章 | MCP 协议的定位与价值 | 协议诞生背景，与 Function Calling 的关系，在 Agent 生态中要解决的问题 |
| 第02章 | 三大核心概念：Resources、Tools、Prompts | 三类能力的定位、典型用法与协作关系 |
| 第03章 | 传输层：stdio、HTTP/SSE 与 JSON-RPC | JSON-RPC 2.0 协议骨架，stdio 与 HTTP/SSE 两种传输的工程取舍 |
| 第04章 | 开发环境与项目骨架 | Python venv 依赖隔离、FastMCP 核心抽象、工程目录约定 |
| 第05章 | 数据层设计：SQLite 工单库 | 电商工单场景、表结构与字段语义、样例数据与初始化函数 |
| 第06章 | Tool 能力实现 | Tool 装饰器与签名约定，统计 / 查询 / 分析三类 Tool 实现 |
| 第07章 | Resource 与 Prompt 实现 | Resource URI 设计、`tickets://` 资源、两类 Prompt 模板形态 |
| 第08章 | stdio 客户端实战 | Client 生命周期、能力清单获取、Tool 调用与 Resource 读取的端到端联调 |
| 第09章 | HTTP/SSE 模式改造与多客户端 | 基于 Starlette/Uvicorn 改造 Server，SSE 双向消息流，多 Client 共享 |
| 第10章 | 接入 OpenCode 与调试排错 | `opencode.json` 配置、local/remote 接入形态、启动与协议层故障排查 |

## 配套源码

- **本书源码**：[https://github.com/kang-airtc/mcp-mini-book](https://github.com/kang-airtc/mcp-mini-book)
- Demo 代码在 `agent-mcp-demo/` 目录：
  - `mcp_server.py` / `mcp_server_http.py` / `mcp_server_json.py` —— 三种传输模式的 Server 实现
  - `mcp_client.py` / `mcp_client_http.py` / `mcp_client_json.py` —— 对应的 Client 实现
  - `tickets.db` —— 工单示例数据库
  - `opencode.json` —— OpenCode 接入配置

## 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.10+ |
| FastMCP | 最新版 |
| SQLite | Python 内置 |
| OpenCode（可选） | 用于第10章接入演示 |

## 快速开始

```bash
# 1. 准备 Python 环境
cd agent-mcp-demo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 启动 stdio 模式 Server + Client（第8章）
python mcp_client.py

# 3. 启动 HTTP/SSE 模式（第9章）
python mcp_server_http.py
# 另开终端
python mcp_client_http.py
```

接入 OpenCode 与全链路调试方法详见第10章。
