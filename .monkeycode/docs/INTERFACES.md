# 接口定义

## 命令行接口

### 主命令

```bash
python -m learn_nanobot [OPTIONS] [INPUT]
```

启动智能终端系统，进入交互式模式或处理单个命令。

**选项**:
- `--model, -m <NAME>`: 指定使用的 AI 模型（默认：配置中的主模型）
- `--config, -c <PATH>`: 指定配置文件路径（默认：`config.yaml`）
- `--test-model`: 测试 AI 模型连接
- `--add-command <CMD>`: 添加命令到知识库
- `--list-models`: 列出所有可用的 AI 模型
- `--history`: 显示命令执行历史
- `--help, -h`: 显示帮助信息

**示例**:
```bash
# 交互式模式
python -m learn_nanobot

# 处理单个命令
python -m learn_nanobot "列出当前目录的所有文件"

# 使用特定模型
python -m learn_nanobot --model ollama:llama3 "查找包含 error 的日志文件"

# 测试模型连接
python -m learn_nanobot --test-model

# 添加命令到知识库
python -m learn_nanobot --add-command

# 查看历史记录
python -m learn_nanobot --history
```

### 交互式命令

在交互式模式中，支持以下特殊命令：

| 命令 | 功能 |
|------|------|
| `/help` | 显示帮助信息 |
| `/models` | 列出可用 AI 模型 |
| `/model <name>` | 切换 AI 模型 |
| `/history` | 显示历史记录 |
| `/add` | 添加命令到知识库 |
| `/config` | 显示当前配置 |
| `/clear` | 清屏 |
| `/exit`, `/quit` | 退出系统 |

**示例**:
```
> 如何查找当前目录下的所有 Python 文件
[系统推荐命令...]

> /model ollama:llama3
已切换到模型: ollama:llama3

> /history
显示最近的命令执行记录...

> /exit
再见！
```

## 配置文件接口

### 配置文件格式 (config.yaml)

```yaml
# AI 模型配置
ai:
  # 模型列表（按优先级排序）
  models:
    - provider: openai
      name: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      base_url: https://api.openai.com/v1
      temperature: 0.7
      max_tokens: 500
      timeout: 15

    - provider: ollama
      name: llama3
      base_url: http://localhost:11434
      temperature: 0.7
      max_tokens: 500
      timeout: 30

  # 默认模型（第一个可用的模型）
  default_model: 0

  # 是否自动切换模型
  auto_fallback: true

# 知识库配置
knowledge_base:
  # 知识库文件路径
  path: data/knowledge.json

  # 命令类型
  types:
    - system      # 系统命令
    - custom      # 自定义脚本

  # 推荐配置
  recommendation:
    max_results: 3
    min_similarity: 0.5

# 执行配置
execution:
  # 命令超时时间（秒）
  timeout: 30

  # 是否显示实时输出
  show_output: true

  # 工作目录
  working_dir: .

# 历史记录配置
history:
  # 历史记录文件路径
  path: data/history.json

  # 最大历史记录数
  max_records: 1000

  # 是否启用历史记录
  enabled: true

# 缓存配置
cache:
  # 是否启用缓存
  enabled: true

  # 缓存有效期（秒）
  ttl: 600

  # 缓存大小限制
  max_size: 100

# 日志配置
logging:
  # 日志级别: DEBUG, INFO, WARNING, ERROR
  level: INFO

  # 日志文件路径
  file: logs/nanobot.log

  # 是否输出到控制台
  console: true

# 界面配置
ui:
  # 主题: light, dark
  theme: dark

  # 提示符
  prompt: "> "

  # 是否高亮命令
  highlight_command: true
```

### 环境变量

支持在配置文件中使用环境变量引用，格式为 `${VAR_NAME}`：

```yaml
ai:
  models:
    - api_key: ${OPENAI_API_KEY}
```

**常用环境变量**:
- `OPENAI_API_KEY`: OpenAI API 密钥
- `ANTHROPIC_API_KEY`: Anthropic API 密钥
- `OLLAMA_HOST`: Ollama 服务地址（默认：`http://localhost:11434`）

## 知识库格式

### 命令数据结构

