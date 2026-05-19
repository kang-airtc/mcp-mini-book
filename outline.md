# Agent MCP实战小册——大纲

## 定位

- 篇幅:约 35 页,小五号字体、每页约 40~45 行
- 章节:10 章,平均 3~4 页/章
- 配比:理论 3:实践 7;贯穿案例为电商工单数据分析 MCP Server
- 源码:`agent-mcp-demo/` 目录已有完整可运行实现

## 章节结构

### 第 01 章 MCP协议的定位与价值(3 页)

- 1.1 协议的由来与诞生背景
- 1.2 MCP与Function Calling的关系
- 1.3 MCP在Agent生态中要解决的问题

含图 1-1。理论章,为后续九章的实战打基础。

### 第 02 章 三大核心概念:Resources、Tools、Prompts(4 页)

- 2.1 Resources:面向AI的上下文数据
- 2.2 Tools:可被AI自动调用的功能
- 2.3 Prompts:用户触发的提示模板
- 2.4 三者的协作关系与典型工作流

含图 2-1、表 2-1。

### 第 03 章 传输层:stdio、HTTP/SSE与JSON-RPC(3 页)

- 3.1 协议骨架:JSON-RPC 2.0
- 3.2 stdio传输:基于子进程的本地通信
- 3.3 HTTP/SSE传输:面向网络服务的双向流
- 3.4 三种模式的工程取舍

含图 3-1、表 3-1。

### 第 04 章 开发环境与项目骨架(3 页)

- 4.1 Python虚拟环境与依赖隔离
- 4.2 FastMCP框架的核心抽象
- 4.3 工程目录约定

实战起点,从空白工程到能 import fastmcp。

### 第 05 章 数据层设计:SQLite工单库(3 页)

- 5.1 业务场景:电商工单分析
- 5.2 表结构与字段语义
- 5.3 样例数据与初始化函数

含图 5-1。

### 第 06 章 Tool能力实现(4 页)

- 6.1 Tool装饰器与签名约定
- 6.2 统计与详情类Tool
- 6.3 查询类Tool
- 6.4 分析类Tool:解决时间分布

含图 6-1、表 6-1。本章对应 `mcp_server.py` 中 5 个 `@mcp.tool()` 函数。

### 第 07 章 Resource与Prompt实现(4 页)

- 7.1 Resource的URI设计
- 7.2 实现tickets://list资源
- 7.3 实现tickets://report报告资源
- 7.4 Prompt模板的两种典型形态

对应 `mcp_server.py` 中 2 个 `@mcp.resource()` 与 2 个 `@mcp.prompt()`。

### 第 08 章 stdio客户端实战(3 页)

- 8.1 Client的生命周期与会话初始化
- 8.2 列出能力清单
- 8.3 调用Tool与读取Resource
- 8.4 完整链路联调

含图 8-1。对应 `mcp_client.py`。

### 第 09 章 HTTP/SSE模式改造与多客户端(4 页)

- 9.1 stdio到HTTP/SSE的迁移动机
- 9.2 基于Starlette与Uvicorn的Server实现
- 9.3 SSE端点的双向消息流
- 9.4 HTTP Client的长连接处理

含图 9-1。对应 `mcp_server_http.py` 与 `mcp_client_http.py`。

### 第 10 章 接入OpenCode与调试排错(4 页)

- 10.1 opencode.json的MCP配置
- 10.2 local与remote两种接入形态
- 10.3 启动与连接类故障排查
- 10.4 协议与业务类异常排查

含图 10-1、表 10-1。本章把前九章成果接进真实 Agent 宿主。

## 图表清单

图 1-1、2-1、3-1、5-1、6-1、8-1、9-1、10-1 共 8 张。
表 2-1、3-1、6-1、10-1 共 4 张。

## 写作约束

- 遵循 `../tech-book-tools/config/writing_style.yaml` 与 `book_style.yaml`
- 遵循 `../tech-book-tools/config/content_policy.yaml` 内容红线
- 术语首次出现给出英文全拼,如 Model Context Protocol(模型上下文协议,MCP)
- 不使用反问标题、不使用"本章介绍"等模板句式
- 代码块单段不超过 30 行,关键处分段并插入解释
