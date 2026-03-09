# Nanobot 项目深度学习指南（修正版）

## 目录

1. [项目概述](#1-项目概述)
2. [核心架构（修正版）](#2-核心架构修正版)
3. [消息总线 (Message Bus)](#3-消息总线-message-bus)
4. [Agent 核心循环](#4-agent-核心循环)
5. [上下文构建器](#5-上下文构建器)
6. [工具系统](#6-工具系统)
7. [会话管理](#7-会话管理)
8. [记忆系统](#8-记忆系统)
9. [渠道模块](#9-渠道模块)
10. [LLM 提供商](#10-llm-提供商)
11. [配置系统](#11-配置系统)
12. [CLI 命令行](#12-cli-命令行)
13. [定时任务与心跳服务](#13-定时任务与心跳服务)
14. [学习路线与实践](#14-学习路线与实践)

---

## 1. 项目概述

### 1.1 项目简介

**Nanobot** 是由香港大学开发的超轻量级个人 AI 助手框架，核心代码仅约 **4000 行**，比同类项目 OpenClaw 少 99% 的代码量。

**技术栈：**
- Python 3.11+
- 异步框架：asyncio
- CLI 框架：Typer
- 数据验证：Pydantic
- LLM 统一接口：LiteLLM
- 日志：Loguru

### 1.2 核心特性

- **多渠道支持**：Telegram、Discord、WhatsApp、飞书、钉钉、Slack、QQ、Email、Matrix、Mochat
- **多模型支持**：通过 LiteLLM 支持 100+ LLM 模型
- **工具系统**：文件系统、Shell 执行、Web 搜索、定时任务、MCP 集成
- **记忆系统**：短期会话记忆 + 长期记忆 (MEMORY.md/HISTORY.md)
- **技能系统**：动态加载自定义技能
- **定时任务**：Cron 定时执行任务
- **心跳服务**：周期性唤醒 Agent 检查任务

---

## 2. 核心架构（修正版）

### 2.1 整体架构图（修正）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLI 入口层 (commands.py)                        │
│                   nanobot agent / nanobot gateway                      │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              │ 2. 创建并初始化
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          配置层 (config/)                               │
│                    Config → Provider / Channels                        │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   MessageBus    │ │   Provider      │ │  SessionManager │
│   (消息总线)    │ │   (LLM 提供商)  │ │   (会话管理)    │
│                 │ │                 │ │                 │
│ inbound Queue  │ │ LiteLLM /      │ │ session/*.jsonl │
│ outbound Queue │ │ Azure / Codex   │ └─────────────────┘
└────────┬────────┘ └─────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────────────┐     ┌─────────────────┐
│   AgentLoop     │     │  ChannelManager │
│  (核心处理引擎) │     │    (渠道管理)   │
│                 │     │                 │
│ - ContextBuilder│     │ - Telegram      │
│ - ToolRegistry  │     │ - Discord       │
│ - MemoryStore   │     │ - WhatsApp      │
│ - SubagentMgr   │     │ - Feishu        │
│ - SkillsLoader  │     │ - ...           │
└────────┬────────┘     └────────┬────────┘
         │                      │
         │ MessageBus            │ MessageBus
         │ outbound             │ inbound
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     并行运行的服务 (asyncio.gather)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ AgentLoop    │  │ ChannelMgr   │  │ CronService  │  │ Heartbeat  │ │
│  │   .run()     │  │ .start_all() │  │   .start()   │  │  .start()  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 消息流向图（修正）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            消息流向                                      │
└─────────────────────────────────────────────────────────────────────────┘

用户消息流程：
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  用户    │───▶│ Channel  │───▶│ inbound  │───▶│AgentLoop │───▶│ outbound │
│          │    │ (Telegram│    │  Queue   │    │  处理    │    │  Queue   │
└──────────┘    │ Discord) │    │          │    │          │    └────┬─────┘
                └──────────┘    └──────────┘    └────┬─────┘         │
                                                    │                │
                              ┌──────────────────────┘                │
                              ▼                                       ▼
                    ┌──────────────────┐                 ┌──────────────────┐
                    │  LLM (Provider)  │                 │     Channel     │
                    │   + Tools        │                 │  (发送回复)     │
                    └──────────────────┘                 └──────────────────┘
                                                              │
                                                              ▼
                                                       ┌──────────┐
                                                       │   用户   │
                                                       └──────────┘
```

### 2.3 模块结构（修正）

```
nanobot/
├── __main__.py           # 入口点: python -m nanobot
├── __init__.py           # 版本信息
├── cli/                  # CLI 入口 ★★★
│   └── commands.py       # Typer 命令 (agent, gateway, onboard, channels)
├── config/               # 配置模块
│   ├── __init__.py
│   ├── loader.py        # 配置加载器
│   ├── paths.py         # 路径配置
│   └── schema.py        # Pydantic 配置模型 ★★
├── bus/                  # 消息总线 ★★★
│   ├── events.py         # 消息事件定义 (InboundMessage, OutboundMessage)
│   └── queue.py          # MessageBus (asyncio.Queue)
├── agent/                # Agent 核心模块 ★★★
│   ├── loop.py           # AgentLoop 核心循环引擎
│   ├── context.py        # ContextBuilder 上下文构建
│   ├── memory.py         # MemoryStore 记忆系统
│   ├── skills.py         # SkillsLoader 技能加载
│   ├── subagent.py       # SubagentManager 子代理管理
│   └── tools/            # 工具模块
│       ├── base.py       # Tool 基类
│       ├── registry.py   # ToolRegistry 工具注册表
│       ├── filesystem.py # 文件读写工具
│       ├── shell.py      # Shell 执行工具
│       ├── web.py        # Web 搜索/获取
│       ├── message.py    # 消息发送
│       ├── cron.py       # 定时任务工具
│       ├── spawn.py      # 子进程启动
│       └── mcp.py        # MCP 集成
├── channels/             # 渠道模块
│   ├── base.py          # BaseChannel 基类
│   ├── manager.py        # ChannelManager 渠道管理器 ★★
│   ├── telegram.py       # Telegram 渠道
│   ├── discord.py        # Discord 渠道
│   ├── whatsapp.py       # WhatsApp 渠道
│   ├── feishu.py         # 飞书渠道
│   ├── dingtalk.py       # 钉钉渠道
│   ├── slack.py          # Slack 渠道
│   ├── qq.py             # QQ 渠道
│   ├── email.py          # Email 渠道
│   ├── matrix.py         # Matrix 渠道
│   └── mochat.py         # Mochat 渠道
├── providers/            # LLM 提供商模块 ★★
│   ├── base.py           # LLMProvider 基类
│   ├── litellm_provider.py # LiteLLM 提供商 (支持 100+ 模型)
│   ├── registry.py       # Provider 注册表
│   ├── azure_openai_provider.py
│   ├── openai_codex_provider.py
│   ├── custom_provider.py
│   └── transcription.py
├── session/              # 会话管理模块 ★★
│   ├── __init__.py
│   └── manager.py       # Session / SessionManager
├── cron/                 # 定时任务模块
│   ├── service.py       # CronService ★★
│   └── types.py
├── heartbeat/            # 心跳服务模块 ★★
│   ├── __init__.py
│   └── service.py       # HeartbeatService
├── skills/               # 内置技能
├── templates/            # 模板文件
└── utils/               # 工具函数
```

---

## 3. 消息总线 (Message Bus)

### 3.1 核心代码

**文件位置：** `nanobot/bus/queue.py`

```python
class MessageBus:
    """异步消息总线，解耦聊天渠道与 Agent 核心"""

    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()

    async def publish_inbound(self, msg: InboundMessage):
        """发布入站消息（渠道 -> Agent）"""
        await self.inbound.put(msg)

    async def publish_outbound(self, msg: OutboundMessage):
        """发布出站消息（Agent -> 渠道）"""
        await self.outbound.put(msg)

    async def consume_inbound(self) -> InboundMessage:
        """消费入站消息"""
        return await self.inbound.get()

    async def consume_outbound(self) -> OutboundMessage:
        """消费出站消息"""
        return await self.outbound.get()
```

### 3.2 消息事件定义

**文件位置：** `nanobot/bus/events.py`

```python
@dataclass
class InboundMessage:
    """入站消息：用户 -> 渠道 -> MessageBus -> Agent"""
    channel: str              # 渠道名称 (telegram, discord, etc.)
    sender_id: str            # 发送者 ID
    chat_id: str              # 聊天 ID (会话标识)
    content: str              # 消息内容
    media: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    session_key_override: str | None = None

@dataclass
class OutboundMessage:
    """出站消息：Agent -> MessageBus -> 渠道 -> 用户"""
    channel: str
    chat_id: str
    content: str
    media: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

### 3.3 设计要点

1. **异步队列**：使用 `asyncio.Queue` 实现真正的异步处理
2. **解耦架构**：渠道模块与 Agent 核心不直接通信，通过 MessageBus 中转
3. **双向队列**：
   - inbound：用户消息从渠道流向 Agent
   - outbound：Agent 回复从 Agent 流向渠道

---

## 4. Agent 核心循环

### 4.1 AgentLoop 核心逻辑

**文件位置：** `nanobot/agent/loop.py`

AgentLoop 是整个系统的核心引擎，负责：
1. 接收并处理消息
2. 构建上下文
3. 调用 LLM
4. 执行工具调用
5. 管理会话

```python
class AgentLoop:
    def __init__(
        self,
        bus: MessageBus,
        provider: LLMProvider,
        workspace: Path,
        model: str | None = None,
        max_iterations: int = 40,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        memory_window: int = 100,
        # ... 其他参数
    ):
        self.bus = bus
        self.provider = provider
        self.workspace = workspace
        self.max_iterations = max_iterations

        # 初始化组件
        self.context = ContextBuilder(workspace)
        self.sessions = session_manager or SessionManager(workspace)
        self.tools = ToolRegistry()
        self.subagents = SubagentManager(...)
```

### 4.2 并行运行机制

在 `gateway` 命令中，所有服务并行启动：

```python
async def run():
    await cron.start()           # 定时任务服务
    await heartbeat.start()      # 心跳服务
    await asyncio.gather(
        agent.run(),             # Agent 循环
        channels.start_all(),    # 渠道管理
    )
```

### 4.3 核心循环流程

```python
async def _run_agent_loop(self, initial_messages, on_progress=None):
    """Agent 迭代循环"""
    messages = initial_messages

    while iteration < self.max_iterations:
        # 1. 调用 LLM
        response = await self.provider.chat(
            messages=messages,
            tools=self.tools.get_definitions(),
            ...
        )

        # 2. 处理工具调用
        if response.has_tool_calls:
            for tool_call in response.tool_calls:
                result = await self.tools.execute(tool_call.name, tool_call.arguments)
                messages = self.context.add_tool_result(...)
        else:
            # 3. 最终响应
            final_content = response.content
            break

    return final_content
```

---

## 5. 上下文构建器

### 5.1 ContextBuilder

**文件位置：** `nanobot/agent/context.py`

```python
class ContextBuilder:
    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md"]

    def build_system_prompt(self, skill_names=None) -> str:
        """构建系统提示词"""
        parts = []
        parts.append(self._get_identity())           # nanobot 身份
        parts.append(self._load_bootstrap_files()) # 引导文件
        parts.append(self.memory.get_memory_context()) # 长期记忆
        parts.append(self.skills.get_always_skills()) # 技能
        return "\n\n---\n\n".join(parts)

    def build_messages(self, history, current_message, ...):
        """构建完整的消息列表"""
        return [
            {"role": "system", "content": self.build_system_prompt()},
            *history,
            {"role": "user", "content": current_message},
        ]
```

---

## 6. 工具系统

### 6.1 工具架构

```
ToolRegistry (工具注册表)
    │
    ├── Tool 基类 (base.py)
    │       ├── name: str
    │       ├── description: str
    │       ├── parameters: dict (JSON Schema)
    │       └── execute(**kwargs) -> str
    │
    ├── ReadFileTool
    ├── WriteFileTool
    ├── EditFileTool
    ├── ListDirTool
    ├── ExecTool
    ├── WebSearchTool
    ├── WebFetchTool
    ├── MessageTool
    ├── CronTool
    ├── SpawnTool
    └── MCPTool
```

### 6.2 ToolRegistry

```python
class ToolRegistry:
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_definitions(self) -> list[dict]:
        """获取所有工具定义（OpenAI 格式）"""
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found."
        params = tool.cast_params(params)
        errors = tool.validate_params(params)
        if errors:
            return f"Error: Invalid parameters..."
        return await tool.execute(**params)
```

---

## 7. 会话管理

### 7.1 Session 数据结构

```python
@dataclass
class Session:
    key: str                    # channel:chat_id
    messages: list[dict]        # 消息列表
    created_at: datetime
    updated_at: datetime
    last_consolidated: int = 0  # 已整合的消息数
```

### 7.2 SessionManager

```python
class SessionManager:
    def __init__(self, workspace: Path):
        self.sessions_dir = workspace / "sessions"
        self._cache: dict[str, Session] = {}

    def get_or_create(self, key: str) -> Session:
        if key in self._cache:
            return self._cache[key]
        session = self._load(key) or Session(key=key)
        self._cache[key] = session
        return session

    def save(self, session: Session) -> None:
        """保存会话到 JSONL 文件"""
```

---

## 8. 记忆系统

### 8.1 双层记忆架构

```
┌─────────────────────────────────────────┐
│         MemoryStore (两层记忆)           │
├─────────────────────────────────────────┤
│ Layer 1: 短期记忆                        │
│ - Session.messages                       │
│ - 保留最近 N 条消息                      │
├─────────────────────────────────────────┤
│ Layer 2: 长期记忆                        │
│ - MEMORY.md (长期事实)                   │
│ - HISTORY.md (可搜索历史)                │
└─────────────────────────────────────────┘
```

### 8.2 记忆整合流程

```python
async def consolidate(self, session, provider, model, ...):
    """将旧消息整合到长期记忆"""

    # 1. 获取待整合的消息
    old_messages = session.messages[session.last_consolidated:-keep_count]

    # 2. 调用 LLM 生成记忆
    response = await provider.chat(
        messages=[...],
        tools=_SAVE_MEMORY_TOOL,  # save_memory 工具
        model=model,
    )

    # 3. 保存记忆
    if response.has_tool_calls:
        args = response.tool_calls[0].arguments
        self.append_history(args["history_entry"])   # HISTORY.md
        self.write_long_term(args["memory_update"])  # MEMORY.md
```

---

## 9. 渠道模块

### 9.1 BaseChannel 基类

```python
class BaseChannel(ABC):
    name: str = "base"

    def __init__(self, config: Any, bus: MessageBus):
        self.config = config
        self.bus = bus

    @abstractmethod
    async def start(self) -> None: pass

    @abstractmethod
    async def stop(self) -> None: pass

    @abstractmethod
    async def send(self, msg: OutboundMessage) -> None: pass

    async def _handle_message(self, sender_id, chat_id, content, ...):
        """处理收到的消息，发送到 MessageBus"""
        if not self.is_allowed(sender_id):
            return
        await self.bus.publish_inbound(InboundMessage(...))
```

### 9.2 ChannelManager

```python
class ChannelManager:
    def __init__(self, config: Config, bus: MessageBus):
        self.channels: dict[str, BaseChannel] = {}
        self._init_channels()

    async def start_all(self) -> None:
        # 启动出站分发器
        self._dispatch_task = asyncio.create_task(self._dispatch_outbound())
        # 启动所有渠道
        await asyncio.gather(*[c.start() for c in self.channels.values()])

    async def _dispatch_outbound(self) -> None:
        """分发出站消息到对应渠道"""
        while True:
            msg = await self.bus.consume_outbound()
            channel = self.channels.get(msg.channel)
            if channel:
                await channel.send(msg)
```

### 9.3 渠道对比

| 渠道 | 通信方式 | 依赖库 |
|------|----------|--------|
| Telegram | Webhook/Long Polling | python-telegram-bot |
| Discord | WebSocket Gateway | slack-sdk |
| WhatsApp | WebSocket (Baileys) | Node.js bridge |
| 飞书 | WebSocket | lark-oapi |
| 钉钉 | Stream Mode | dingtalk-stream |
| Slack | Socket Mode | slack-sdk |
| QQ | WebSocket | botpy |
| Email | IMAP/SMTP | 内置 |
| Matrix | WebSocket | matrix-nio |
| Mochat | Socket.IO | python-socketio |

---

## 10. LLM 提供商

### 10.1 LLMProvider 基类

```python
@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    finish_reason: str = "stop"
    reasoning_content: str | None = None
    thinking_blocks: list[dict] | None = None

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages, tools=None, model=None, ...):
        """发送聊天完成请求"""
        pass
```

### 10.2 LiteLLM Provider

```python
class LiteLLMProvider(LLMProvider):
    """使用 LiteLLM 的统一接口"""

    async def chat(self, messages, tools=None, model=None, ...):
        # 1. 解析模型名称
        resolved_model = self._resolve_model(model)

        # 2. 处理消息和工具
        messages = self._sanitize_messages(messages)

        # 3. 调用 LiteLLM
        response = await acompletion(
            model=resolved_model,
            messages=messages,
            tools=tools,
            ...
        )

        return self._parse_response(response)
```

---

## 11. 配置系统

### 11.1 配置模型（Pydantic）

```python
class TelegramConfig(Base):
    enabled: bool = False
    token: str = ""
    allow_from: list[str] = Field(default_factory=list)

class Config(Base):
    version: int = 1
    workspace: Path = Path("~/.nanobot")
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    channels: ChannelsConfig = Field(default_factory=ChannelsConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
```

---

## 12. CLI 命令行

### 12.1 CLI 命令

```python
app = typer.Typer(name="nanobot")

@app.command()
def agent():
    """启动 CLI 交互模式"""

@app.command()
def gateway(port=18790, workspace=None, config=None):
    """启动网关（连接渠道）"""

@app.command()
def onboard():
    """初始化配置"""

@app.command()
def channels():
    """渠道管理命令"""
```

### 12.2 Gateway 启动流程

```python
def gateway(...):
    # 1. 加载配置
    config = _load_runtime_config(config, workspace)

    # 2. 创建核心组件
    bus = MessageBus()
    provider = _make_provider(config)
    session_manager = SessionManager(workspace)
    cron = CronService(...)
    agent = AgentLoop(bus=bus, provider=provider, ...)
    channels = ChannelManager(config, bus)
    heartbeat = HeartbeatService(...)

    # 3. 并行启动
    async def run():
        await cron.start()
        await heartbeat.start()
        await asyncio.gather(
            agent.run(),
            channels.start_all(),
        )
    asyncio.run(run())
```

---

## 13. 定时任务与心跳服务

### 13.1 CronService

```python
class CronService:
    """定时任务服务"""

    def __init__(self, store_path: Path, on_job=None):
        self.store_path = store_path
        self.on_job = on_job  # 回调：执行任务

    async def start(self) -> None:
        """启动定时任务调度"""

    async def on_cron_job(job: CronJob) -> str | None:
        """通过 Agent 执行任务"""
        return await agent.process_direct(
            job.payload.message,
            session_key=f"cron:{job.id}",
            channel=job.payload.channel,
            chat_id=job.payload.to,
        )
```

### 13.2 HeartbeatService

```python
class HeartbeatService:
    """周期性心跳服务"""

    def __init__(self, workspace, provider, model, on_execute=None, ...):
        self.workspace = workspace
        self.provider = provider
        self.on_execute = on_execute  # 回调：执行任务

    async def start(self) -> None:
        """启动心跳服务"""

    async def on_heartbeat_execute(tasks: str) -> str:
        """通过 Agent 执行任务"""
        return await agent.process_direct(
            tasks,
            session_key="heartbeat",
            channel=channel,
            chat_id=chat_id,
        )
```

---

## 14. 学习路线与实践

### 14.1 推荐学习顺序

| 阶段 | 模块 | 核心文件 | 重点内容 |
|------|------|----------|----------|
| 1 | CLI 入口 | `cli/commands.py` | gateway 启动流程 |
| 2 | 消息总线 | `bus/queue.py`, `bus/events.py` | 异步队列、消息定义 |
| 3 | Agent 核心 | `agent/loop.py` | 核心循环、工具调用 |
| 4 | 上下文 | `agent/context.py` | System Prompt、消息构建 |
| 5 | 工具系统 | `agent/tools/base.py`, `registry.py` | 工具接口、注册、执行 |
| 6 | 会话管理 | `session/manager.py` | 会话持久化、JSONL |
| 7 | 记忆系统 | `agent/memory.py` | 记忆整合、HISTORY/MEMORY |
| 8 | 渠道基类 | `channels/base.py`, `manager.py` | 渠道接口、消息路由 |
| 9 | 定时任务 | `cron/service.py` | CronService |
| 10 | 心跳服务 | `heartbeat/service.py` | HeartbeatService |
| 11 | LLM Provider | `providers/base.py`, `litellm_provider.py` | 多模型支持 |

### 14.2 修正说明

**原架构图问题：**

1. ~~CLI 放在"核心层"~~ → CLI 是入口层，启动 gateway 命令
2. ~~AgentLoop 调用 Channels~~ → 通过 MessageBus 通信，对等关系
3. ~~Provider 指向 Channels~~ → Provider 只被 AgentLoop 使用
4. ~~缺少 Cron/Heartbeat~~ → 需要体现它们通过 AgentLoop.process_direct() 执行任务

---

*本文档基于 nanobot v0.1.4.post4 版本生成*
