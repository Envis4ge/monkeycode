# Nanobot 项目深度学习指南

## 目录

1. [项目概述](#1-项目概述)
2. [核心架构](#2-核心架构)
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
13. [学习路线与实践](#13-学习路线与实践)

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

---

## 2. 核心架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI / Gateway                           │
│                    (nanobot agent / gateway)                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        MessageBus (消息总线)                     │
│                 (asyncio.Queue 异步消息队列)                    │
│  ┌─────────────────────┐          ┌─────────────────────────┐  │
│  │   inbound Queue    │          │    outbound Queue      │  │
│  │  (入站消息队列)    │          │    (出站消息队列)       │  │
│  └─────────┬───────────┘          └───────────┬─────────────┘  │
└────────────┼─────────────────────────────────────┼──────────────┘
             │                                     │
    ┌────────▼────────┐                   ┌────────▼────────┐
    │    Channels    │                   │    Channels    │
    │   (接收消息)   │                   │   (发送消息)   │
    └───────┬────────┘                   └───────┬────────┘
            │                                     │
┌───────────▼─────────────────────────────────────▼──────────────┐
│                      AgentLoop (代理循环引擎)                    │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ ContextBuilder│  │ ToolRegistry│  │  SessionManager     │  │
│  │ (上下文构建)  │  │ (工具注册)  │  │    (会话管理)       │  │
│  └──────────────┘  └────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  MemoryStore │  │ SubagentMgr │  │    SkillsLoader     │  │
│  │  (记忆存储)  │  │ (子代理管理) │  │    (技能加载)       │  │
│  └──────────────┘  └────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  LLMProvider      │
                    │  (LLM 提供商)     │
                    └───────────────────┘
```

### 2.2 模块结构

```
nanobot/
├── __main__.py           # 入口点
├── __init__.py           # 版本信息
├── agent/                # Agent 核心模块
│   ├── __init__.py
│   ├── loop.py           # AgentLoop 核心循环 ★★★
│   ├── context.py        # ContextBuilder 上下文构建 ★★
│   ├── memory.py         # MemoryStore 记忆系统 ★★
│   ├── skills.py         # SkillsLoader 技能加载
│   ├── subagent.py       # SubagentManager 子代理管理
│   └── tools/            # 工具模块 ★★★
│       ├── base.py       # Tool 基类
│       ├── registry.py   # ToolRegistry 工具注册
│       ├── filesystem.py # 文件读写工具
│       ├── shell.py      # Shell 执行工具
│       ├── web.py        # Web 搜索/获取
│       ├── message.py    # 消息发送
│       ├── cron.py       # 定时任务
│       ├── spawn.py      # 子进程启动
│       └── mcp.py        # MCP 集成
├── bus/                  # 消息总线
│   ├── events.py         # 消息事件定义
│   └── queue.py          # MessageBus 队列 ★★
├── channels/             # 渠道模块
│   ├── base.py          # BaseChannel 基类 ★★
│   ├── manager.py       # ChannelManager 渠道管理 ★★
│   ├── telegram.py      # Telegram 渠道
│   ├── discord.py       # Discord 渠道
│   ├── whatsapp.py      # WhatsApp 渠道
│   ├── feishu.py        # 飞书渠道
│   ├── dingtalk.py      # 钉钉渠道
│   ├── slack.py         # Slack 渠道
│   ├── qq.py            # QQ 渠道
│   ├── email.py         # Email 渠道
│   ├── matrix.py        # Matrix 渠道
│   └── mochat.py        # Mochat 渠道
├── providers/           # LLM 提供商模块
│   ├── base.py          # LLMProvider 基类 ★★
│   ├── litellm_provider.py  # LiteLLM 提供商 ★★
│   ├── registry.py      # Provider 注册表
│   ├── azure_openai_provider.py
│   ├── openai_codex_provider.py
│   ├── custom_provider.py
│   └── transcription.py
├── session/            # 会话管理模块
│   ├── __init__.py
│   └── manager.py      # Session/SessionManager ★★
├── config/             # 配置模块
│   ├── __init__.py
│   ├── loader.py       # 配置加载器
│   ├── paths.py        # 路径配置
│   └── schema.py       # Pydantic 配置模型 ★★
├── cli/                # CLI 模块
│   └── commands.py     # Typer CLI 命令 ★★
├── cron/               # 定时任务模块
│   ├── __init__.py
│   ├── service.py      # CronService 定时任务
│   └── types.py
├── heartbeat/          # 心跳服务模块
│   ├── __init__.py
│   └── service.py      # HeartbeatService
├── skills/             # 内置技能
├── templates/          # 模板文件
└── utils/              # 工具函数
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
    media: list[str] = field(default_factory=list)  # 媒体文件
    metadata: dict = field(default_factory=dict)    # 元数据
    session_key_override: str | None = None        # 会话 key 覆盖

@dataclass
class OutboundMessage:
    """出站消息：Agent -> MessageBus -> 渠道 -> 用户"""
    channel: str              # 渠道名称
    chat_id: str              # 聊天 ID
    content: str              # 消息内容
    media: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

### 3.3 设计要点

1. **异步队列**：使用 `asyncio.Queue` 实现真正的异步处理
2. **解耦架构**：渠道模块与 Agent 核心不直接通信，通过 MessageBus 中转
3. **双向通信**：入站队列处理用户消息，出站队列处理回复消息

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
        max_iterations: int = 40,       # 最大迭代次数
        temperature: float = 0.1,        # 温度参数
        max_tokens: int = 4096,          # 最大 token 数
        memory_window: int = 100,        # 内存窗口大小
        # ... 其他参数
    ):
        self.bus = bus
        self.provider = provider
        self.workspace = workspace
        self.max_iterations = max_iterations
        # 初始化各组件
        self.context = ContextBuilder(workspace)
        self.sessions = session_manager or SessionManager(workspace)
        self.tools = ToolRegistry()
        self.subagents = SubagentManager(...)
```

### 4.2 核心循环流程

```python
async def _run_agent_loop(self, initial_messages, on_progress=None):
    """Agent 迭代循环"""
    messages = initial_messages
    iteration = 0

    while iteration < self.max_iterations:
        iteration += 1

        # 1. 调用 LLM
        response = await self.provider.chat(
            messages=messages,
            tools=self.tools.get_definitions(),
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            reasoning_effort=self.reasoning_effort,
        )

        # 2. 如果有工具调用
        if response.has_tool_calls:
            # 添加助手消息到上下文
            messages = self.context.add_assistant_message(
                messages, response.content, tool_call_dicts, ...
            )

            # 执行工具调用
            for tool_call in response.tool_calls:
                result = await self.tools.execute(
                    tool_call.name, tool_call.arguments
                )
                # 添加工具结果到上下文
                messages = self.context.add_tool_result(
                    messages, tool_call.id, tool_call.name, result
                )

        # 3. 如果没有工具调用（最终响应）
        else:
            final_content = response.content
            break

    return final_content, tools_used, messages
```

### 4.3 消息处理流程

```python
async def _process_message(self, msg: InboundMessage) -> OutboundMessage | None:
    """处理单条入站消息"""

    # 1. 创建/获取会话
    key = msg.session_key
    session = self.sessions.get_or_create(key)

    # 2. 处理特殊命令
    if msg.content.strip().lower() == "/new":
        # 开始新会话
        await self._consolidate_memory(session, archive_all=True)
        session.clear()
        return OutboundMessage(content="New session started.")

    if msg.content.strip().lower() == "/help":
        return OutboundMessage(content="帮助信息...")

    # 3. 内存 Consolidation（自动）
    unconsolidated = len(session.messages) - session.last_consolidated
    if unconsolidated >= self.memory_window:
        # 触发记忆整合
        await self._consolidate_memory(session)

    # 4. 获取历史消息
    history = session.get_history(max_messages=self.memory_window)

    # 5. 构建消息列表
    initial_messages = self.context.build_messages(
        history=history,
        current_message=msg.content,
        media=msg.media,
        channel=msg.channel,
        chat_id=msg.chat_id,
    )

    # 6. 运行 Agent 循环
    final_content, _, all_msgs = await self._run_agent_loop(
        initial_messages, on_progress=on_progress
    )

    # 7. 保存会话
    self._save_turn(session, all_msgs, 1 + len(history))
    self.sessions.save(session)

    # 8. 返回响应
    return OutboundMessage(
        channel=msg.channel,
        chat_id=msg.chat_id,
        content=final_content,
    )
```

### 4.4 关键特性

1. **进度流式输出**：通过 `on_progress` 回调支持流式输出
2. **会话隔离**：每个 channel:chat_id 对应独立会话
3. **内存 Consolidation**：自动将旧消息整合到长期记忆
4. **工具调用链**：支持多轮工具调用（最多 40 轮）
5. **错误处理**：LLM 错误响应不会污染会话历史（防止 400 错误循环）

---

## 5. 上下文构建器

### 5.1 ContextBuilder 作用

**文件位置：** `nanobot/agent/context.py`

构建发送给 LLM 的完整消息列表，包括：
- System Prompt（系统提示词）
- 会话历史
- 当前用户消息

### 5.2 系统提示词构建

```python
def build_system_prompt(self, skill_names: list[str] | None = None) -> str:
    """构建系统提示词"""
    parts = []

    # 1. 核心身份
    parts.append(self._get_identity())

    # 2. Bootstrap 文件 (AGENTS.md, SOUL.md, USER.md, TOOLS.md)
    bootstrap = self._load_bootstrap_files()
    if bootstrap:
        parts.append(bootstrap)

    # 3. 长期记忆
    memory = self.memory.get_memory_context()
    if memory:
        parts.append(f"# Memory\n\n{memory}")

    # 4. Always-on 技能
    always_skills = self.skills.get_always_skills()
    if always_skills:
        always_content = self.skills.load_skills_for_context(always_skills)
        if always_content:
            parts.append(f"# Active Skills\n\n{always_content}")

    # 5. 技能摘要
    skills_summary = self.skills.build_skills_summary()
    if skills_summary:
        parts.append(f"# Skills\n\n{skills_summary}")

    return "\n\n---\n\n".join(parts)
```

### 5.3 运行时上下文注入

```python
@staticmethod
def _build_runtime_context(channel: str | None, chat_id: str | None) -> str:
    """构建运行时元数据"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
    tz = time.strftime("%Z") or "UTC"
    lines = [f"Current Time: {now} ({tz})"]
    if channel and chat_id:
        lines += [f"Channel: {channel}", f"Chat ID: {chat_id}"]
    return "[Runtime Context — metadata only, not instructions]\n" + "\n".join(lines)
```

### 5.4 完整消息构建

```python
def build_messages(self, history, current_message, skill_names=None,
                  media=None, channel=None, chat_id=None):
    """构建完整的消息列表"""
    runtime_ctx = self._build_runtime_context(channel, chat_id)
    user_content = self._build_user_content(current_message, media)

    # 合并运行时上下文和用户消息（避免连续相同 role 消息）
    if isinstance(user_content, str):
        merged = f"{runtime_ctx}\n\n{user_content}"
    else:
        merged = [{"type": "text", "text": runtime_ctx}] + user_content

    return [
        {"role": "system", "content": self.build_system_prompt(skill_names)},
        *history,
        {"role": "user", "content": merged},
    ]
```

### 5.5 图像处理

```python
def _build_user_content(self, text: str, media: list[str] | None):
    """构建用户消息内容，支持 base64 编码的图片"""
    if not media:
        return text

    images = []
    for path in media:
        p = Path(path)
        if not p.is_file():
            continue
        raw = p.read_bytes()
        # 检测 MIME 类型
        mime = detect_image_mime(raw) or mimetypes.guess_type(path)[0]
        if not mime or not mime.startswith("image/"):
            continue
        b64 = base64.b64encode(raw).decode()
        images.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"}
        })

    if not images:
        return text
    return images + [{"type": "text", "text": text}]
```

---

## 6. 工具系统

### 6.1 工具架构

```
ToolRegistry (工具注册表)
    │
    ├── Tool 基类 (base.py)
    │       ├── name: str (工具名称)
    │       ├── description: str (描述)
    │       ├── parameters: dict (JSON Schema)
    │       └── execute(**kwargs) -> str
    │
    ├── ReadFileTool (filesystem.py)
    ├── WriteFileTool (filesystem.py)
    ├── EditFileTool (filesystem.py)
    ├── ListDirTool (filesystem.py)
    ├── ExecTool (shell.py)
    ├── WebSearchTool (web.py)
    ├── WebFetchTool (web.py)
    ├── MessageTool (message.py)
    ├── CronTool (cron.py)
    ├── SpawnTool (spawn.py)
    └── MCPTool (mcp.py)
```

### 6.2 Tool 基类

**文件位置：** `nanobot/agent/tools/base.py`

```python
class Tool(ABC):
    """工具基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema 格式的参数定义"""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """执行工具"""
        pass

    def cast_params(self, params: dict) -> dict:
        """根据 Schema 类型转换参数"""
        ...

    def validate_params(self, params: dict) -> list[str]:
        """验证参数合法性"""
        ...

    def to_schema(self) -> dict:
        """转换为 OpenAI Function Calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
```

### 6.3 ToolRegistry 工具注册表

**文件位置：** `nanobot/agent/tools/registry.py`

```python
class ToolRegistry:
    """工具注册与执行"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool

    def get_definitions(self) -> list[dict]:
        """获取所有工具定义（OpenAI 格式）"""
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, params: dict) -> str:
        """执行工具"""
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found."

        try:
            # 参数类型转换
            params = tool.cast_params(params)

            # 参数验证
            errors = tool.validate_params(params)
            if errors:
                return f"Error: Invalid parameters: {'; '.join(errors)}"

            # 执行
            result = await tool.execute(**params)
            return result
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
```

### 6.4 文件工具实现

**ReadFileTool：**
```python
class ReadFileTool(Tool):
    _MAX_CHARS = 128_000  # 最大读取 128KB

    async def execute(self, path: str, **kwargs) -> str:
        file_path = _resolve_path(path, self._workspace, self._allowed_dir)

        if not file_path.exists():
            return f"Error: File not found: {path}"

        if file_path.stat().st_size > self._MAX_CHARS * 4:
            return "Error: File too large. Use head/tail/grep."

        content = file_path.read_text(encoding="utf-8")
        if len(content) > self._MAX_CHARS:
            return content[:self._MAX_CHARS] + "\n... (truncated)"
        return content
```

**WriteFileTool：**
```python
class WriteFileTool(Tool):
    async def execute(self, path: str, content: str, **kwargs) -> str:
        file_path = _resolve_path(path, self._workspace, self._allowed_dir)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} bytes to {file_path}"
```

### 6.5 Shell 执行工具

**ExecTool：**
```python
class ExecTool(Tool):
    """执行 Shell 命令"""

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute a shell command and return its output."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"]
        }

    async def execute(self, command: str, **kwargs) -> str:
        # 执行命令，返回输出
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        # 处理输出...
```

---

## 7. 会话管理

### 7.1 Session 数据结构

**文件位置：** `nanobot/session/manager.py`

```python
@dataclass
class Session:
    """会话数据模型"""
    key: str                           # channel:chat_id
    messages: list[dict[str, Any]]     # 消息列表
    created_at: datetime              # 创建时间
    updated_at: datetime               # 更新时间
    metadata: dict                     # 元数据
    last_consolidated: int = 0         # 已整合的消息数量

    def get_history(self, max_messages: int = 500) -> list[dict]:
        """获取未整合的消息历史"""
        unconsolidated = self.messages[self.last_consolidated:]
        sliced = unconsolidated[-max_messages:]

        # 丢弃开头的非 user 消息（避免孤立的 tool_result）
        for i, m in enumerate(sliced):
            if m.get("role") == "user":
                sliced = sliced[i:]
                break

        return [{"role": m["role"], "content": m.get("content", "")} for m in sliced]
```

### 7.2 SessionManager 会话管理器

```python
class SessionManager:
    """会话管理器"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.sessions_dir = ensure_dir(workspace / "sessions")
        self._cache: dict[str, Session] = {}

    def get_or_create(self, key: str) -> Session:
        """获取或创建会话"""
        if key in self._cache:
            return self._cache[key]

        session = self._load(key)
        if session is None:
            session = Session(key=key)

        self._cache[key] = session
        return session

    def _load(self, key: str) -> Session | None:
        """从磁盘加载会话（JSONL 格式）"""
        path = self._get_session_path(key)
        if not path.exists():
            # 尝试从旧位置迁移
            ...

        messages = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                if data.get("_type") == "metadata":
                    # 元数据
                    ...
                else:
                    messages.append(data)

        return Session(key=key, messages=messages, ...)

    def save(self, session: Session) -> None:
        """保存会话到磁盘（JSONL 格式）"""
        path = self._get_session_path(session.key)

        # 写入元数据
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "_type": "metadata",
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "last_consolidated": session.last_consolidated,
                "metadata": session.metadata,
            }) + "\n")

            # 写入消息
            for msg in session.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
