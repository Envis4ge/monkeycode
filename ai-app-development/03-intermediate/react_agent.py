"""
ReAct Agent — 推理+行动循环
===========================
目标：实现 Reasoning(推理) + Acting(行动) 的 Agent 循环

核心循环:
  Thought: 我需要做某事
  Action: 调用工具
  Observation: 工具返回结果
  Thought: 基于结果继续推理
  Final Answer: 最终回答
"""

import re
import json
from typing import Optional

# ============ 工具定义 ============

class Tool:
    """工具基类"""
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func
    
    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def calculator(expression):
    """安全的计算器"""
    # 只允许数字和基本运算符
    allowed = set('0123456789+-*/.() ')
    if not all(c in allowed for c in expression):
        return "错误：包含不允许的字符"
    try:
        result = eval(expression)
        return f"{result}"
    except Exception as e:
        return f"计算错误: {e}"


def search(query):
    """模拟搜索（实际项目中接入真实搜索API）"""
    fake_db = {
        "Python": "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年发布。",
        "GPT": "GPT (Generative Pre-trained Transformer) 是 OpenAI 开发的大语言模型系列。",
        "机器学习": "机器学习是AI的子领域，让计算机从数据中学习规律。",
        "transformer": "Transformer 是2017年提出的注意力机制架构，是现代LLM的基础。",
    }
    for key, val in fake_db.items():
        if key.lower() in query.lower():
            return val
    return f"未找到关于 '{query}' 的信息"


def get_tools():
    """返回可用工具列表"""
    return [
        Tool("calculator", "执行数学计算，输入数学表达式如 '2+3*4'", calculator),
        Tool("search", "搜索信息，输入搜索关键词", search),
    ]


# ============ LLM 模拟 ============

class MockLLM:
    """
    模拟 LLM 响应。实际项目中替换为真实 API 调用。
    用于演示 ReAct 循环的完整流程。
    """
    
    def __init__(self):
        self.tools = {t.name: t for t in get_tools()}
    
    def think(self, question, scratchpad):
        """模拟 LLM 的思考过程"""
        q_lower = question.lower()
        
        # 已经有 Observation 了 → 给出 Final Answer
        if "Observation:" in scratchpad:
            # 提取最后一条 Observation 的内容
            obs_lines = [l for l in scratchpad.split('\n') if l.startswith('Observation:')]
            if obs_lines:
                obs_content = obs_lines[-1].replace('Observation:', '').strip()
                return f"Thought: 我已经得到了结果\nFinal Answer: {obs_content}"
        
        # 需要计算
        if any(c in q_lower for c in ['计算', '等于', '+', '-', '*', '/']):
            nums = re.findall(r'[\d.]+', question)
            if len(nums) >= 2:
                op = '+' if '+' in question else '-' if '-' in question else '*' if '*' in question else '/' if '/' in question else '+'
                expr = f"{nums[0]} {op} {nums[1]}"
                return f"Thought: 我需要计算 {expr}\nAction: calculator(\"{expr}\")"
        
        # 需要搜索
        if any(w in q_lower for w in ['什么是', '介绍', '搜索', '了解']):
            topic = question.replace('什么是', '').replace('介绍', '').replace('搜索', '').strip()
            return f"Thought: 我需要搜索关于'{topic}'的信息\nAction: search(\"{topic}\")"
        
        # 直接回答
        return f"Thought: 我可以直接回答这个问题\nFinal Answer: {question}"


# ============ ReAct Agent ============

class ReActAgent:
    """
    ReAct Agent：推理-行动循环
    
    流程:
    1. 接收问题
    2. LLM 思考 (Thought)
    3. 如果需要行动 → 执行工具 (Action + Observation)
    4. 循环直到 LLM 给出最终答案
    """
    
    def __init__(self, tools=None, max_steps=10):
        self.tools = {t.name: t for t in (tools or get_tools())}
        self.llm = MockLLM()
        self.max_steps = max_steps
    
    def parse_action(self, response):
        """从 LLM 响应中解析 Action"""
        match = re.search(r'Action:\s*(\w+)\("([^"]+)"\)', response)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def run(self, question):
        """执行 ReAct 循环"""
        print(f"\n问题: {question}")
        print("-" * 40)
        
        scratchpad = ""  # 记录推理过程
        
        for step in range(self.max_steps):
            # 1. LLM 思考
            response = self.llm.think(question, scratchpad)
            print(response)
            
            # 2. 检查是否完成
            if "Final Answer" in response:
                answer = response.split("Final Answer:")[-1].strip()
                return answer
            
            # 3. 解析并执行 Action
            action_name, action_input = self.parse_action(response)
            if action_name and action_name in self.tools:
                observation = self.tools[action_name].run(action_input)
                obs_line = f"Observation: {observation}"
                print(obs_line)
                scratchpad += response + "\n" + obs_line + "\n"
            else:
                scratchpad += response + "\n"
        
        return "无法在最大步数内得出答案"


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("ReAct Agent 演示")
    print("=" * 60)
    
    agent = ReActAgent()
    
    questions = [
        "计算 15 + 27",
        "什么是 GPT",
    ]
    
    for q in questions:
        answer = agent.run(q)
        print(f"\n最终答案: {answer}\n")


if __name__ == '__main__':
    demo()
