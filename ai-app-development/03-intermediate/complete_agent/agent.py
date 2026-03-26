"""
Agent 核心引擎
==============
ReAct + Function Calling + 记忆系统的完整整合
"""

import json
import re
import time
from typing import Optional


class Message:
    """对话消息"""
    def __init__(self, role, content, tool_calls=None, tool_call_id=None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id
        self.timestamp = time.time()
    
    def to_dict(self):
        d = {"role": self.role, "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d


class Memory:
    """简化版记忆系统"""
    
    def __init__(self, max_turns=20):
        self.messages = []
        self.max_turns = max_turns
        self.facts = {}  # 长期记忆
    
    def add(self, role, content, **kwargs):
        self.messages.append(Message(role, content, **kwargs))
        if len(self.messages) > self.max_turns * 2:
            # 简单截断：移除最早的消息
            self.messages = self.messages[-self.max_turns * 2:]
    
    def remember(self, key, value):
        self.facts[key] = value
    
    def recall(self, key):
        return self.facts.get(key)
    
    def get_messages(self):
        return [m.to_dict() for m in self.messages]
    
    def get_context_summary(self):
        """生成上下文摘要"""
        if not self.facts:
            return ""
        items = [f"{k}: {v}" for k, v in self.facts.items()]
        return "已知信息: " + "; ".join(items)


class Agent:
    """
    完整的 Agent 引擎
    
    架构:
    用户输入 → Agent 主循环
                 ↓
           LLM 决策(Thought)
                 ↓
           工具调用(Action) ←→ 工具系统
                 ↓
           观察结果(Observation)
                 ↓
           最终回答(Final Answer)
    """
    
    def __init__(self, llm_client, tools, system_prompt="你是一个有帮助的助手。", max_steps=10):
        self.llm = llm_client
        self.tools = {t["name"]: t for t in tools}
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        self.memory = Memory()
    
    def _build_tool_definitions(self):
        """构建工具定义（给 LLM）"""
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                }
            }
            for t in self.tools.values()
        ]
    
    def _execute_tool(self, name, arguments):
        """执行工具"""
        if name not in self.tools:
            return f"错误: 未知工具 '{name}'"
        
        tool = self.tools[name]
        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
            result = tool["func"](**args)
            return str(result)
        except Exception as e:
            return f"工具执行错误: {e}"
    
    def run(self, user_input):
        """运行 Agent"""
        # 添加用户消息
        self.memory.add("user", user_input)
        
        print(f"\n{'='*50}")
        print(f"用户: {user_input}")
        print(f"{'='*50}")
        
        for step in range(self.max_steps):
            # 1. 调用 LLM
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # 添加长期记忆摘要
            summary = self.memory.get_context_summary()
            if summary:
                messages.append({"role": "system", "content": summary})
            
            messages.extend(self.memory.get_messages())
            
            response = self.llm.chat(messages, self._build_tool_definitions())
            
            # 2. 检查是否有工具调用
            if response.get("tool_calls"):
                for tc in response["tool_calls"]:
                    func_name = tc["function"]["name"]
                    func_args = tc["function"]["arguments"]
                    
                    print(f"\n  🔧 调用工具: {func_name}({func_args})")
                    
                    # 执行工具
                    result = self._execute_tool(func_name, func_args)
                    print(f"  📋 结果: {result}")
                    
                    # 记录工具调用和结果
                    self.memory.add("assistant", None, tool_calls=[tc])
                    self.memory.add("tool", result, tool_call_id=tc["id"])
                
                continue  # 继续循环让 LLM 处理工具结果
            
            # 3. 纯文本回答
            answer = response.get("content", "")
            print(f"\n  🤖 Agent: {answer}")
            self.memory.add("assistant", answer)
            
            return answer
        
        return "达到最大步数限制，无法完成任务。"
    
    def reset(self):
        """重置 Agent 状态"""
        self.memory = Memory()


# ReAct 模式的纯文本版（不需要 Function Calling API）
class ReActAgent:
    """
    ReAct Agent：纯文本推理版
    
    适用于不支持 Function Calling 的 LLM
    通过提示词引导 LLM 输出结构化的 Thought/Action/Observation
    """
    
    REACT_PROMPT = """你是一个能使用工具的助手。

可用工具:
{tools}

请按以下格式回答:
Thought: 我需要思考...
Action: 工具名("参数")
Observation: (工具返回的结果)
... (可以重复多次)
Final Answer: 最终答案

重要: 每次只调用一个工具，等待结果后再继续。"""
    
    def __init__(self, llm_client, tools, max_steps=10):
        self.llm = llm_client
        self.tools = {t["name"]: t for t in tools}
        self.max_steps = max_steps
        
        # 格式化工具描述
        tool_desc = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tools
        ])
        self.system_prompt = self.REACT_PROMPT.format(tools=tool_desc)
    
    def _execute_tool(self, name, args_str):
        if name not in self.tools:
            return f"未知工具: {name}"
        try:
            tool = self.tools[name]
            # 简单参数解析
            args_str = args_str.strip('()"\'')
            if "expression" in str(tool.get("parameters", {})):
                return str(tool["func"](expression=args_str))
            elif "query" in str(tool.get("parameters", {})):
                return str(tool["func"](query=args_str))
            return str(tool["func"](args_str))
        except Exception as e:
            return f"错误: {e}"
    
    def run(self, question):
        """运行 ReAct 循环"""
        print(f"\n问题: {question}")
        print("-" * 40)
        
        context = f"Question: {question}\n"
        
        for step in range(self.max_steps):
            # LLM 生成下一步
            prompt = self.system_prompt + "\n\n" + context
            response = self.llm.complete(prompt)
            print(response)
            
            # 检查是否完成
            if "Final Answer" in response:
                context += response + "\n"
                return response.split("Final Answer:")[-1].strip()
            
            # 解析 Action
            match = re.search(r'Action:\s*(\w+)\(["\'](.+?)["\']\)', response)
            if match:
                tool_name, tool_args = match.group(1), match.group(2)
                result = self._execute_tool(tool_name, tool_args)
                obs = f"Observation: {result}"
                print(obs)
                context += response + "\n" + obs + "\n"
            else:
                context += response + "\n"
        
        return "达到最大步数限制"