```json
{
  "commands": [
    {
      "id": "cmd-001",
      "name": "ls",
      "type": "system",
      "description": "列出目录内容",
      "keywords": ["list", "directory", "files", "目录", "文件", "列表"],
      "command_template": "ls {options} {path}",
      "parameters": [
        {
          "name": "path",
          "description": "目录路径",
          "required": false,
          "default": "."
        },
        {
          "name": "options",
          "description": "选项参数",
          "required": false,
          "default": "-la",
          "choices": ["-l", "-la", "-a", "-h"]
        }
      ],
      "examples": [
        "ls -la /home/user",
        "ls -la",
        "ls -h /var/log"
      ],
      "aliases": ["dir", "list"],
      "tags": ["file", "directory", "basic"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "categories": [
    {
      "id": "cat-001",
      "name": "文件操作",
      "description": "与文件和目录相关的命令",
      "parent_id": null
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `id` | string | 是 | 命令唯一标识符 |
| `name` | string | 是 | 命令名称 |
| `type` | string | 是 | 命令类型：`system` 或 `custom` |
| `description` | string | 是 | 命令功能描述 |
| `keywords` | array | 是 | 用于匹配的关键词（支持中英文） |
| `command_template` | string | 是 | 命令模板，使用 `{param}` 作为参数占位符 |
| `parameters` | array | 否 | 命令参数定义 |
| `examples` | array | 否 | 使用示例 |
| `aliases` | array | 否 | 命令别名 |
| `tags` | array | 否 | 分类标签 |
| `created_at` | string | 是 | 创建时间（ISO 8601） |
| `updated_at` | string | 是 | 更新时间（ISO 8601） |

## 历史记录格式

### 历史记录数据结构

```json
{
  "records": [
    {
      "id": "hist-001",
      "user_input": "列出当前目录的所有文件",
      "recommended_commands": [
        {
          "command_id": "cmd-001",
          "command": "ls -la",
          "similarity": 0.95,
          "selected": true
        }
      ],
      "executed_command": "ls -la",
      "exit_code": 0,
      "output": "drwxr-xr-x  2 user user 4096 Jan  1 00:00 .",
      "error": null,
      "model_used": "ollama:llama3",
      "executed_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `id` | string | 是 | 记录唯一标识符 |
| `user_input` | string | 是 | 用户原始输入 |
| `recommended_commands` | array | 是 | 推荐的命令列表 |
| `executed_command` | string | 否 | 实际执行的命令 |
| `exit_code` | integer | 否 | 命令退出码 |
| `output` | string | 否 | 命令输出 |
| `error` | string | 否 | 错误信息 |
| `model_used` | string | 是 | 使用的 AI 模型 |
| `executed_at` | string | 是 | 执行时间（ISO 8601） |

## AI 模型接口

### Ollama API

**端点**: `POST /api/generate`

**请求格式**:
```json
{
  "model": "llama3",
  "prompt": "用户的自然语言输入",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "num_predict": 500
  }
}
```

**响应格式**:
```json
{
  "response": "AI 的分析结果",
  "done": true,
  "context": [1, 2, 3, 4, 5]
}
```

### OpenAI API

**端点**: `POST /v1/chat/completions`

**请求格式**:
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "你是一个命令行助手..."
    },
    {
      "role": "user",
      "content": "用户的自然语言输入"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
```

**响应格式**:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "AI 的分析结果"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## 输出格式

### 命令推荐输出

```
🤖 根据您的输入，我推荐以下命令：

[1] ls -la
    描述: 列出目录内容（包括隐藏文件）
    匹配度: 95%
    示例: ls -la /home/user

[2] ls -h
    描述: 以人类可读格式列出目录内容
    匹配度: 88%
    示例: ls -h /var/log

[3] find . -type f
    描述: 查找当前目录下的所有文件
    匹配度: 76%
    示例: find . -type f -name "*.log"

请选择要执行的命令 [1-3]，或输入 'n' 取消: _
```

### 命令执行输出

```
🚀 执行命令: ls -la

drwxr-xr-x  2 user user 4096 Jan  1 00:00 .
drwxr-xr-x 10 user user 4096 Jan  1 00:00 ..
-rw-r--r--  1 user user   42 Jan  1 00:00 file.txt
-rw-r--r--  1 user user  123 Jan  1 00:00 script.py

✅ 命令执行成功 (退出码: 0)
```

### 错误输出

```
❌ 错误: 命令执行失败

错误信息: bash: nonexistent-command: command not found

建议:
- 请检查命令名称是否正确
- 使用 'which <command>' 查看命令是否存在
- 尝试使用 /help 查看可用命令
```
