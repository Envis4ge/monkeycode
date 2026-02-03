# 接口定义

## 概述

本文档定义了smart_term系统的核心接口，包括命令行接口、Python API接口、配置接口和事件接口。这些接口定义了系统与外部交互的契约。

## 命令行接口 (CLI)

### 启动命令

```bash
# 启动智能终端
smart_term

# 指定配置文件
smart_term --config /path/to/config.toml

# 启用调试模式
smart_term --debug

 # 指定AI服务
smart_term --ai ollama
smart_term --ai openai
smart_term --ai anthropic

# 查看可用模型
smart_term --list-models
```

### 终端内命令

在smart_term终端中，支持以下特殊命令：

```bash
# 自然语言转命令
> 列出当前目录的所有文件

# 查看命令解释
> explain ls -la

# 搜索历史命令
> history search docker

# 查看最近命令
> history recent

 # 配置管理
> config set ai_service openai
> config get ai_service
> config list

# 知识库管理
> kb add --name "my-script" --path "~/scripts/myscript.sh" --description "My custom script"
> kb list
> kb search "docker"
> kb remove <id>
> kb import /path/to/kb.json
> kb export /path/to/kb.json

# 模型管理
> model list
> model switch <model_name>
> model status

# 退出
> exit
> quit
```

## Python API 接口

### AI服务接口

```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict

class AIService(ABC):
    """AI服务抽象接口"""

    @abstractmethod
    async def convert_natural_language(self, text: str, context: Dict) -> str:
        """
        将自然语言转换为命令

        Args:
            text: 自然语言文本
            context: 上下文信息（当前目录、历史命令等）

        Returns:
            建议的命令字符串
        """
        pass

    @abstractmethod
    async def suggest_completion(self, partial_input: str, context: Dict) -> List[str]:
        """
        提供命令补全建议

        Args:
            partial_input: 部分输入的命令
            context: 上下文信息

        Returns:
            补全建议列表，按优先级排序
        """
        pass

    @abstractmethod
    async def explain_command(self, command: str, context: Dict) -> Dict[str, str]:
        """
        解释命令

        Args:
            command: 命令字符串
            context: 上下文信息

        Returns:
            解释信息字典，包含：
            - description: 命令描述
            - parameters: 参数说明
            - examples: 使用示例
            - warnings: 警告信息
        """
        pass
```

### 命令历史接口

```python
class CommandHistory:
    """命令历史管理接口"""

    async def add(self, command: str, metadata: Optional[Dict] = None) -> None:
        """
        添加命令到历史

        Args:
            command: 命令字符串
            metadata: 元数据（执行时间、退出码等）
        """
        pass

    async def search(self, query: str, limit: int = 10) -> List[CommandRecord]:
        """
        搜索历史命令

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            命令记录列表
        """
        pass

    async def get_recent(self, limit: int = 10) -> List[CommandRecord]:
        """
        获取最近的命令

        Args:
            limit: 返回结果数量限制

        Returns:
            命令记录列表
        """
        pass

    async def get_by_id(self, record_id: int) -> Optional[CommandRecord]:
        """
        根据ID获取命令记录

        Args:
            record_id: 记录ID

        Returns:
            命令记录，如果不存在则返回None
        """
        pass
```

### 知识库接口