```

### 7.3 设计要点

1. **JSONL 格式**：每行一个 JSON，方便流式读写
2. **会话缓存**：内存缓存加速访问
3. **last_consolidated**：标记已整合的消息，支持增量整合
4. **会话隔离**：channel:chat_id 作为会话 key

---

## 8. 记忆系统

### 8.1 双层记忆架构

**文件位置：** `nanobot/agent/memory.py`

```
┌─────────────────────────────────────────────┐
│           MemoryStore (两层记忆)            │
├─────────────────────────────────────────────┤
│  Layer 1: 短期记忆                         │
│  - Session.messages (会话消息列表)        │
│  - 保留最近 N 条消息                       │
├─────────────────────────────────────────────┤
│  Layer 2: 长期记忆                         │
│  - MEMORY.md (长期事实)                    │
│  - HISTORY.md (可搜索历史)                 │
└─────────────────────────────────────────────┘
```

### 8.2 记忆整合流程

```python
class MemoryStore:
    def __init__(self, workspace: Path):
        self.memory_dir = ensure_dir(workspace / "memory")
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.history_file = self.memory_dir / "HISTORY.md"

    async def consolidate(
        self,
        session: Session,
        provider: LLMProvider,
        model: str,
        archive_all: bool = False,
        memory_window: int = 50,
    ) -> bool:
        """将旧消息整合到长期记忆"""

        # 1. 确定需要整合的消息
        if archive_all:
            old_messages = session.messages
        else:
            keep_count = memory_window // 2
            old_messages = session.messages[session.last_consolidated:-keep_count]

        # 2. 构建消息摘要
        lines = []
        for m in old_messages:
            if not m.get("content"):
                continue
            tools = f" [tools: {', '.join(m['tools_used'])}]" if m.get("tools_used") else ""
            lines.append(f"[{m.get('timestamp', '?')[:16]}] {m['role'].upper()}{tools}: {m['content']}")

        # 3. 调用 LLM 生成记忆
        current_memory = self.read_long_term()
        prompt = f"""Process this conversation and call the save_memory tool.

## Current Long-term Memory
{current_memory or "(empty)"}

## Conversation to Process
{chr(10).join(lines)}"""

        response = await provider.chat(
            messages=[
                {"role": "system", "content": "You are a memory consolidation agent."},
                {"role": "user", "content": prompt},
            ],
            tools=_SAVE_MEMORY_TOOL,  # 调用 save_memory 工具
            model=model,
        )

        # 4. 保存记忆
        if response.has_tool_calls:
            args = response.tool_calls[0].arguments
            if entry := args.get("history_entry"):
                self.append_history(entry)  # 写入 HISTORY.md
            if update := args.get("memory_update"):
                self.write_long_term(update)  # 更新 MEMORY.md

            session.last_consolidated = len(session.messages) - keep_count
            return True

        return False
