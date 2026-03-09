# 开发指南

## 项目目的

智能终端系统是一个基于 AI 的命令行增强工具，旨在通过自然语言理解降低终端使用门槛，提高用户效率。它作为用户与操作系统之间的智能桥梁，帮助用户快速找到并执行合适的命令。

**核心职责**:
- 自然语言理解：使用 AI 模型分析用户意图
- 智能命令推荐：从知识库中筛选并推荐合适的命令
- 安全执行：在用户确认后执行命令
- 历史记录：记录和查询命令执行历史

**相关系统**:
- Ollama 服务 - 本地 AI 模型提供者
- OpenAI/Anthropic API - 云端 AI 模型提供者
- Linux/Unix Shell - 命令执行环境

## 环境搭建

### 前置条件

- Python 3.9 或更高版本
- pip 包管理器
- Git

### 可选依赖

- Ollama 服务（用于本地 AI 模型）
- OpenAI API 密钥（用于云端模型）
- Anthropic API 密钥（用于云端模型）

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/learn_nanobot.git
cd learn_nanobot

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp config.yaml.example config.yaml

# 编辑配置文件，填入你的配置
nano config.yaml
```

### 环境变量

| 变量 | 必需 | 描述 | 示例 |
|------|------|------|------|
| `OPENAI_API_KEY` | 否 | OpenAI API 密钥 | `sk-...` |
| `ANTHROPIC_API_KEY` | 否 | Anthropic API 密钥 | `sk-ant-...` |
| `OLLAMA_HOST` | 否 | Ollama 服务地址 | `http://localhost:11434` |
| `PYTHONPATH` | 否 | Python 模块路径 | `/path/to/learn_nanobot` |

⚠️ **绝不提交密钥**。使用 `.env` 文件或配置文件中的环境变量引用。

### 运行

```bash
# 开发模式
python -m learn_nanobot

# 测试 AI 模型连接
python -m learn_nanobot --test-model

# 查看帮助
python -m learn_nanobot --help

# 运行测试
pytest

# 运行测试并显示覆盖率
pytest --cov=learn_nanobot --cov-report=html
```

### 本地开发 Ollama 设置

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull llama3
ollama pull mistral

# 测试 Ollama
ollama run llama3 "Hello, world!"
```

## 开发工作流

### 代码质量工具

| 工具 | 命令 | 目的 |
|------|------|------|
| Black | `black .` | 代码格式化 |
| Flake8 | `flake8 .` | 代码检查 |
| MyPy | `mypy .` | 类型检查 |
| pytest | `pytest` | 单元/集成测试 |

### 提交前检查

这些会在提交时自动运行（通过 pre-commit hooks）：
1. Black 代码格式化
2. Flake8 代码检查
3. MyPy 类型检查
4. Pytest 单元测试

手动运行：
```bash
# 安装 pre-commit
pip install pre-commit

# 安装 hooks
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

### 分支策略

- `main` - 生产就绪代码
- `develop` - 开发分支
- `feature/*` - 新功能
- `fix/*` - Bug 修复
- `refactor/*` - 代码重构

### Pull Request 流程

1. 从 `main` 创建功能分支
2. 编写代码和测试
3. 运行 `pre-commit run --all-files`
4. 创建 PR 并填写描述
5. 处理审查反馈
6. 合并到 `main`

## 常见任务

### 添加新的 AI 模型提供商

**需修改的文件**:
1. `core/ai/base.py` - 定义新的模型类（继承 `BaseAIModel`）
2. `core/ai/provider.py` - 注册新模型
3. `config/schema.py` - 添加配置 Schema
4. `tests/unit/test_ai.py` - 添加测试

**步骤**:
1. 在 `core/ai/` 下创建新文件（如 `custom_ai.py`）
2. 继承 `BaseAIModel` 类，实现必要的方法：
   - `async def analyze(self, input: str) -> dict`
   - `async def test_connection(self) -> bool`
3. 在 `core/ai/provider.py` 中注册新模型
4. 在配置 Schema 中添加新模型的配置项
5. 编写单元测试
6. 更新文档

**示例提交**: `feat(ai): add support for custom AI provider`

### 添加新的命令类型到知识库

**需修改的文件**:
1. `data/knowledge.json` - 添加新命令
2. `core/kb/command.py` - 如果需要新的命令类型定义
3. `tests/integration/test_kb.py` - 添加测试

**步骤**:
1. 在 `data/knowledge.json` 中添加新命令条目
2. 按照命令数据结构格式填写字段
3. 如果需要新的命令类型，在 `core/kb/command.py` 中定义
4. 编写集成测试验证命令可用性
5. 更新文档

**示例提交**: `feat(kb): add docker command type to knowledge base`

### 添加新的交互式命令

**需修改的文件**:
1. `cli/interactive.py` - 添加命令处理器
2. `cli/main.py` - 注册命令
3. `tests/unit/test_cli.py` - 添加测试

**步骤**:
1. 在 `cli/interactive.py` 中定义新的命令处理函数
2. 使用装饰器或注册机制将命令添加到命令列表
3. 实现命令逻辑
4. 添加帮助文本
5. 编写单元测试
6. 更新文档

**示例提交**: `feat(cli): add /clear command to interactive mode`

### 优化命令推荐算法

**需修改的文件**:
1. `core/recommender/ranker.py` - 修改排序算法
2. `core/recommender/selector.py` - 修改选择逻辑
3. `tests/unit/test_recommender.py` - 更新测试