```python
class KnowledgeBase:
    """知识库管理接口"""

    async def add_command(self, command: CommandEntry) -> None:
        """
        添加命令到知识库

        Args:
            command: 命令条目

        Raises:
            ValidationError: 命令格式验证失败
            DuplicateError: 命令已存在
        """
        pass

    async def search(self, query: str, limit: int = 10) -> List[CommandEntry]:
        """
        搜索知识库中的命令

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的命令条目列表，按相关度排序
        """
        pass

    async def get_by_id(self, entry_id: int) -> Optional[CommandEntry]:
        """
        根据ID获取命令条目

        Args:
            entry_id: 条目ID

        Returns:
            命令条目，如果不存在则返回None
        """
        pass

    async def update_command(self, entry_id: int, command: CommandEntry) -> None:
        """
        更新命令条目

        Args:
            entry_id: 条目ID
            command: 更新的命令条目
        """
        pass

    async def delete_command(self, entry_id: int) -> None:
        """
        删除命令条目

        Args:
            entry_id: 条目ID
        """
        pass

    async def list_by_type(self, command_type: CommandType) -> List[CommandEntry]:
        """
        按类型列出命令

        Args:
            command_type: 命令类型（system或custom）

        Returns:
            该类型的所有命令条目
        """
        pass

    async def export(self, format: str = "json") -> str:
        """
        导出知识库

        Args:
            format: 导出格式（json、csv）

        Returns:
            导出的数据字符串
        """
        pass

    async def import_data(self, data: str, format: str = "json") -> int:
        """
        导入知识库

        Args:
            data: 导入的数据字符串
            format: 数据格式（json、csv）

        Returns:
            导入的条目数量
        """
        pass
```

### 模型管理器接口

```python
class ModelManager:
    """模型管理器接口，支持多模型配置和自动切换"""

    async def register_model(self, model_config: ModelConfig) -> None:
        """
        注册AI模型

        Args:
            model_config: 模型配置

        Raises:
            ConfigError: 配置无效
        """
        pass

    async def get_primary_model(self) -> AIService:
        """
        获取当前主模型

        Returns:
            主模型实例
        """
        pass

    async def get_model_by_name(self, name: str) -> Optional[AIService]:
        """
        根据名称获取模型

        Args:
            name: 模型名称

        Returns:
            模型实例，如果不存在则返回None
        """
        pass

    async def switch_model(self, model_name: str) -> None:
        """
        切换到指定模型

        Args:
            model_name: 模型名称

        Raises:
            ModelNotFoundError: 模型不存在
        """
        pass

    async def list_models(self) -> List[ModelInfo]:
        """
        列出所有模型

        Returns:
            模型信息列表
        """
        pass

    async def test_model(self, model_name: str) -> bool:
        """
        测试模型可用性

        Args:
            model_name: 模型名称

        Returns:
            是否可用
        """
        pass

    async def get_status(self) -> Dict[str, Any]:
        """
        获取模型管理器状态

        Returns:
            状态信息字典
        """
        pass
```

### 缓存接口

```python
class ResponseCache:
    """AI响应缓存接口"""

    async def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            缓存数据，如果不存在或过期则返回None
        """
        pass

    async def set(self, key: str, value: Any, ttl: int = 600) -> None:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认600秒（10分钟）
        """
        pass

    async def delete(self, key: str) -> None:
        """
        删除缓存数据

        Args:
            key: 缓存键
        """
        pass

    async def clear(self) -> None:
        """
        清空所有缓存
        """
        pass

    async def generate_key(self, service: str, method: str, input_data: str) -> str:
        """
        生成缓存键

        Args:
            service: AI服务名称
            method: 方法名称
            input_data: 输入数据

        Returns:
            缓存键
        """
        pass
```

### 配置接口

```python
class ConfigManager:
    """配置管理接口"""

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键（支持点号分隔的嵌套键）
            default: 默认值

        Returns:
            配置值
        """
        pass

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        pass

    def save(self) -> None:
        """
        保存配置到文件
        """
        pass

    def reload(self) -> None:
        """
        从文件重新加载配置
        """
        pass
```

## 事件接口

### 事件类型

```python
class EventType(Enum):
    """事件类型枚举"""
    INPUT_RECEIVED = "input_received"          # 用户输入接收
    COMMAND_EXECUTED = "command_executed"      # 命令执行
    COMMAND_FAILED = "command_failed"          # 命令失败
    SUGGESTION_SHOWN = "suggestion_shown"      # 显示建议
    HISTORY_ACCESSED = "history_accessed"      # 访问历史
    ERROR_OCCURRED = "error_occurred"           # 错误发生
```

### 事件数据

