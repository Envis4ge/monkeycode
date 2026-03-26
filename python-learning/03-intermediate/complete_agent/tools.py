"""
工具系统 — Agent 可调用的工具集合
=================================
三个安全工具: 计算器、网页搜索、文件读取
"""

import os
import json
import re


def calculator(expression):
    """
    安全计算器
    
    限制:
    - 只允许数字和基本运算符
    - 禁止调用函数、导入模块
    - 禁止访问属性
    """
    # 白名单字符
    allowed = set('0123456789+-*/.() %')
    if not all(c in allowed for c in expression):
        return "错误: 表达式包含不允许的字符"
    
    # 禁止危险模式
    dangerous = ['__', 'import', 'exec', 'eval', 'open', 'os', 'sys']
    for d in dangerous:
        if d in expression.lower():
            return f"错误: 禁止使用 {d}"
    
    try:
        result = eval(expression)
        return f"{result}"
    except ZeroDivisionError:
        return "错误: 除以零"
    except Exception as e:
        return f"计算错误: {e}"


def web_search(query):
    """
    模拟网页搜索
    
    实际项目中替换为:
    - Google Search API
    - Bing Search API
    - SerpAPI
    - DuckDuckGo API
    """
    # 模拟知识库
    knowledge = {
        "python": "Python是一种高级编程语言，由Guido van Rossum创建。特点：简洁、可读性强、生态丰富。",
        "机器学习": "机器学习是AI的子领域，让计算机从数据中学习规律。主要方法：监督学习、无监督学习、强化学习。",
        "langchain": "LangChain是一个用于构建LLM应用的Python框架，支持链式调用、工具使用、记忆管理。",
        "agent": "AI Agent是能自主执行任务的智能体，通常包含推理、工具调用、记忆管理能力。",
        "rag": "RAG(检索增强生成)结合了信息检索和文本生成，先检索相关文档再生成回答，减少幻觉。",
    }
    
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return f"搜索结果: {value}"
    
    return f"搜索结果: 未找到关于 '{query}' 的具体信息。建议使用更具体的关键词。"


def file_read(filepath):
    """
    安全的文件读取
    
    安全限制:
    - 只能读取当前目录下的文件
    - 禁止读取敏感文件
    - 限制读取大小
    """
    # 安全检查
    abs_path = os.path.abspath(filepath)
    current_dir = os.path.abspath('.')
    
    if not abs_path.startswith(current_dir):
        return "错误: 只能读取当前目录下的文件"
    
    # 禁止读取敏感文件
    blocked = ['.env', '.ssh', 'passwd', 'shadow', 'id_rsa', '.key']
    filename = os.path.basename(abs_path).lower()
    for b in blocked:
        if b in filename:
            return f"错误: 禁止读取敏感文件 {filename}"
    
    # 检查扩展名
    allowed_ext = ['.txt', '.md', '.py', '.json', '.csv', '.log']
    ext = os.path.splitext(filepath)[1]
    if ext not in allowed_ext:
        return f"错误: 不支持的文件类型 {ext}"
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read(10000)  # 限制10KB
        
        lines = content.count('\n') + 1
        return f"文件: {filepath} ({lines} 行, {len(content)} 字符)\n---\n{content}"
    except FileNotFoundError:
        return f"错误: 文件不存在: {filepath}"
    except Exception as e:
        return f"读取错误: {e}"


# ============ 工具定义 ============

TOOLS = [
    {
        "name": "calculator",
        "description": "执行数学计算。输入数学表达式，返回计算结果。",
        "func": calculator,
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3 * 4', '100 / 3'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "web_search",
        "description": "搜索网页信息。输入搜索关键词，返回搜索结果。",
        "func": web_search,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "file_read",
        "description": "读取文件内容。输入文件路径，返回文件内容。",
        "func": file_read,
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "文件路径（相对路径）"
                }
            },
            "required": ["filepath"]
        }
    }
]


def get_tool_descriptions():
    """返回工具描述字符串"""
    lines = []
    for t in TOOLS:
        lines.append(f"- {t['name']}: {t['description']}")
    return "\n".join(lines)
