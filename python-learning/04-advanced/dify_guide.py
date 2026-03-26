"""
Dify 工作流配置指南 — 低代码搭建 LLM 应用
============================================
目标：了解 Dify 平台的核心概念和配置方法

Dify 是什么:
- 开源 LLM 应用开发平台
- 可视化工作流编排
- 支持 RAG、Agent、对话等应用类型
- 支持多种模型（OpenAI、Ollama、通义千问等）
"""

# ============ Dify 应用类型 ============

DIFY_APP_TYPES = """
Dify 支持 4 种应用类型:

1. 聊天助手 (Chatbot)
   - 最简单的应用类型
   - 支持多轮对话 + 知识库
   - 适合：客服、问答系统

2. 文本生成 (Text Generation)
   - 单次输入 → 单次输出
   - 支持变量填充
   - 适合：写作、翻译、摘要

3. Agent (智能体)
   - 自主决策 + 工具调用
   - 支持 ReAct 模式
   - 适合：复杂任务自动化

4. 工作流 (Workflow)
   - 可视化编排复杂流程
   - 支持条件分支、循环、并行
   - 适合：多步骤业务流程
"""


# ============ Dify vs 代码开发 ============

COMPARISON = """
Dify vs LangChain 代码开发 对比:

维度            Dify               LangChain 代码
─────────────────────────────────────────────────
学习曲线        低                 高
开发速度        快（拖拽配置）     中（写代码）
灵活性          中（受限于平台）   高（完全自定义）
部署方式        Docker 自部署      自定义部署
适合场景        快速原型           生产级定制
代码控制        无（配置驱动）     完全控制
社区支持        活跃               最大
模型支持        多种（需配置）     多种
"""

RECOMMENDATION = """
推荐策略:

1. 需求验证阶段 → 用 Dify 快速搭建原型
2. 确认需求后 → 核心逻辑用代码实现
3. 复杂场景 → Dify + 自定义代码混合
"""


# ============ Dify RAG 配置 ============

DIFY_RAG_CONFIG = """
Dify RAG 知识库配置步骤:

1. 创建知识库
   - 上传文档（PDF/TXT/Markdown/Word）
   - 选择分段模式

2. 分段设置
   - 自动分段：按段落/标题智能分割
   - 自定义分段：手动设置 chunk 大小
   - 推荐: 500 tokens/chunk, 50 tokens 重叠

3. 索引方式
   - 高质量模式: 使用 Embedding 模型（推荐）
   - 经济模式: 使用关键词索引

4. 检索设置
   - 语义检索: 基于向量相似度
   - 全文检索: 基于关键词匹配
   - 混合检索: 两者结合（推荐）
   - Rerank: 对结果重排序（需配置 Rerank 模型）

5. 在应用中引用知识库
   - 添加"知识检索"节点
   - 连接到 LLM 节点
   - 在 Prompt 中引用 {#context#}
"""


# ============ Dify Agent 配置 ============

DIFY_AGENT_CONFIG = """
Dify Agent 配置步骤:

1. 创建 Agent 应用
   - 选择"Agent"类型
   - 选择 LLM 模型

2. 配置工具
   - 内置工具: Google搜索、维基百科、网页抓取等
   - 自定义工具: 添加 API 工具
   - 工具描述要清晰（影响 LLM 选择工具的准确性）

3. 设置系统提示
   - 描述 Agent 角色和行为
   - 说明可用工具及其用途
   - 设置安全边界

4. 调试和测试
   - 使用内置调试面板
   - 观察 Agent 的推理过程
   - 调整 Prompt 和工具配置
"""


# ============ Dify 工作流示例 ============

DIFY_WORKFLOW = """
Dify 工作流示例 — 智能客服:

                    [开始]
                      ↓
                [问题分类器]
               ↙     ↓     ↘
          [知识库] [API查询] [人工转接]
               ↘     ↓     ↙
                 [LLM 生成回答]
                      ↓
                    [结束]

节点类型:
- 开始: 接收用户输入
- LLM: 调用大语言模型
- 知识检索: 从知识库检索相关文档
- 条件分支: 根据条件走不同路径
- HTTP 请求: 调用外部 API
- 代码执行: 运行自定义 Python/JS 代码
- 变量聚合: 合并多个节点的输出
- 结束: 返回最终结果
"""


# ============ Dify API 调用 ============

DIFY_API_CODE = """
# 通过 API 调用 Dify 应用

import requests

DIFY_BASE_URL = "https://your-dify-instance.com"
API_KEY = "app-xxxxxxxx"

def chat(message, conversation_id=None):
    url = f"{DIFY_BASE_URL}/v1/chat-messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": message,
        "response_mode": "streaming",
        "user": "user-001",
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            data = line.decode().removeprefix("data: ")
            if data != "[DONE]":
                import json
                chunk = json.loads(data)
                print(chunk.get("answer", ""), end="", flush=True)

chat("你好，我想了解一下退款政策")
"""


# ============ 演示 ============

if __name__ == '__main__':
    print("=" * 60)
    print("Dify 工作流配置指南")
    print("=" * 60)
    
    print(DIFY_APP_TYPES)
    print(COMPARISON)
    print(RECOMMENDATION)
    print(DIFY_RAG_CONFIG)
    print(DIFY_AGENT_CONFIG)
    print(DIFY_WORKFLOW)
    print("\n" + "=" * 60)
    print("Dify API 调用示例代码")
    print("=" * 60)
    print(DIFY_API_CODE)