```

### 8.3 save_memory 工具定义

```python
_SAVE_MEMORY_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save the memory consolidation result to persistent storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "history_entry": {
                        "type": "string",
                        "description": "A paragraph summarizing key events. Start with [YYYY-MM-DD HH:MM]."
                    },
                    "memory_update": {
                        "type": "string",
                        "description": "Full updated long-term memory as markdown."
                    },
                },
                "required": ["history_entry", "memory_update"],
            },
        },
    }
]
```

---

## 9. 渠道模块

### 9.1 BaseChannel 基类

**文件位置：** `nanobot/channels/base.py`

```python
class BaseChannel(ABC):
    """渠道基类"""

    name: str = "base"

    def __init__(self, config: Any, bus: MessageBus):
        self.config = config
        self.bus = bus
        self._running = False

    @abstractmethod
    async def start(self) -> None:
        """启动渠道"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止渠道"""
        pass

    @abstractmethod
    async def send(self, msg: OutboundMessage) -> None:
        """发送消息"""
        pass

    def is_allowed(self, sender_id: str) -> bool:
        """权限检查"""
        allow_list = getattr(self.config, "allow_from", [])
        if not allow_list:
            return False
        if "*" in allow_list:
            return True
        return str(sender_id) in allow_list

    async def _handle_message(self, sender_id, chat_id, content,
                             media=None, metadata=None, session_key=None):
        """处理收到的消息，发送到 MessageBus"""
        if not self.is_allowed(sender_id):
            logger.warning("Access denied for sender {} on channel {}",
                         sender_id, self.name)
            return

        msg = InboundMessage(
            channel=self.name,
            sender_id=str(sender_id),
            chat_id=str(chat_id),
            content=content,
            media=media or [],
            metadata=metadata or {},
            session_key_override=session_key,
        )
        await self.bus.publish_inbound(msg)
