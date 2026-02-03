# 开发指南

## 项目目的

smart_term 是一个智能终端增强工具，通过集成AI能力为新手用户提供友好的命令行使用体验。它在命令行工具生态中担任"智能辅助层"的角色，帮助用户降低学习门槛、提高使用效率。

 **核心职责**:
- 提供自然语言到命令的转换能力，基于知识库筛选
- 实时解释和说明命令的作用
- 智能推荐和补全命令
- 管理和检索命令历史
- 维护结构化的命令知识库
- 支持多AI模型配置和自动切换

**相关系统**:
- Shell（bash/zsh/fish）- 底层命令执行环境
- Ollama - 本地AI模型服务
- 云端AI服务（OpenAI/Anthropic）- 提供智能能力
- 终端模拟器 - 用户交互界面

## 环境搭建

 ### 前置条件

- Python 3.10 或更高版本
- pip（Python包管理器）
- Git（版本控制）
- Ollama（可选，用于本地AI模型）

```bash
# 安装Ollama（如果使用本地模型）
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama3
```

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/smart_term.git
cd smart_term

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install --break-system-packages -r requirements.txt

# 安装开发依赖
pip install --break-system-packages -r requirements-dev.txt

# 配置环境
cp config/default.toml ~/.smart_term/config.toml
# 编辑配置文件填入你的值
```

### 环境变量

 | 变量 | 必需 | 描述 | 示例 |
|------|------|------|------|
| `OPENAI_API_KEY` | 使用OpenAI时 | OpenAI API密钥 | `sk-...` |
| `ANTHROPIC_API_KEY` | 使用Anthropic时 | Anthropic API密钥 | `sk-ant-...` |
| `OLLAMA_HOST` | 使用Ollama时 | Ollama服务地址 | `http://localhost:11434` |
| `SMART_TERM_CONFIG` | 否 | 配置文件路径 | `~/.smart_term/config.toml` |
| `SMART_TERM_DEBUG` | 否 | 启用调试模式 | `true` |

⚠️ **绝不提交密钥**。使用环境变量或加密的密钥管理器。

### 运行

```bash
# 开发模式
python -m smart_term

# 带调试日志
python -m smart_term --debug

 # 指定AI服务
python -m smart_term --ai ollama
python -m smart_term --ai openai
python -m smart_term --ai anthropic

# 列出可用模型
python -m smart_term --list-models

# 启动Ollama服务（如果使用本地模型）
ollama serve &

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 代码检查
flake8 src/
mypy src/
black --check src/
```

## 开发工作流

### 代码质量工具

| 工具 | 命令 | 目的 |
|------|------|------|
| pytest | `pytest` | 单元测试和集成测试 |
| pytest-cov | `pytest --cov` | 测试覆盖率 |
| flake8 | `flake8 src/` | 代码风格检查 |
| black | `black src/` | 代码格式化 |
| mypy | `mypy src/` | 类型检查 |
| isort | `isort src/` | import排序 |

### 提交前检查

这些会在提交时自动运行：
1. 代码格式化检查（black, isort）
2. 代码风格检查（flake8）
3. 类型检查（mypy）
4. 单元测试（pytest）

手动运行全部检查：
```bash
pre-commit run --all-files
```

### 分支策略

- `main` - 生产就绪代码
- `develop` - 开发主分支
- `feature/*` - 新功能分支
- `fix/*` - Bug修复分支
- `docs/*` - 文档更新

### Pull Request 流程

1. 从 `develop` 创建功能分支
2. 编写代码和测试
3. 运行 `pre-commit run --all-files`
4. 运行 `pytest` 确保测试通过
5. 创建 PR 并填写描述模板
6. 处理审查反馈
7. 确保所有检查通过
8. 合并到 `develop`

## 常见任务

### 添加新的AI服务集成

**需修改的文件**:
1. `src/ai/new_service.py` - 实现新的AI服务
2. `src/ai/__init__.py` - 导出新服务
3. `src/ai/manager.py` - 在模型管理器中注册
4. `config/default.toml` - 添加配置项
5. `tests/ai/test_new_service.py` - 添加测试