```python
class Event:
    """事件对象"""

    def __init__(self, type: EventType, data: Dict, timestamp: datetime):
        self.type = type
        self.data = data
        self.timestamp = timestamp

class EventHandler(ABC):
    """事件处理器接口"""

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """
        处理事件

        Args:
            event: 事件对象
        """
        pass

class EventBus:
    """事件总线接口"""

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理器
        """
        pass

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        取消订阅

        Args:
            event_type: 事件类型
            handler: 事件处理器
        """
        pass

    async def publish(self, event: Event) -> None:
        """
        发布事件

        Args:
            event: 事件对象
        """
        pass
```

## 配置接口

### 配置文件格式 (TOML)

```toml
# 默认配置文件示例

[terminal]
# 终端设置
theme = "default"                # 主题名称
history_size = 1000              # 历史记录保存数量
show_explanations = true         # 是否显示命令解释
enable_completion = true         # 是否启用智能补全

[ai]
# AI服务设置
# 模型优先级列表，按顺序尝试
primary_model = "ollama"         # 主模型
fallback_models = ["openai", "anthropic"]  # 备用模型

[ai.ollama]
# Ollama本地模型配置
service_url = "http://localhost:11434"     # Ollama服务地址
model = "llama3"                           # 模型名称
temperature = 0.7                         # 温度参数
max_tokens = 500                           # 最大token数
timeout = 30                               # 请求超时（秒）

[ai.openai]
# OpenAI特定配置
api_key_env = "OPENAI_API_KEY"             # API密钥环境变量名
model = "gpt-4"                            # 模型名称
temperature = 0.7                         # 温度参数
max_tokens = 500                           # 最大token数
timeout = 30                               # 请求超时（秒）
base_url = "https://api.openai.com/v1"

[ai.anthropic]
# Anthropic特定配置
api_key_env = "ANTHROPIC_API_KEY"          # API密钥环境变量名
model = "claude-3-sonnet-20240229"         # 模型名称
temperature = 0.7                         # 温度参数
max_tokens = 500                           # 最大token数
timeout = 30                               # 请求超时（秒）

[cache]
# AI响应缓存设置
enabled = true                             # 是否启用缓存
ttl = 600                                  # 缓存过期时间（秒），默认10分钟
max_size = 1000                            # 最大缓存条目数

[knowledge_base]
# 知识库设置
db_path = "~/.smart_term/knowledge.db"     # 知识库数据库路径
default_commands = "default_kb.json"        # 默认命令集文件
enable_custom_scripts = true               # 是否启用自定义脚本
script_dir = "~/.smart_term/scripts"       # 自定义脚本目录

[history]
# 历史记录设置
db_path = "~/.smart_term/history.db"
auto_save = true                 # 自动保存
enable_search = true             # 启用搜索
index_by_date = true             # 按日期索引
max_records = 1000               # 最大记录数

[logging]
# 日志设置
level = "INFO"                   # 日志级别: DEBUG, INFO, WARN, ERROR
file = "~/.smart_term/smart_term.log"
max_size = 10485760              # 日志文件最大大小（字节）
backup_count = 5                 # 保留的备份文件数

[features]
# 功能开关
nl2cmd = true                    # 自然语言转命令
explanation = true               # 命令解释
completion = true                # 智能补全
history = true                   # 命令历史
knowledge_base = true             # 知识库管理
model_fallback = true            # 模型自动切换
```

### 环境变量

| 变量名 | 描述 | 必需 | 默认值 |
|--------|------|------|--------|
| `SMART_TERM_CONFIG` | 配置文件路径 | 否 | `~/.smart_term/config.toml` |
| `SMART_TERM_HOME` | 主目录 | 否 | `~/.smart_term` |
| `OPENAI_API_KEY` | OpenAI API密钥 | 使用OpenAI时 | - |
| `ANTHROPIC_API_KEY` | Anthropic API密钥 | 使用Anthropic时 | - |
| `OLLAMA_HOST` | Ollama服务地址 | 使用Ollama时 | `http://localhost:11434` |
| `SMART_TERM_DEBUG` | 调试模式 | 否 | `false` |