```

### 9.2 ChannelManager 渠道管理器

**文件位置：** `nanobot/channels/manager.py`

```python
class ChannelManager:
    """管理所有启用的渠道"""

    def __init__(self, config: Config, bus: MessageBus):
        self.config = config
        self.bus = bus
        self.channels: dict[str, BaseChannel] = {}

        self._init_channels()

    def _init_channels(self) -> None:
        """根据配置初始化渠道"""

        # Telegram
        if self.config.channels.telegram.enabled:
            from nanobot.channels.telegram import TelegramChannel
            self.channels["telegram"] = TelegramChannel(
                self.config.channels.telegram, self.bus
            )

        # Discord
        if self.config.channels.discord.enabled:
            from nanobot.channels.discord import DiscordChannel
            self.channels["discord"] = DiscordChannel(
                self.config.channels.discord, self.bus
            )

        # ... 其他渠道类似

    async def start_all(self) -> None:
        """启动所有渠道"""

        # 1. 启动出站分发器
        self._dispatch_task = asyncio.create_task(self._dispatch_outbound())

        # 2. 启动所有渠道
        tasks = []
        for name, channel in self.channels.items():
            tasks.append(asyncio.create_task(channel.start()))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _dispatch_outbound(self) -> None:
        """分发出站消息"""
        while True:
            msg = await self.bus.consume_outbound()

            # 处理进度消息
            if msg.metadata.get("_progress"):
                if msg.metadata.get("_tool_hint") and not self.config.channels.send_tool_hints:
                    continue
                if not msg.metadata.get("_tool_hint") and not self.config.channels.send_progress:
                    continue

            # 发送到对应渠道
            channel = self.channels.get(msg.channel)
            if channel:
                await channel.send(msg)
