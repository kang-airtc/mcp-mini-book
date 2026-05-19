# 第04章 开发环境与项目骨架

<!-- status: writing -->

前三章把 MCP 的定位、能力模型、传输层逐一交代清楚,本章进入实战准备阶段,从空白目录开始,把开发环境搭起来。

环境层面只关注三件事:依赖如何隔离、FastMCP 框架的最小心智模型是什么、四个核心 Python 文件如何在工程里组织。读完本章,读者将拥有一个空但完整的 MCP 项目骨架,能够 `import fastmcp` 成功,具备进入后续六章实战的前置条件。

本章不再赘述 Python 基础;只讨论 MCP 项目特有的环境约定与目录布局。

## 4.1 Python虚拟环境与依赖隔离

Python 项目需要把依赖与系统全局 Python 隔离开,这是基本卫生。MCP Server 在生产场景中通常会被多个 Client 同时接入,任何依赖错配都会被放大暴露:一旦 Server 端的某个底层依赖被全局 pip 升级搞坏,所有接入它的 Client 都会受影响。本机开发阶段就把环境隔离这件事做规范,后续部署会省下大量调试时间。

Python 自 3.3 起内置 `venv` 模块用于创建虚拟环境。本书示例工程的初始化命令如下:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

第一行在当前目录下创建 `venv/` 子目录,内含独立的 Python 解释器与 site-packages;第二行激活该环境,激活后 `pip install` 安装的依赖只会进入 `venv/lib/...`,不污染系统 Python(Windows 系统的激活命令为 `venv\Scripts\activate`);第三行按 `requirements.txt` 安装项目依赖。

`requirements.txt` 文件本身极简,只有两行:

```text
fastmcp
mcp
```

两个包构成 MCP Python 开发的最小依赖集。`fastmcp` 是 Server 侧的高层框架,`mcp` 是协议规范的 Python SDK,提供 Client 侧的会话与传输能力。HTTP/SSE 模式底层依赖 Starlette 与 Uvicorn,但 FastMCP 会将它们作为传递依赖自动拉取,`requirements.txt` 不必显式声明。

生产部署中应通过 `pip freeze > requirements.txt` 锁定具体版本号(例如 `fastmcp==X.Y.Z`),以防协议升级导致的不兼容。本书示例不锁定版本,方便读者跟进 SDK 最新演进,但读者在自己的项目中应按上述方式锁版本。

> 注意:激活 venv(`source venv/bin/activate`)是 `pip install` 进入隔离环境的前提。如果忘记激活就跑 `pip install`,依赖会装到系统 Python,污染全局环境。后续在第 10 章接入 OpenCode 时,启动命令中也需要显式指向 venv 内的 Python 解释器,否则会出现“本机能跑、宿主报 ImportError”的典型问题。

## 4.2 FastMCP框架的核心抽象

FastMCP 是 Python 生态下的高层 MCP 框架,目标是把“实现一个 Tool”简化到“写一个普通 Python 函数加一行装饰器”。框架内部封装了 JSON-RPC 编解码、传输层多路复用、参数 schema 自动推导等繁琐工作,业务代码只需关注三件事:函数签名、类型注解、文档字符串。

FastMCP 暴露三个核心装饰器,分别对应上一章讲过的 Resources、Tools、Prompts。以工单分析服务的最小骨架为例:

```python
import json
from fastmcp import FastMCP

mcp = FastMCP("电商工单数据分析服务")


@mcp.tool()
def query_tickets_by_status(status: str) -> str:
    """按状态查询工单"""
    # 业务逻辑见第 06 章
    return json.dumps([], ensure_ascii=False)


@mcp.resource("tickets://list")
def get_all_tickets() -> str:
    """获取所有工单列表"""
    return json.dumps([], ensure_ascii=False)


@mcp.prompt()
def analyze_priority_tickets() -> str:
    """分析高优先级工单的提示模板"""
    return "请分析当前所有高优先级工单..."


if __name__ == "__main__":
    mcp.run()
```

三个装饰器的工作机制各有不同。`@mcp.tool()` 把普通函数注册为 MCP Tool:函数名变为 Tool 名,docstring 变为 description,类型注解推导出 `inputSchema`,返回值会被序列化为 content 字段。`@mcp.resource(uri)` 注册一个 Resource,装饰器的位置参数是该资源的 URI(本例使用业务化的 `tickets://` scheme)。`@mcp.prompt()` 注册 Prompt 模板,函数返回值作为提示词正文。

文件末尾的 `mcp.run()` 是整个 Server 的入口。无参调用时 FastMCP 默认走 stdio 传输,从 stdin 读取请求、向 stdout 写响应。切换到 HTTP/SSE 只需传入 transport 参数:`mcp.run(transport="streamable-http", port=8000, path="/mcp")`。业务代码不需要任何改动,这一便利在第 09 章会再次用到。

## 4.3 工程目录约定

本书示例工程的目录布局非常扁平,在根目录下放置四个核心 Python 文件加少量配置:

```text
agent-mcp-demo/
├── mcp_server.py          # stdio 模式 Server
├── mcp_client.py          # stdio 模式 Client
├── mcp_server_http.py     # HTTP/SSE 模式 Server
├── mcp_client_http.py     # HTTP/SSE 模式 Client
├── tickets.db             # SQLite 数据库(运行时自动创建)
├── requirements.txt       # Python 依赖
└── venv/                  # 虚拟环境(不入版本控制)
```

扁平结构适合学习场景:每个文件单一职责,便于读者把 stdio 版与 HTTP/SSE 版做横向对照。`mcp_server.py` 与 `mcp_server_http.py` 暴露的 Tool/Resource/Prompt 集合完全相同,差别仅在最后一行 `mcp.run()` 的传输参数。这种刻意保持的对称,有助于读者从 stdio 平滑迁移到 HTTP/SSE。

四个核心 Python 文件各自独立运行。`mcp_server.py` 直接 `python3 mcp_server.py` 启动,Server 进入 stdio 监听;`mcp_client.py` 运行时会自动 fork `mcp_server.py` 子进程,不必手动启动 Server。HTTP/SSE 模式则需要分别打开两个终端:先 `python3 mcp_server_http.py` 启动 Server,再 `python3 mcp_client_http.py` 连接。

生产场景的目录约定会更复杂,通常按业务模块拆分,把 `tools/`、`resources/`、`prompts/` 分别建子模块,通过 `__init__.py` 集中向 `mcp` 实例注册。本书示例选择单文件结构,纯粹是为了让读者能在一屏内看完一个 Server 的全部能力。读者在迁移到自己的项目时,按需调整即可。

环境与骨架准备到位,下一步是设计数据层。本书贯穿案例是电商工单数据分析,数据由 SQLite 承载。下一章把表结构、字段语义、初始化函数交代清楚,作为后续 Tool 与 Resource 实现的数据基底。