## 数据模型

### CommandRecord（命令记录）

```python
class CommandRecord:
    """命令历史记录"""

    id: int                       # 唯一标识
    command: str                  # 命令文本
    timestamp: datetime            # 执行时间
    exit_code: Optional[int]      # 退出码
    duration: float               # 执行时长（秒）
    metadata: Dict                 # 元数据
    tags: List[str]                # 标签
```

### CommandSuggestion（命令建议）

```python
class CommandSuggestion:
    """命令建议"""

    command: str                  # 建议的命令
    description: str              # 命令描述
    confidence: float             # 置信度（0-1）
    source: str                   # 来源（ai/history/context）
    metadata: Dict                # 元数据
```

### CommandExplanation（命令解释）

```python
class CommandExplanation:
    """命令解释"""

    command: str                  # 命令文本
    description: str              # 功能描述
    parameters: List[Parameter]   # 参数列表
    examples: List[str]           # 使用示例
    warnings: List[str]           # 警告信息
    related_commands: List[str]    # 相关命令

class Parameter:
    """命令参数"""

    name: str                     # 参数名称
    short: Optional[str]          # 短选项
    long: Optional[str]           # 长选项
    description: str              # 参数描述
    required: bool               # 是否必需
    default: Optional[Any]        # 默认值
```

### CommandEntry（知识库条目）

```python
class CommandType(Enum):
    """命令类型枚举"""
    SYSTEM = "system"             # 系统命令
    CUSTOM = "custom"             # 自定义脚本

class CommandEntry:
    """知识库命令条目"""

    id: int                       # 唯一标识
    name: str                     # 命令名称
    type: CommandType             # 命令类型
    command: str                  # 完整命令或脚本路径
    description: str              # 命令描述
    category: str                 # 分类（如：文件管理、网络、进程等）
    parameters: List[Dict]        # 参数说明
    examples: List[str]          # 使用示例
    keywords: List[str]           # 搜索关键词
    created_at: datetime          # 创建时间
    updated_at: datetime          # 更新时间
```

### ModelConfig（模型配置）

```python
class ModelType(Enum):
    """模型类型枚举"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class ModelConfig:
    """AI模型配置"""

    name: str                     # 模型名称（唯一标识）
    type: ModelType               # 模型类型
    model_name: str               # 实际模型名称
    priority: int                 # 优先级（数字越小优先级越高）
    enabled: bool                 # 是否启用
    temperature: float            # 温度参数
    max_tokens: int               # 最大token数
    timeout: int                  # 请求超时（秒）

    # Ollama特定配置
    service_url: Optional[str]    # Ollama服务地址

    # 云端模型特定配置
    api_key_env: Optional[str]    # API密钥环境变量名
    base_url: Optional[str]       # API基础URL
```

### ModelInfo（模型信息）

```python
class ModelStatus(Enum):
    """模型状态枚举"""
    AVAILABLE = "available"       # 可用
    UNAVAILABLE = "unavailable"   # 不可用
    TESTING = "testing"           # 测试中

class ModelInfo:
    """模型信息"""

    name: str                     # 模型名称
    type: ModelType               # 模型类型
    status: ModelStatus           # 当前状态
    priority: int                 # 优先级
    is_primary: bool              # 是否为主模型
    last_used: Optional[datetime] # 最后使用时间
    error_message: Optional[str]   # 错误信息（如果有）
```

## WebSocket 接口（未来扩展）

如果未来需要支持远程会话或Web界面，可以添加WebSocket接口：

```python
class WebSocketInterface:
    """WebSocket接口"""

    async def connect(self) -> None:
        """建立连接"""
        pass

    async def send_command(self, command: str) -> None:
        """发送命令"""
        pass

    async def receive_output(self) -> str:
        """接收输出"""
        pass

    async def get_suggestions(self, partial_input: str) -> List[str]:
        """获取补全建议"""
        pass

    async def disconnect(self) -> None:
        """断开连接"""
        pass
```