```

### 9.3 渠道对比

| 渠道 | 通信方式 | 依赖库 | 特殊配置 |
|------|----------|--------|----------|
| Telegram | Webhook/Long Polling | python-telegram-bot | Bot Token |
| Discord | WebSocket Gateway | slack-sdk | Bot Token + Intent |
| WhatsApp | WebSocket (Baileys) | Node.js bridge | QR 码 |
| 飞书 | WebSocket | lark-oapi | App ID/Secret |
| 钉钉 | Stream Mode | dingtalk-stream | AppKey/Secret |
| Slack | Socket Mode | slack-sdk | Bot/App Token |
| QQ | WebSocket | botpy | AppID/Secret |
| Email | IMAP/SMTP | 内置 | IMAP/SMTP 配置 |
| Matrix | WebSocket | matrix-nio | Access Token |
| Mochat | Socket.IO | python-socketio | Claw Token |

---

## 10. LLM 提供商

### 10.1 LLMProvider 基类

**文件位置：** `nanobot/providers/base.py`

```python
@dataclass
class ToolCallRequest:
    """LLM 返回的工具调用请求"""
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: dict[str, int] = field(default_factory=dict)
    reasoning_content: str | None = None  # 推理内容 (Kimi, DeepSeek-R1)
    thinking_blocks: list[dict] | None = None  # Anthropic 扩展思考

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

