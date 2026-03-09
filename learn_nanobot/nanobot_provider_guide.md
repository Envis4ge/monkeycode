# Nanobot LLM Provider 适配机制详解

## 目录

1. [架构概述](#1-架构概述)
2. [Provider 注册机制](#2-provider-注册机制)
3. [适配器实现详解](#3-适配器实现详解)
4. [通信与认证机制](#4-通信与认证机制)
5. [支持的 Provider 列表](#5-支持的-provider-列表)
6. [模型匹配机制](#6-模型匹配机制)
7. [消息处理与响应解析](#7-消息处理与响应解析)
8. [添加新 Provider](#8-添加新-provider)

---

## 1. 架构概述

Nanobot 采用**三层适配架构**来实现对多种 LLM Provider 的支持：

```
┌─────────────────────────────────────────────────────────────┐
│                     配置层 (config/schema.py)                 │
│              定义各 Provider 的配置字段                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 注册表层 (providers/registry.py)             │
│            ProviderSpec 定义 + 查找函数                       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ find_by_   │  │ find_       │  │ find_by_name    │   │
│  │ model()    │  │ gateway()   │  │                 │   │
│  └─────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  适配层 (providers/*.py)                     │
│                                                              │
│  ┌──────────────────┐   ┌────────────────────────────┐   │
│  │ LiteLLMProvider  │   │  Direct Provider            │   │
│  │ (通用适配器)      │   │  - AzureOpenAIProvider     │   │
│  │                  │   │  - CustomProvider           │   │
│  │ 100+ 模型        │   │  - OpenAICodexProvider      │   │
│  └──────────────────┘   └────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Provider 注册机制

### 2.1 ProviderSpec 数据结构

**文件位置：** `nanobot/providers/registry.py`

```python
@dataclass(frozen=True)
class ProviderSpec:
    """Provider 元数据定义"""

    # 身份
    name: str                    # 配置字段名，如 "dashscope"
    keywords: tuple[str, ...]    # 模型名关键词，用于匹配
    env_key: str                 # 环境变量，如 "DASHSCOPE_API_KEY"

    # 模型前缀处理
    litellm_prefix: str = ""    # LiteLLM 前缀，如 "dashscope"
    skip_prefixes: tuple[str, ...] = ()  # 跳过前缀的场景

    # 网关/本地部署
    is_gateway: bool = False     # 是否网关（如 OpenRouter）
    is_local: bool = False       # 是否本地部署（如 vLLM）
    detect_by_key_prefix: str = ""  # API Key 前缀检测
    detect_by_base_keyword: str = ""  # API Base URL 关键词检测
    default_api_base: str = ""    # 默认 API Base URL

    # 其他
    is_oauth: bool = False      # 是否 OAuth 认证
    is_direct: bool = False     # 是否直连（绕过 LiteLLM）
    supports_prompt_caching: bool = False  # 是否支持 Prompt Caching

    # 模型特定参数覆盖
    model_overrides: tuple[tuple[str, dict[str, Any]], ...] = ()
```

### 2.2 Provider 类型分类

```
Provider 类型：
│
├── 标准 Provider（Standard）
│   ├── 通过模型名关键词匹配
│   ├── 示例：anthropic, openai, deepseek, gemini
│   └── 查找函数：find_by_model()
│
├── 网关 Provider（Gateway）
│   ├── 通过 API Key 前缀或 API Base URL 关键词检测
│   ├── 可以路由任意模型
│   ├── 示例：openrouter, siliconflow, volcengine
│   └── 查找函数：find_gateway()
│
├── 本地部署（Local）
│   ├── 检测方式同网关
│   ├── 示例：vllm, ollama
│   └── 查找函数：find_gateway()
│
├── 直连 Provider（Direct）
│   ├── 绕过 LiteLLM，直接调用
│   ├── 示例：azure_openai, custom
│   └── 在 CLI 中特殊处理
│
└── OAuth Provider
    ├── 使用 OAuth 认证，无需 API Key
    ├── 示例：openai_codex, github_copilot
    └── 在 CLI 中特殊处理
```

---

## 3. 适配器实现详解

### 3.1 LiteLLMProvider（通用适配器）

**文件位置：** `nanobot/providers/litellm_provider.py`

通过 LiteLLM 库统一支持 100+ 模型：

```python
class LiteLLMProvider(LLMProvider):
    """使用 LiteLLM 的统一接口"""

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        default_model: str = "anthropic/claude-opus-4-5",
        provider_name: str | None = None,
    ):
        # 1. 检测网关/本地部署
        self._gateway = find_gateway(provider_name, api_key, api_base)

        # 2. 设置环境变量（详见第 4 节）
        if api_key:
            self._setup_env(api_key, api_base, default_model)

        # 3. 设置自定义 API Base
        if api_base:
            litellm.api_base = api_base

    def _resolve_model(self, model: str) -> str:
        """解析模型名称，应用前缀"""
        if self._gateway:
            # 网关模式：应用网关前缀
            prefix = self._gateway.litellm_prefix
            if self._gateway.strip_model_prefix:
                model = model.split("/")[-1]
            if prefix and not model.startswith(f"{prefix}/"):
                model = f"{prefix}/{model}"
            return model

        # 标准模式：通过关键词匹配前缀
        spec = find_by_model(model)
        if spec and spec.litellm_prefix:
            model = f"{spec.litellm_prefix}/{model}"
        return model
```

---

## 4. 通信与认证机制

### 4.1 环境变量设置流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    环境变量设置流程 (_setup_env)                  │
└─────────────────────────────────────────────────────────────────┘

1. 获取 Provider Spec
   │
   ├── find_gateway() → 网关/本地部署
   │
   └── find_by_model() → 标准 Provider

2. 设置主环境变量
   │
   ├── 网关/本地部署：直接覆盖
   │   └── os.environ[spec.env_key] = api_key
   │
   └── 标准 Provider：仅当未设置时
       └── os.environ.setdefault(spec.env_key, api_key)

3. 设置额外环境变量（env_extras）
   │
   └── 解析占位符：
       ├── {api_key} → 用户 API Key
       └── {api_base} → 用户 api_base 或 spec.default_api_base
```

**示例：DashScope 配置**

```python
# ProviderSpec 定义
ProviderSpec(
    name="dashscope",
    keywords=("qwen", "dashscope"),
    env_key="DASHSCOPE_API_KEY",
    litellm_prefix="dashscope",
    ...
)

# 实际设置的环境变量
os.environ["DASHSCOPE_API_KEY"] = "your-api-key"
# qwen-max → dashscope/qwen-max
```

**示例：Moonshot 配置（带额外变量）**

```python
ProviderSpec(
    name="moonshot",
    keywords=("moonshot", "kimi"),
    env_key="MOONSHOT_API_KEY",
    litellm_prefix="moonshot",
    env_extras=(
        ("MOONSHOT_API_BASE", "{api_base}"),  # 额外环境变量
    ),
    default_api_base="https://api.moonshot.ai/v1",
    ...
)

# 实际设置的环境变量
os.environ["MOONSHOT_API_KEY"] = "your-api-key"
os.environ.setdefault("MOONSHOT_API_BASE", "https://api.moonshot.ai/v1")
```

### 4.2 API Key 传递方式

LiteLLMProvider 支持两种 API Key 传递方式：

```python
async def chat(self, messages, tools=None, model=None, ...):
    # 方式 1：通过环境变量（自动设置）
    # 在 __init__ 中已通过 _setup_env 设置

    # 方式 2：直接传递（更可靠）
    if self.api_key:
        kwargs["api_key"] = self.api_key

    if self.api_base:
        kwargs["api_base"] = self.api_base

    # 方式 3：额外请求头（如 AiHubMix 需要 APP-Code）
    if self.extra_headers:
        kwargs["extra_headers"] = self.extra_headers

    # 调用 LiteLLM
    response = await acompletion(**kwargs)
```

### 4.3 认证类型

| 认证类型 | 实现方式 | 示例 Provider |
|----------|----------|---------------|
| **API Key** | 环境变量 + 直接传递 | anthropic, openai, deepseek |
| **OAuth** | OAuth 流程获取 token | openai_codex, github_copilot |
| **自定义 Header** | extra_headers 传递 | siliconflow (APP-Code) |
| **Azure** | API Version + Endpoint | azure_openai |

---

## 5. 支持的 Provider 列表

### 5.1 网关 Provider（Gateway）

| Provider | 配置名 | API Key 前缀 | API Base | 特点 |
|----------|--------|--------------|----------|------|
| **OpenRouter** | `openrouter` | `sk-or-` | `openrouter.ai/api/v1` | 全球网关，支持 100+ 模型 |
| **SiliconFlow** | `siliconflow` | - | `api.siliconflow.cn/v1` | 硅基流动，国内可用 |
| **VolcEngine** | `volcengine` | - | `ark.cn-beijing.volces.com` | 火山引擎，豆包模型 |
| **AiHubMix** | `aihubmix` | - | `aihubmix.com/v1` | 自动前缀转换 |

### 5.2 标准 Provider（Standard）

| Provider | 配置名 | 模型关键词 | 环境变量 | 特点 |
|----------|--------|-----------|----------|------|
| **Anthropic** | `anthropic` | `claude` | `ANTHROPIC_API_KEY` | Claude 系列，支持 Prompt Caching |
| **OpenAI** | `openai` | `gpt` | `OPENAI_API_KEY` | GPT 系列 |
| **DeepSeek** | `deepseek` | `deepseek` | `DEEPSEEK_API_KEY` | 深度求索 |
| **Gemini** | `gemini` | `gemini` | `GEMINI_API_KEY` | Google Gemini |
| **Zhipu AI** | `zhipu` | `glm`, `zhi` | `ZAI_API_KEY` | 智谱清言 |
| **DashScope** | `dashscope` | `qwen` | `DASHSCOPE_API_KEY` | 阿里通义千问 |
| **Moonshot** | `moonshot` | `kimi` | `MOONSHOT_API_KEY` | 月之暗面 Kimi |
| **MiniMax** | `minimax` | `minimax` | `MINIMAX_API_KEY` | MiniMax |
| **Groq** | `groq` | `groq` | `GROQ_API_KEY` | 快速推理 |

### 5.3 本地部署（Local）

| Provider | 配置名 | 环境变量 | 特点 |
|----------|--------|----------|------|
| **vLLM** | `vllm` | `HOSTED_VLLM_API_KEY` | 本地部署，支持 OpenAI 兼容 API |

### 5.4 直连 Provider（Direct）

| Provider | 配置名 | 特点 |
|----------|--------|------|
| **Azure OpenAI** | `azure_openai` | 企业级部署，绕过 LiteLLM，使用 API Version |
| **Custom** | `custom` | 自定义 OpenAI 兼容端点 |

### 5.5 OAuth Provider

| Provider | 配置名 | 认证方式 |
|----------|--------|----------|
| **OpenAI Codex** | `openai_codex` | OAuth 登录 |
| **GitHub Copilot** | `github_copilot` | OAuth 登录 |

---

## 6. 模型匹配机制

### 6.1 匹配优先级

```
模型匹配优先级（从高到低）：

1. 网关检测（最高优先级）
   │
   ├── 方式 A：API Key 前缀匹配
   │   └── "sk-or-*" → OpenRouter
   │   └── "sk-ant-*" → Anthropic
   │
   └── 方式 B：API Base URL 关键词匹配
       └── "siliconflow.cn" → SiliconFlow
       └── "aihubmix.com" → AiHubMix
       └── "volces.com" → VolcEngine

2. 配置指定（次优先级）
   │
   └── provider_name 直接指定
       └── 配置 "provider": "dashscope" → DashScope

3. 模型名关键词匹配（最低优先级）
   │
   ├── qwen-* → DashScope (prefix: dashscope)
   ├── claude-* → Anthropic (无需前缀)
   ├── gpt-* → OpenAI (无需前缀)
   ├── deepseek-* → DeepSeek (prefix: deepseek)
   ├── gemini-* → Gemini (prefix: gemini)
   ├── glm-* → Zhipu (prefix: zai)
   ├── kimi-* → Moonshot (prefix: moonshot)
   ├── minimax-* → MiniMax (prefix: minimax)
   └── groq-* → Groq (prefix: groq)
```

### 6.2 模型前缀处理

```python
# 模型名转换为 LiteLLM 格式

原始模型                    转换后                    Provider
─────────────────────────────────────────────────────────────
claude-opus-4-5         (无需转换)              Anthropic
gpt-4o                  (无需转换)              OpenAI
qwen-max                dashscope/qwen-max      DashScope
deepseek-chat           deepseek/deepseek-chat  DeepSeek
gemini-pro              gemini/gemini-pro       Gemini
glm-4                   zai/glm-4              Zhipu
kimi-k2.5               moonshot/kimi-k2.5     Moonshot
llama-3-8b              openrouter/llama-3-8b  OpenRouter
```

### 6.3 前缀跳过机制（skip_prefixes）

有些模型已经带有前缀，需要跳过重复添加：

```python
ProviderSpec(
    name="dashscope",
    litellm_prefix="dashscope",
    skip_prefixes=("dashscope/", "openrouter/"),
    # dashscope/qwen-max → 保持不变
    # openrouter/qwen-max → 保持不变
    # qwen-max → dashscope/qwen-max
)
```

---

## 7. 消息处理与响应解析

### 7.1 消息预处理

在发送请求前，消息会经过多层处理：

```python
async def chat(self, messages, tools=None, model=None, ...):
    # 1. 解析模型名称
    model = self._resolve_model(original_model)

    # 2. 获取 Provider 特定的消息键
    extra_msg_keys = self._extra_msg_keys(original_model, model)
    #    - Anthropic: 保留 thinking_blocks
    #    - 其他: 只保留标准键

    # 3. 清空内容处理（避免 400 错误）
    messages = self._sanitize_empty_content(messages)
    #    - 空字符串 → None 或 "(empty)"
    #    - 空文本块 → 过滤掉

    # 4. 消息清理
    messages = self._sanitize_messages(messages, extra_keys)
    #    - 只保留 allowed_keys 中的键
    #    - 确保 assistant 消息有 content 键
    #    - 规范化 tool_call_id 为 9 位字母数字
```

### 7.2 Prompt Caching 支持

对于支持 Prompt Caching 的 Provider（如 Anthropic、OpenRouter）：

```python
def _apply_cache_control(self, messages, tools):
    """为 System 消息和工具添加缓存标记"""
    new_messages = []
    for msg in messages:
        if msg.get("role") == "system":
            # 添加 cache_control 标记
            content = msg["content"]
            if isinstance(content, str):
                new_content = [{"type": "text", "text": content,
                              "cache_control": {"type": "ephemeral"}}]
            else:
                new_content = list(content)
                new_content[-1] = {...new_content[-1],
                                  "cache_control": {"type": "ephemeral"}}
            new_messages.append({**msg, "content": new_content})
        else:
            new_messages.append(msg)

    # 工具定义最后一项也添加缓存标记
    if tools:
        new_tools = list(tools)
        new_tools[-1] = {**new_tools[-1],
                        "cache_control": {"type": "ephemeral"}}

    return new_messages, new_tools
```

### 7.3 响应解析

```python
def _parse_response(self, response) -> LLMResponse:
    """解析 LiteLLM 响应为标准格式"""

    # 1. 获取主要响应
    choice = response.choices[0]
    content = choice.message.content
    finish_reason = choice.finish_reason

    # 2. 合并多选项的工具调用（某些 Provider 如 GitHub Copilot 会分开返回）
    raw_tool_calls = []
    for ch in response.choices:
        msg = ch.message
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            raw_tool_calls.extend(msg.tool_calls)

    # 3. 解析工具调用
    tool_calls = []
    for tc in raw_tool_calls:
        # arguments 可能是 JSON 字符串或 dict
        args = tc.function.arguments
        if isinstance(args, str):
            args = json_repair.loads(args)  # 修复可能的畸形 JSON

        tool_calls.append(ToolCallRequest(
            id=_short_tool_id(),  # 生成 9 位字母数字 ID
            name=tc.function.name,
            arguments=args,
        ))

    # 4. 提取推理内容（DeepSeek-R1、Kimi 等）
    reasoning_content = getattr(message, "reasoning_content", None)

    # 5. 提取 Anthropic 扩展思考
    thinking_blocks = getattr(message, "thinking_blocks", None)

    return LLMResponse(
        content=content,
        tool_calls=tool_calls,
        finish_reason=finish_reason,
        usage={...},  # token 使用量
        reasoning_content=reasoning_content,
        thinking_blocks=thinking_blocks,
    )
```

### 7.4 错误处理

```python
try:
    response = await acompletion(**kwargs)
    return self._parse_response(response)
except Exception as e:
    # 优雅降级：返回错误作为内容
    return LLMResponse(
        content=f"Error calling LLM: {str(e)}",
        finish_reason="error",
    )
```

---

## 8. 添加新 Provider

### 8.1 添加步骤

Nanobot 的设计使得添加新 Provider 只需 2 步：

**步骤 1：在 registry.py 中添加 ProviderSpec**

```python
# 示例：添加新的 Provider
ProviderSpec(
    name="myprovider",           # 配置字段名
    keywords=("myprovider", "mymodel"),  # 模型关键词
    env_key="MYPROVIDER_API_KEY",  # 环境变量
    display_name="My Provider",   # 显示名称
    litellm_prefix="myprovider", # LiteLLM 前缀
    skip_prefixes=("myprovider",),  # 避免重复前缀
    env_extras=(),                # 额外环境变量
    is_gateway=False,            # 是否网关
    is_local=False,              # 是否本地
    supports_prompt_caching=False,  # 是否支持 Prompt Caching
    model_overrides=(            # 模型特定参数
        ("my-model-v2", {"temperature": 1.0}),
    ),
),
```

**步骤 2：在 schema.py 中添加配置字段**

```python
# config/schema.py
class ProvidersConfig(Base):
    # ... 其他 provider ...

    myprovider: MyProviderConfig = Field(default_factory=MyProviderConfig)

class MyProviderConfig(Base):
    enabled: bool = False
    api_key: str = ""
    api_base: str | None = None
    extra_headers: dict[str, str] = Field(default_factory=dict)
```

### 8.2 配置示例

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    },
    "anthropic": {
      "apiKey": "sk-ant-xxx"
    },
    "dashscope": {
      "apiKey": "sk-xxx"
    },
    "azure_openai": {
      "apiKey": "your-api-key",
      "apiBase": "https://your-resource.openai.azure.com"
    },
    "custom": {
      "apiBase": "https://your-custom-endpoint.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

---

## 附录：工作流程图

```
用户请求流程：

┌─────────────┐
│ CLI / Agent │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ nanobot/providers/litellm_provider.py  │
│                                         │
│ 1. find_gateway(api_key, api_base)    │
│    → 检测是否是网关/本地部署            │
│                                         │
│ 2. _setup_env(api_key, api_base)      │
│    → 设置环境变量                      │
│                                         │
│ 3. find_by_model(model)                 │
│    → 通过关键词匹配标准 Provider        │
│                                         │
│ 4. _resolve_model(model)                │
│    → 应用正确的模型前缀                 │
│                                         │
│ 5. _sanitize_messages()                 │
│    → 清理消息，移除不支持的键          │
│                                         │
│ 6. _apply_cache_control()              │
│    → 添加 Prompt Caching 标记           │
│                                         │
│ 7. acompletion(model, messages, tools) │
│    → 调用 LiteLLM                       │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│              LiteLLM                     │
│                                        │
│ 根据模型前缀路由到对应 Provider：      │
│   • openrouter/* → OpenRouter API      │
│   • anthropic/* → Anthropic API        │
│   • openai/* → OpenAI API             │
│   • dashscope/* → DashScope API       │
│   • ...                                │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         _parse_response()                │
│                                        │
│ • 解析响应内容                          │
│ • 提取工具调用                         │
│ • 处理推理内容/扩展思考                │
│ • 返回 LLMResponse                     │
└─────────────────────────────────────────┘
```

---

*本文档基于 nanobot v0.1.4.post4 版本生成*
