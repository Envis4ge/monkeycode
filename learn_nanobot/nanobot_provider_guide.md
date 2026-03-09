# Nanobot LLM Provider 适配机制详解

## 目录

1. [架构概述](#1-架构概述)
2. [Provider 注册机制](#2-provider-注册机制)
3. [适配器实现](#3-适配器实现)
4. [支持的 Provider 列表](#4-支持的-provider-列表)
5. [模型匹配机制](#5-模型匹配机制)
6. [添加新 Provider](#6-添加新-provider)

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

    # 其他
    is_oauth: bool = False      # 是否 OAuth 认证
    is_direct: bool = False     # 是否直连（绕过 LiteLLM）
    supports_prompt_caching: bool = False  # 是否支持 Prompt Caching
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

## 3. 适配器实现

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

        # 2. 设置环境变量
        if api_key:
            self._setup_env(api_key, api_base, default_model)

    def _resolve_model(self, model: str) -> str:
        """解析模型名称，应用前缀"""
        if self._gateway:
            # 网关模式：应用网关前缀
            prefix = self._gateway.litellm_prefix
            if self._gateway.strip_model_prefix:
                model = model.split("/")[-1]  # 去除原前缀
            if prefix and not model.startswith(f"{prefix}/"):
                model = f"{prefix}/{model}"
            return model

        # 标准模式：通过关键词匹配前缀
        spec = find_by_model(model)
        if spec and spec.litellm_prefix:
            model = f"{spec.litellm_prefix}/{model}"
        return model

    async def chat(self, messages, tools=None, model=None, ...):
        """统一的 chat 接口"""
        resolved_model = self._resolve_model(model or self.default_model)

        # 消息处理
        messages = self._sanitize_messages(messages)

        # Prompt Caching（如果支持）
        if tools and self._supports_cache_control(model):
            messages, tools = self._apply_cache_control(messages, tools)

        # 调用 LiteLLM
        response = await acompletion(
            model=resolved_model,
            messages=messages,
            tools=tools,
            ...
        )

        return self._parse_response(response)
```

### 3.2 Direct Provider（直连适配器）

**文件位置：** `nanobot/providers/azure_openai_provider.py`

```python
class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI 直连适配器"""

    async def chat(self, messages, tools=None, model=None, ...):
        # 直接使用 OpenAI SDK 调用 Azure
        response = await openai.AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version="2024-10-21",
            azure_endpoint=self.api_base,
        ).chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            ...
        )
        return self._parse_response(response)
```

### 3.3 OAuth Provider（OAuth 认证）

**文件位置：** `nanobot/providers/openai_codex_provider.py`

```python
class OpenAICodexProvider(LLMProvider):
    """OpenAI Codex OAuth 认证适配器"""

    def __init__(self, default_model: str = "openai-codex"):
        # 使用 OAuth 流程获取 token
        self._token = self._get_oauth_token()
```

---

## 4. 支持的 Provider 列表

### 4.1 网关 Provider（Gateway）

| Provider | 配置名 | API Key 前缀 | API Base | 特点 |
|----------|--------|--------------|----------|------|
| **OpenRouter** | `openrouter` | `sk-or-` | `openrouter.ai/api/v1` | 全球网关，支持 100+ 模型 |
| **SiliconFlow** | `siliconflow` | - | `api.siliconflow.cn/v1` | 硅基流动，国内可用 |
| **VolcEngine** | `volcengine` | - | `ark.cn-beijing.volces.com` | 火山引擎，豆包模型 |
| **AiHubMix** | `aihubmix` | - | `aihubmix.com/v1` | 自动前缀转换 |

### 4.2 标准 Provider（Standard）

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

### 4.3 本地部署（Local）

| Provider | 配置名 | 环境变量 | 特点 |
|----------|--------|----------|------|
| **vLLM** | `vllm` | `HOSTED_VLLM_API_KEY` | 本地部署，支持 OpenAI 兼容 API |

### 4.4 直连 Provider（Direct）

| Provider | 配置名 | 特点 |
|----------|--------|------|
| **Azure OpenAI** | `azure_openai` | 企业级部署，绕过 LiteLLM |
| **Custom** | `custom` | 自定义 OpenAI 兼容端点 |

### 4.5 OAuth Provider

| Provider | 配置名 | 认证方式 |
|----------|--------|----------|
| **OpenAI Codex** | `openai_codex` | OAuth 登录 |
| **GitHub Copilot** | `github_copilot` | OAuth 登录 |

---

## 5. 模型匹配机制

### 5.1 匹配优先级

```
模型匹配优先级：

1. 网关检测（最高优先级）
   │
   ├── API Key 前缀匹配
   │   └── sk-or-* → OpenRouter
   │
   └── API Base URL 关键词匹配
       └── siliconflow.cn → SiliconFlow

2. 配置指定（次优先级）
   │
   └── provider_name 直接指定
       └── "dashscope" → DashScope

3. 模型名关键词匹配（最低优先级）
   │
   ├── qwen-* → DashScope (prefix: dashscope)
   ├── claude-* → Anthropic
   ├── gpt-* → OpenAI
   ├── deepseek-* → DeepSeek
   └── ...
```

### 5.2 模型前缀处理

```python
# 示例：模型名转换为 LiteLLM 格式

原始模型                    转换后                    Provider
─────────────────────────────────────────────────────────────
claude-opus-4-5         (无需转换)              Anthropic
gpt-4o                  (无需转换)              OpenAI
qwen-max                dashscope/qwen-max      DashScope
deepseek-chat           deepseek/deepseek-chat  DeepSeek
gemini-pro              gemini/gemini-pro       Gemini
llama-3-8b              openrouter/llama-3-8b  OpenRouter
```

### 5.3 Prompt Caching 支持

支持 Prompt Caching 的 Provider：

| Provider | 特点 |
|----------|------|
| **Anthropic** | 原生支持 |
| **OpenRouter** | 转发 Anthropic 模型时支持 |

---

## 6. 添加新 Provider

### 6.1 添加步骤

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
```

### 6.2 配置示例

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
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  }
}
```

---

## 7. 工作流程图

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
│ 2. find_by_model(model)                 │
│    → 通过关键词匹配标准 Provider        │
│                                         │
│ 3. _resolve_model(model)                │
│    → 应用正确的模型前缀                 │
│                                         │
│ 4. acompletion(model, messages, tools) │
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
│   • ...                                │
└─────────────────────────────────────────┘
```

---

*本文档基于 nanobot v0.1.4.post4 版本生成*