class LLMProvider(ABC):
    """LLM 提供商基类"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
    ) -> LLMResponse:
        """发送聊天完成请求"""
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型"""
        pass
```

### 10.2 LiteLLM Provider

**文件位置：** `nanobot/providers/litellm_provider.py`

LiteLLM Provider 是默认的 LLM 提供商，通过 LiteLLM 库统一支持 100+ 模型：

```python
class LiteLLMProvider(LLMProvider):
    """使用 LiteLLM 的 LLM 提供商"""

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        default_model: str = "anthropic/claude-opus-4-5",
        extra_headers: dict[str, str] | None = None,
        provider_name: str | None = None,
    ):
        self.default_model = default_model
        self._gateway = find_gateway(provider_name, api_key, api_base)

        # 配置 LiteLLM
        litellm.suppress_debug_info = True
        litellm.drop_params = True

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
    ) -> LLMResponse:
        """调用 LiteLLM"""

        # 1. 解析模型名称
        model = model or self.default_model
        resolved_model = self._resolve_model(model)

        # 2. 处理消息
        extra_keys = self._extra_msg_keys(model, resolved_model)
        messages = self._sanitize_messages(messages, extra_keys)

        # 3. Prompt Caching (如果支持)
        if tools and self._supports_cache_control(model):
            messages, tools = self._apply_cache_control(messages, tools)

        # 4. 调用 LiteLLM
        response = await acompletion(
            model=resolved_model,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            extra_headers=self.extra_headers,
        )

        # 5. 解析响应
        return self._parse_response(response)
