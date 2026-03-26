# 完整 Agent 项目

一个整合了 **ReAct + Function Calling + 记忆系统** 的完整 Agent 实现。

## 项目结构

```
complete_agent/
├── agent.py      # 核心引擎（Agent 类、ReActAgent 类）
├── tools.py      # 工具系统（计算器、搜索、文件读取）
├── config.py     # 配置管理（LLM 端点、参数）
├── demo.py       # 演示入口
└── README.md     # 本文档
```

## 快速开始

### 1. 演示模式（无需 API）

```bash
cd complete_agent
python3 demo.py --demo
```

这会使用模拟 LLM 展示完整的工具调用流程。

### 2. 交互模式（需要 Ollama）

```bash
# 确保 Ollama 已安装并运行
ollama serve

# 下载模型（如果还没有）
ollama pull qwen2.5:7b

# 运行交互模式
python3 demo.py --interactive
```

## 架构说明

### 核心组件

1. **Agent 引擎** (`agent.py`)
   - `Agent` 类：支持 Function Calling 的完整 Agent
   - `ReActAgent` 类：纯文本 ReAct 模式（兼容不支持 FC 的 LLM）
   - `Memory` 类：短期记忆 + 长期记忆管理

2. **工具系统** (`tools.py`)
   - `calculator`: 安全计算器（限制运算符）
   - `web_search`: 模拟搜索（可替换为真实 API）
   - `file_read`: 安全文件读取（限制路径和类型）

3. **配置管理** (`config.py`)
   - LLM 端点、模型选择
   - Agent 行为参数
   - 工具安全限制

### 工作流程

```
用户输入
    ↓
Agent 主循环
    ↓
LLM 决策 (Thought)
    ├─→ 需要工具 → 执行 Action → 获取 Observation → 继续循环
    └─→ 不需要 → Final Answer → 返回用户
```

## 自定义扩展

### 添加新工具

在 `tools.py` 中添加:

```python
def my_tool(arg1, arg2):
    """工具描述"""
    # 实现逻辑
    return result

TOOLS.append({
    "name": "my_tool",
    "description": "工具描述",
    "func": my_tool,
    "parameters": {
        "type": "object",
        "properties": {
            "arg1": {"type": "string", "description": "..."}
        },
        "required": ["arg1"]
    }
})
```

### 更换 LLM

修改 `config.py`:

```python
# 使用 OpenAI
self.provider = "openai"
self.model = "gpt-4o-mini"
self.api_key = os.getenv("OPENAI_API_KEY")

# 或使用其他 Ollama 模型
self.model = "llama3.1:8b"
```

## 安全注意事项

1. **计算器**: 使用白名单过滤，禁止函数调用
2. **文件读取**: 限制在当前目录，禁止敏感文件
3. **搜索**: 模拟实现，实际使用时注意 API 限流

## 下一步

- 接入真实搜索 API（Google/Bing/SerpAPI）
- 添加更多实用工具（天气、新闻、股票等）
- 实现长期记忆的向量检索
- 添加多轮对话的状态管理

---

*这是一个教学项目，用于理解 Agent 的核心架构。生产环境需要更完善的安全和错误处理。*