**步骤**:
1. 创建新的AI服务类，继承 `AIService` 抽象基类
2. 实现所有抽象方法（convert_natural_language, suggest_completion, explain_command）
3. 在模型管理器中注册新服务
4. 添加配置项支持
5. 编写单元测试和集成测试
6. 更新文档

**示例提交**: `feat(ai): add Anthropic Claude integration`

### 添加新的命令补全源

**需修改的文件**:
1. `src/features/completion.py` - 添加新的补全源
2. `tests/features/test_completion.py` - 添加测试

**步骤**:
1. 实现补全源的接口
2. 在补全器中注册新源
3. 添加评分和排序逻辑
4. 编写测试用例
5. 更新文档

### 添加命令到知识库

**需修改的文件**:
1. `data/default_kb.json` - 添加默认命令
2. `src/features/kb.py` - 可能需要扩展知识库功能
3. `tests/features/test_kb.py` - 添加测试

**步骤**:
1. 在默认知识库文件中添加命令条目
2. 确保命令包含：name、command、description、category、examples、keywords
3. 验证命令格式正确
4. 测试命令搜索和筛选功能

**示例提交**: `docs(kb): add Docker commands to default knowledge base`

### 管理知识库导入导出

**需修改的文件**:
1. `src/features/kb.py` - 实现导入导出功能
2. `tests/features/test_kb.py` - 添加测试

**步骤**:
1. 实现JSON格式的导出功能
2. 实现JSON格式的导入功能，包含验证
3. 添加错误处理和去重逻辑
4. 编写测试用例

**示例提交**: `feat(kb): add import/export functionality`

### 配置模型切换与回退

**需修改的文件**:
1. `src/ai/manager.py` - 实现模型管理器
2. `config/default.toml` - 添加多模型配置
3. `src/config/settings.py` - 添加配置验证
4. `tests/ai/test_manager.py` - 添加测试

**步骤**:
1. 实现模型注册和优先级管理
2. 实现自动切换逻辑
3. 添加模型状态监控
4. 实现模型可用性测试
5. 编写单元测试和集成测试

**示例提交**: `feat(ai): add model manager with automatic fallback`

### 配置响应缓存

**需修改的文件**:
1. `src/ai/cache.py` - 实现缓存接口
2. `src/ai/manager.py` - 集成缓存
3. `config/default.toml` - 添加缓存配置
4. `tests/ai/test_cache.py` - 添加测试

**步骤**:
1. 实现基于内存的缓存
2. 实现缓存键生成逻辑
3. 添加TTL过期机制
4. 实现缓存统计和清理
5. 编写测试用例

**示例提交**: `feat(cache): add response cache for AI services`

### 添加新的配置项

**需修改的文件**:
1. `config/default.toml` - 添加默认配置
2. `src/config/settings.py` - 添加配置验证
3. `.monkeycode/docs/INTERFACES.md` - 更新配置文档

**步骤**:
1. 在默认配置中添加新项
2. 在配置类中添加对应的属性和验证
3. 在相关代码中使用新配置
4. 更新文档说明配置项的用途

### 添加新的主题

**需修改的文件**:
1. `src/ui/theme.py` - 添加新主题定义
2. `src/ui/themes/` - 主题文件目录（可选）

**步骤**:
1. 定义主题的颜色、字体等样式
2. 在主题管理器中注册
3. 添加主题预览和切换功能
4. 编写测试确保主题正确应用

### 修复Bug

**流程**:
1. 编写复现bug的失败测试
2. 在代码中定位根因
3. 用最小改动修复
4. 验证测试通过
5. 检查其他地方是否有类似问题

**示例提交**: `fix(completion): handle empty input gracefully`

## 编码规范

### 文件组织
- 每个文件一个主要类或功能模块
- 文件以其默认导出命名
- 相关文件放在同一目录
- 使用 `__init__.py` 管理包的公开接口

### 命名

