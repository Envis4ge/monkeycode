# AI 应用开发学习代码

按难度分 5 个阶段，从入门到生产级项目。

## 目录结构

```
python-learning/
├── 01-entry-level/     # 入门：手写神经网络核心组件
├── 02-basics/          # 基础：模型推理与优化
├── 03-intermediate/    # 中级：Agent 开发核心技术
│   └── complete_agent/ # 完整 Agent 项目
├── 04-advanced/        # 进阶：RAG / 工作流 / 低代码
└── 05-production/      # 高级：多Agent协作 / 评估 / 部署
```

## 阶段说明

### 01 - 入门：神经网络基础
| 文件 | 内容 |
|------|------|
| `micrograd.py` | 手写自动微分引擎，理解反向传播 |
| `nanogpt.py` | 从零实现 GPT，理解 Transformer |
| `makemore.py` | 字符级语言模型，理解序列生成 |

### 02 - 基础：模型推理
| 文件 | 内容 |
|------|------|
| `ollama_api.py` | Ollama API 调用与集成 |
| `quantization_experiment.py` | 模型量化实验（INT8/INT4） |
| `inference_optimization.py` | 推理优化技术（KV Cache等） |

### 03 - 中级：Agent 开发
| 文件 | 内容 |
|------|------|
| `function_calling.py` | Function Calling 机制详解 |
| `memory_management.py` | Agent 记忆管理策略 |
| `react_agent.py` | ReAct 模式实现推理+行动循环 |
| `complete_agent/` | 完整 Agent 项目（含工具、配置、Demo） |

### 04 - 进阶：RAG 与工作流
| 文件 | 内容 |
|------|------|
| `langchain_rag.py` | LangChain RAG 实现 |
| `rag_core.py` | RAG 核心原理与优化 |
| `langgraph_workflow.py` | LangGraph 工作流编排 |
| `dify_guide.py` | Dify 低代码平台指南 |

### 05 - 高级：生产级项目
| 文件 | 内容 |
|------|------|
| `auto_gen_collab.py` | AutoGen 多Agent协作框架 |
| `eval_framework.py` | LLM 评估框架设计 |
| `prod_deployment.py` | 生产环境部署方案 |
