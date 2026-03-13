# MCP 与 Skills 实现方法研究报告

**生成时间**: 2026-03-13  
**研究目标**: 深入研究 MCP 和 Skills 的实现方法

---

## 一、MCP (Model Context Protocol) 研究

### 1.1 MCP 定义

**MCP (Model Context Protocol)** 是一个开放协议，用于将 AI 应用连接到外部系统。

> 就像 USB-C 为电子设备提供标准化连接方式一样，MCP 为 AI 应用提供了一种标准化连接外部系统的方式。

### 1.2 MCP 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Host (AI 应用)                        │
│   运行 LLM 的环境（如 Claude Desktop、VS Code、ChatGPT）        │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   MCP Client      │
                    │  (维护连接、发现工具)│
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   MCP Server      │
                    │ (提供工具/资源/提示) │
                    └───────────────────┘
```

### 1.3 MCP 两层架构

| 层级 | 说明 |
|------|------|
| **数据层** | 基于 JSON-RPC 2.0，包含生命周期管理、核心原语 |
| **传输层** | STDIO（本地）、Streamable HTTP（远程） |

### 1.4 MCP 三大原语 (Primitives)

| 原语 | 作用 | 示例 |
|------|------|------|
| **Tools** | AI 可调用的执行函数 | 文件操作、API调用 |
| **Resources** | 提供上下文数据 | 文件内容、数据库记录 |
| **Prompts** | 交互模板 | 系统提示词、few-shot示例 |

### 1.5 官方 SDK

| 语言 | 包名 | GitHub 仓库 |
|------|------|-------------|
| TypeScript | `@modelcontextprotocol/server` | [typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) |
| Python | `mcp` (pip install mcp) | [python-sdk](https://github.com/modelcontextprotocol/python-sdk) |
| Java | (查看官方仓库) | [java-sdk](https://github.com/modelcontextprotocol/java-sdk) |
| Go | (查看官方仓库) | [go-sdk](https://github.com/modelcontextprotocol/go-sdk) |

> **注意**：SDK 包名可能随版本变化，建议访问对应 GitHub 仓库查看最新安装方式。

### 1.6 MCP Server 实现示例 (Python)

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

# 创建 Server
server = Server("my-server")

# 注册工具
@server.tool()
async def get_weather(city: str) -> str:
    """查询城市天气"""
    # 实际业务逻辑
    return f"{city} 的天气是晴天，20°C"

# 运行服务器 (STDIO 模式)
if __name__ == "__main__":
    asyncio.run(server.run_stdio())
```

---

## 二、Skills 研究

### 2.1 Skills 定义

Skills 是模块化、自包含的包，通过提供专业化知识、工作流程和工具来扩展 AI 能力。

> 就像"入职指南"——将通用 AI 转变为专业领域的专家。

### 2.2 Skills 目录结构

```
skill-name/
├── SKILL.md              # 必需
│   ├── ---               # YAML frontmatter
│   │   name:             # 技能名称
│   │   description:      # 触发描述（关键！）
│   └── Markdown body    # 技能说明
├── scripts/              # 可选：可执行脚本
├── references/           # 可选：参考文档
└── assets/               # 可选：静态资源
```

### 2.3 Skills 触发机制

```
用户输入 → 检查 Metadata → 匹配 → 加载 SKILL.md → 按需加载资源
```

### 2.4 Progressive Disclosure 设计

| 层级 | 内容 | 加载条件 |
|------|------|----------|
| Level 1 | Metadata (name + description) | 始终加载 |
| Level 2 | SKILL.md body | 技能触发时 |
| Level 3 | Bundled resources | 按需加载 |

### 2.5 创建 Skill 的步骤

1. **理解需求** - 明确具体使用场景
2. **规划内容** - 列出 scripts/references/assets
3. **初始化** - 运行 `init_skill.py`
4. **编辑实现** - 编写 SKILL.md 和资源文件
5. **打包发布** - 运行 `package_skill.py`
6. **迭代优化** - 根据使用反馈改进

---

## 三、MCP vs Skills 对比

| 特性 | MCP | Skills |
|------|-----|--------|
| **定位** | AI 与外部系统通信协议 | AI 能力扩展包 |
| **核心** | 标准化连接 | 专业化知识 |
| **通信** | JSON-RPC 2.0 | Markdown + 脚本 |
| **触发** | 运行时动态发现 | 静态 metadata 匹配 |
| **状态** | 有状态 | 无状态 |

---

## 四、参考资源

### MCP 官方
- 官网: https://modelcontextprotocol.io
- 规范: https://modelcontextprotocol.io/specification/latest
- SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Servers: https://github.com/modelcontextprotocol/servers

### Skills 参考
- 本地示例: `/root/.openclaw/workspace/skills/skill-creator/`
- 官方 Skill 商店: 已在系统中安装多个 Skills

---

## 五、总结

1. **MCP** 解决 AI 与外部系统连接的标准化问题
2. **Skills** 解决 AI 专业化能力扩展的问题
3. 两者可以结合使用：MCP 作为通信层，Skills 作为能力封装

---

*报告完成*