| 类型 | 约定 | 示例 |
|------|------|------|
| 文件 | snake_case | `command_history.py` |
| 类 | PascalCase | `CommandHistory` |
| 函数 | snake_case | `get_recent_commands` |
| 变量 | snake_case | `user_input` |
| 常量 | SCREAMING_SNAKE | `MAX_HISTORY_SIZE` |
| 私有成员 | 前缀下划线 | `_internal_method` |

### 错误处理

```python
# 推荐：特定错误类型
raise CommandExecutionError("Command failed with exit code 1")

# 推荐：使用日志记录错误
logger.error("Failed to execute command", command=cmd, error=str(e))

# 避免：通用错误
raise Exception("Something went wrong")
```

### 日志

```python
# 包含上下文
logger.info("Command executed", command=cmd, duration=duration)

# 使用适当级别
logger.debug()  # 开发详情
logger.info()   # 正常操作
logger.warn()   # 可恢复问题
logger.error()  # 需要关注的故障
logger.exception()  # 异常详情
```

### 异步编程

```python
# 推荐：使用asyncio处理IO密集型操作
async def fetch_suggestions(self, partial: str) -> List[str]:
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json={"input": partial})
        return await response.json()

# 推荐：正确处理异步上下文
async with database.transaction():
    await execute_command(cmd)
```

### 测试
- 测试文件: `test_*.py` 或 `*_test.py`
- 测试类: 以 `Test` 开头
- 测试方法: 以 `test_` 开头
- 使用描述性名称: `test_should_return_empty_list_when_input_is_empty`

```python
import pytest

@pytest.mark.asyncio
async def test_should_return_suggestions_when_valid_input():
    result = await completion.suggest("ls")
    assert len(result) > 0
    assert any("ls" in cmd for cmd in result)
```

### 类型注解

```python
# 推荐：使用类型注解
def search_history(
    query: str,
    limit: int = 10
) -> List[CommandRecord]:
    ...

# 推荐：使用TypedDict定义复杂类型
class CommandMetadata(TypedDict):
    exit_code: int
    duration: float
    timestamp: datetime
```

### 文档字符串

```python
def convert_natural_language(text: str, context: Dict) -> str:
    """
    将自然语言转换为命令

    Args:
        text: 自然语言文本
        context: 上下文信息，包含当前目录、历史命令等

    Returns:
        建议的命令字符串

    Raises:
        AIRequestError: 当AI服务请求失败时
        ValidationError: 当输入文本无效时

    Examples:
        >>> convert_natural_language("列出所有文件", {"cwd": "/home"})
        'ls -la'
    """
    ...
```

## 修改建议区域

以下是适合新手贡献者的安全修改区域：

1. **主题和样式** (`src/ui/theme.py`)
   - 添加新的颜色主题
   - 调整UI布局

2. **Prompt模板** (`data/prompts/`)
   - 优化自然语言转换的prompt
   - 添加特定场景的prompt

3. **配置文件** (`config/default.toml`)
   - 调整默认值
   - 添加新配置项

4. **文档** (`.monkeycode/docs/`, `README.md`)
   - 添加使用示例
   - 翻译文档
   - 补充说明

5. **测试** (`tests/`)
   - 提高测试覆盖率
   - 添加边界情况测试

## 构建与发布

### 打包

```bash
# 安装打包工具
pip install --break-system-packages build twine

# 构建
python -m build

# 检查包
twine check dist/*
```

### 发布

```bash
# 发布到PyPI
twine upload dist/*
```

### 版本管理

使用语义化版本（Semantic Versioning）：
- `MAJOR.MINOR.PATCH`
  - MAJOR：不兼容的API变更
  - MINOR：向后兼容的功能新增
  - PATCH：向后兼容的Bug修复

## 调试技巧

### 启用调试模式

```bash
python -m smart_term --debug
```

### 查看详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 使用pdb调试

```python
import pdb; pdb.set_trace()
```

### 性能分析

```bash
python -m cProfile -o profile.stats -m smart_term
python -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(20)"
```