```

### 10.3 Provider 注册表

**文件位置：** `nanobot/providers/registry.py`

```python
# 模型注册表定义示例
MODELS = {
    "anthropic/claude-opus-4-5": ModelSpec(
        name="anthropic",
        litellm_prefix="anthropic",
        env_key="ANTHROPIC_API_KEY",
        supports_prompt_caching=True,
    ),
    "openai/gpt-4o": ModelSpec(
        name="openai",
        litellm_prefix="openai",
        env_key="OPENAI_API_KEY",
    ),
    # ... 更多模型
}
```

---

## 11. 配置系统

### 11.1 配置模型

**文件位置：** `nanobot/config/schema.py`

使用 Pydantic 定义配置模型，支持 camelCase 和 snake_case：

```python
class Base(BaseModel):
    """基类，支持 camelCase 和 snake_case"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

# 渠道配置
class TelegramConfig(Base):
    enabled: bool = False
    token: str = ""
    allow_from: list[str] = Field(default_factory=list)
    proxy: str | None = None
    reply_to_message: bool = False

class FeishuConfig(Base):
    enabled: bool = False
    app_id: str = ""
    app_secret: str = ""
    encrypt_key: str = ""
    verification_token: str = ""
    allow_from: list[str] = Field(default_factory=list)
    react_emoji: str = "THUMBSUP"

# 提供商配置
class OpenAIConfig(Base):
    api_key: str = ""
    api_base: str | None = None

class LiteLLMConfig(Base):
    api_key: str = ""
    api_base: str | None = None

# 主配置
class Config(Base):
    version: int = 1
    workspace: Path = Path("~/.nanobot")

    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    channels: ChannelsConfig = Field(default_factory=ChannelsConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
```

### 11.2 配置加载

**文件位置：** `nanobot/config/loader.py`

```python
def load_config(config_path: Path | None = None) -> Config:
    """加载配置"""
    config_path = config_path or get_config_path()

    if not config_path.exists():
        return Config()

    with open(config_path) as f:
        data = json.load(f)

    return Config(**data)
```

---

## 12. CLI 命令行

### 12.1 CLI 命令

**文件位置：** `nanobot/cli/commands.py`

使用 Typer 构建 CLI：

```python
app = typer.Typer(name="nanobot", help="nanobot - Personal AI Assistant")

@app.command()
def agent():
    """启动 CLI 交互模式"""
    ...

@app.command()
def gateway():
    """启动网关（连接渠道）"""
    ...

@app.command()
def onboard():
    """初始化配置"""
    ...

@app.command()
def channels():
    """渠道管理命令"""
    ...
```

### 12.2 使用方式

```bash
# 初始化
nanobot onboard

# CLI 交互模式
nanobot agent

# 启动网关（连接渠道）
nanobot gateway

# 渠道登录（如 WhatsApp）
nanobot channels login
```

---

## 13. 学习路线与实践

### 13.1 推荐学习顺序

| 阶段 | 模块 | 核心文件 | 重点内容 |
|------|------|----------|----------|
| 1 | 消息总线 | `bus/queue.py`, `bus/events.py` | 异步队列、消息定义 |
| 2 | Agent 核心 | `agent/loop.py` | 核心循环、工具调用 |
| 3 | 上下文 | `agent/context.py` | System Prompt、消息构建 |
| 4 | 工具系统 | `agent/tools/base.py`, `registry.py` | 工具接口、注册、执行 |
| 5 | 文件工具 | `agent/tools/filesystem.py` | 文件读写实现 |
| 6 | 会话管理 | `session/manager.py` | 会话持久化、JSONL |
| 7 | 记忆系统 | `agent/memory.py` | 记忆整合、HISTORY/MEMORY |
| 8 | 渠道基类 | `channels/base.py`, `manager.py` | 渠道接口、消息路由 |
| 9 | 渠道实现 | `channels/telegram.py` | 任意渠道深入 |
| 10 | LLM 提供商 | `providers/base.py`, `litellm_provider.py` | 多模型支持 |
| 11 | 配置系统 | `config/schema.py` | Pydantic 配置模型 |

### 13.2 实践项目建议

1. **添加新渠道**：实现一个简单的自定义渠道
2. **添加新工具**：实现一个自定义工具（如天气查询）
3. **添加新 Provider**：添加一个 LiteLLM 不支持的模型
4. **修改 Agent 行为**：添加自定义的记忆策略

### 13.3 调试技巧

```python
# 开启详细日志
import nanobot
import logging
logging.basicConfig(level=logging.DEBUG)

# 本地测试 CLI
nanobot agent

# 测试消息处理
from nanobot.bus.queue import MessageBus
from nanobot.bus.events import InboundMessage

bus = MessageBus()
await bus.publish_inbound(InboundMessage(
    channel="cli",
    sender_id="test",
    chat_id="test",
    content="Hello"
))
```

---

## 附录：关键代码行数统计

```
agent/loop.py         ~510 行   (核心循环)
agent/context.py      ~194 行   (上下文构建)
agent/memory.py      ~158 行   (记忆系统)
agent/tools/*.py     ~800+ 行  (工具系统)
channels/*.py        ~180+ 行  (每个渠道)
session/manager.py   ~200+ 行  (会话管理)
providers/*.py       ~400+ 行  (LLM 提供商)
config/schema.py     ~450+ 行  (配置模型)
cli/commands.py      ~900+ 行  (CLI 命令)
```

---

*本文档基于 nanobot v0.1.4.post4 版本生成*