**步骤**:
1. 分析当前算法的瓶颈
2. 设计新的算法或改进方案
3. 实现新算法
4. 编写单元测试
5. 运行性能测试对比
6. 更新文档

**示例提交**: `perf(recommender): improve ranking algorithm speed by 50%`

### 添加新的配置项

**需修改的文件**:
1. `config.yaml.example` - 添加示例配置
2. `config/schema.py` - 添加配置 Schema
3. `config/settings.py` - 添加配置加载逻辑
4. `.monkeycode/docs/INTERFACES.md` - 更新文档

**步骤**:
1. 在 `config/schema.py` 中定义新的配置项
2. 在 `config/settings.py` 中添加加载逻辑
3. 在 `config.yaml.example` 中添加示例
4. 编写单元测试
5. 更新文档

**示例提交**: `feat(config): add max_retries configuration option`

### 修复 Bug

**流程**:
1. 编写复现 bug 的失败测试
2. 在代码中定位根因
3. 用最小改动修复
4. 验证测试通过
5. 检查其他地方是否有类似问题

**示例提交**: `fix(executor): handle timeout errors gracefully`

## 编码规范

### 文件组织
- 每个模块一个目录
- 相关文件放在同一目录
- `__init__.py` 定义公开接口

### 命名

| 类型 | 约定 | 示例 |
|------|------|------|
| 文件 | snake_case | `command_executor.py` |
| 类 | PascalCase | `CommandExecutor` |
| 函数 | snake_case | `execute_command` |
| 常量 | SCREAMING_SNAKE | `MAX_TIMEOUT` |
| 私有成员 | 前缀下划线 | `_internal_method` |

### 类型注解

```python
# 推荐：使用类型注解
async def analyze_input(input: str, model: AIModel) -> AnalysisResult:
    """分析用户输入并返回结果。"""
    result = await model.analyze(input)
    return result

# 避免：缺少类型注解
async def analyze_input(input, model):
    result = await model.analyze(input)
    return result
```

### 错误处理

```python
# 推荐：特定错误类型
raise ModelNotAvailableError(f"Model {model_name} is not available")

# 推荐：捕获特定异常
try:
    result = await model.analyze(input)
except ModelTimeoutError as e:
    logger.error(f"Model timeout: {e}")
    raise

# 避免：通用错误
raise Exception("Something went wrong")
```

### 异步编程

```python
# 推荐：使用 async/await
async def process_command(command: str) -> Result:
    output = await executor.run(command)
    return Result(output=output)

# 推荐：使用 asyncio.gather 并发执行
results = await asyncio.gather(*[task1, task2, task3])
```

### 日志

```python
import logging

logger = logging.getLogger(__name__)

# 推荐：包含上下文
logger.info("Command executed", command=cmd, exit_code=code)

# 使用适当级别
logger.debug()  # 开发详情
logger.info()   # 正常操作
logger.warning() # 可恢复问题
logger.error()  # 需要关注的故障
logger.critical() # 严重错误
```

### 测试

```python
# 推荐：使用 pytest
import pytest

from learn_nanobot.core.nlu import InputAnalyzer

@pytest.mark.asyncio
async def test_analyze_input():
    analyzer = InputAnalyzer(model=mock_model)
    result = await analyzer.analyze("列出文件")
    assert result.intent == "list_files"

# 推荐：使用 fixture
@pytest.fixture
async def analyzer():
    model = MockModel()
    return InputAnalyzer(model=model)

# 推荐：描述性测试名
def should_return_empty_list_when_no_matches():
    # 测试实现
    pass
```

## 性能优化

### 缓存策略

```python
# 使用 functools.lru_cache 缓存函数结果
from functools import lru_cache

@lru_cache(maxsize=128)
def load_command_metadata(command: str) -> dict:
    """加载命令元数据并缓存结果。"""
    # 加载逻辑
    return metadata
```

### 并发处理

```python
# 使用 asyncio.Semaphore 限制并发
semaphore = asyncio.Semaphore(5)

async def process_with_limit(task_id: int):
    async with semaphore:
        await process(task_id)
```

### 批量操作

```python
# 批量处理命令
async def batch_execute(commands: List[str]) -> List[Result]:
    tasks = [execute(cmd) for cmd in commands]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 调试

### 启用调试日志

```bash
# 设置日志级别为 DEBUG
LOG_LEVEL=DEBUG python -m learn_nanobot
```

### 使用 pdb 调试

```python
import pdb

def process_command(command: str):
    # 在此处设置断点
    pdb.set_trace()
    result = execute(command)
    return result
```

### 性能分析

```bash
# 使用 cProfile 分析性能
python -m cProfile -s tottime -m learn_nanobot

# 使用 memory_profiler 分析内存
python -m memory_profiler -m learn_nanobot
```

## 部署

### 打包为可执行文件

```bash
# 使用 PyInstaller
pip install pyinstaller
pyinstaller --onefile main.py -n nanobot

# 生成的可执行文件在 dist/nanobot
```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "learn_nanobot"]
```

```bash
# 构建镜像
docker build -t nanobot:latest .

# 运行容器
docker run -it --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  nanobot:latest
```

## 修改建议区域

**安全起步点**（低风险修改）:
- 添加新的系统命令到知识库
- 改进日志输出格式
- 优化错误提示信息
- 添加新的单元测试
- 改进文档和注释

**中等风险区域**:
- 优化推荐算法
- 改进缓存策略
- 添加新的配置项
- 优化性能瓶颈

**高风险区域**:
- 修改核心 NLU 逻辑
- 更改 AI 模型接口
- 修改命令执行逻辑
- 更改数据格式
