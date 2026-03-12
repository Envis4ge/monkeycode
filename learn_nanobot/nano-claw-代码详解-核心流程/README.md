# 🦞 nano-claw 代码详解

> 超轻量级个人 AI 助手框架 - 核心代码详细注释

## 📚 文档说明

本目录包含 nano-claw 框架核心代码的详细中文注释，适合初学者学习。

## 📁 文件列表

### 核心流程注释（按执行顺序）

| 文件 | 说明 |
|------|------|
| `01_agent_loop_带详细注释.ts` | 代理核心循环 - 整个框架的大脑 |
| `02_memory_带详细注释.ts` | 记忆系统 - 对话历史持久化 |
| `03_context_builder_带详细注释.ts` | 上下文构建器 - 构建发送给 LLM 的消息 |
| `04_skills_loader_带详细注释.ts` | 技能加载器 - 加载 Markdown 技能文件 |
| `05_tool_registry_带详细注释.ts` | 工具注册表 - 管理所有可用工具 |
| `06_shell_tool_带详细注释.ts` | Shell 工具 - 执行命令行命令 |
| `07_file_tools_带详细注释.ts` | 文件工具 - 读写文件 |
| `08_provider_manager_带详细注释.ts` | 提供商管理器 - 管理 LLM 调用 |
| `09_完整架构流程图.ts` | 完整架构流程图和目录结构 |

## 🎯 学习路径

### 1. 新手入门（推荐顺序）

```
1. 阅读 09_完整架构流程图.ts
   → 了解整体架构和执行流程

2. 阅读 01_agent_loop_带详细注释.ts
   → 理解核心循环如何工作

3. 阅读 02_memory_带详细注释.ts
   → 理解如何存储对话历史

4. 阅读 03_context_builder_带详细注释.ts
   → 理解如何构建 LLM 上下文
```

### 2. 进阶学习

```
5. 阅读 04_skills_loader_带详细注释.ts
   → 理解技能系统

6. 阅读 05_tool_registry_带详细注释.ts
   → 理解工具系统

7. 阅读 06_shell_tool_带详细注释.ts
   → 理解 Shell 工具实现

8. 阅读 07_file_tools_带详细注释.ts
   → 理解文件工具实现
```

### 3. 高级主题

```
9. 阅读 08_provider_manager_带详细注释.ts
   → 理解多 LLM 提供商支持
```

## 🏗️ 核心概念

### Agent Loop（代理循环）

```
用户消息 → 构建上下文 → 调用 LLM → 执行工具 → 返回结果
```

### Memory（记忆）

- 持久化存储对话历史
- 自动清理旧消息
- 按会话隔离

### Skills（技能）

- Markdown 文件形式
- 扩展 AI 能力
- 动态加载

### Tools（工具）

- 预定义函数调用
- 安全可控
- 可扩展

### Provider（提供商）

- 支持多种 LLM
- 自动路由
- 统一接口

## 🔧 快速开始

### 安装

```bash
npm install -g nano-claw
```

### 配置

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

### 运行

```bash
nano-claw onboard
nano-claw agent -m "你好"
```

## 📖 相关资源

- [nano-claw 官方仓库](https://github.com/hustcc/nano-claw)
- [awesome-nanobot](https://github.com/billLiao/awesome-nanobot)

## 📝 注释规范

本项目注释遵循以下规范：

```typescript
/**
 * ============================================================
 * 标题
 * ============================================================
 * 
 * 详细说明...
 */

// 方法说明
/**
 * 方法功能
 * @param 参数说明
 * @returns 返回值说明
 */
async function example(param: string): Promise<string> {
  // 步骤说明
  // ...
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License