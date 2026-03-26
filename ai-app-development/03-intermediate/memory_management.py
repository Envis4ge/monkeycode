"""
记忆管理 — 让 Agent 记住对话上下文
====================================
目标：理解短期记忆、长期记忆、工作记忆的管理方案

核心概念：
- 短期记忆(Short-term): 上下文窗口内的对话历史
- 长期记忆(Long-term): 持久化的知识存储
- 工作记忆(Working): 当前任务的状态和变量
"""

import json
import time
from collections import deque
from typing import Optional

# ============ 短期记忆 ============

class ShortTermMemory:
    """
    短期记忆：对话上下文窗口
    
    策略:
    - 保留最近 N 轮对话
    - 超出窗口时，旧对话被截断或压缩
    - 最简单的实现方式
    """
    
    def __init__(self, max_turns=10):
        self.max_turns = max_turns
        self.messages = deque(maxlen=max_turns * 2)  # user + assistant 各一条
    
    def add(self, role, content):
        self.messages.append({"role": role, "content": content, "ts": time.time()})
    
    def get_context(self):
        return list(self.messages)
    
    def clear(self):
        self.messages.clear()
    
    def __len__(self):
        return len(self.messages)


# ============ 带摘要的短期记忆 ============

class SummaryMemory:
    """
    摘要记忆：旧对话压缩为摘要
    
    策略:
    - 保留最近 K 轮完整对话
    - 更早的对话压缩为摘要
    - 总 token 数控制在预算内
    """
    
    def __init__(self, recent_turns=5, token_budget=2000):
        self.recent_turns = recent_turns
        self.token_budget = token_budget
        self.recent = deque(maxlen=recent_turns * 2)
        self.summary = ""
        self.all_messages = []
    
    def add(self, role, content):
        msg = {"role": role, "content": content}
        self.recent.append(msg)
        self.all_messages.append(msg)
        
        # 当最近消息满了，压缩旧消息
        if len(self.recent) >= self.recent_turns * 2:
            self._summarize_old()
    
    def _summarize_old(self):
        """压缩旧对话为摘要"""
        # 取出超出 recent 窗口的消息
        old_count = len(self.all_messages) - self.recent_turns * 2
        if old_count <= 0:
            return
        
        old_messages = self.all_messages[:old_count]
        
        # 简单摘要：提取关键信息
        topics = []
        for msg in old_messages:
            if msg["role"] == "user":
                topics.append(msg["content"][:50])
        
        new_summary = f"之前的对话涉及以下话题: {'; '.join(topics[:5])}"
        if self.summary:
            new_summary = self.summary + " | " + new_summary
        
        self.summary = new_summary
        self.all_messages = list(self.recent)
    
    def get_context(self):
        """返回完整的上下文（摘要 + 最近对话）"""
        context = []
        if self.summary:
            context.append({"role": "system", "content": f"[对话摘要] {self.summary}"})
        context.extend(list(self.recent))
        return context


# ============ 向量长期记忆 ============

class VectorLongTermMemory:
    """
    长期记忆：基于向量相似度的知识检索
    
    实际项目中使用:
    - 向量数据库 (Chroma, FAISS, Pinecone)
    - Embedding 模型 (OpenAI, BGE, M3E)
    
    这里用简单的关键词匹配模拟
    """
    
    def __init__(self):
        self.memories = []  # (text, metadata, timestamp)
    
    def store(self, text, metadata=None):
        """存储记忆"""
        self.memories.append({
            "text": text,
            "metadata": metadata or {},
            "timestamp": time.time(),
        })
    
    def retrieve(self, query, top_k=3):
        """检索相关记忆（简单关键词匹配）"""
        query_lower = query.lower()
        scored = []
        
        for mem in self.memories:
            # 简单相关性：共同关键词数量
            common = sum(1 for word in query_lower.split() if word in mem["text"].lower())
            if common > 0:
                scored.append((common, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:top_k]]
    
    def get_all(self):
        return self.memories


# ============ 工作记忆 ============

class WorkingMemory:
    """
    工作记忆：当前任务的状态管理
    
    类似于程序中的局部变量：
    - 存储当前任务的中间结果
    - 跟踪多步骤任务的进度
    - 任务完成后可选择持久化到长期记忆
    """
    
    def __init__(self):
        self.state = {}          # 键值对状态
        self.task_stack = []     # 任务栈（支持嵌套任务）
        self.step_log = []       # 执行日志
    
    def set(self, key, value):
        self.state[key] = value
        self.step_log.append({"action": "set", "key": key, "value": value})
    
    def get(self, key, default=None):
        return self.state.get(key, default)
    
    def push_task(self, task_name, description=""):
        self.task_stack.append({"name": task_name, "desc": description})
        self.step_log.append({"action": "push_task", "task": task_name})
    
    def pop_task(self):
        if self.task_stack:
            task = self.task_stack.pop()
            self.step_log.append({"action": "pop_task", "task": task["name"]})
            return task
        return None
    
    def current_task(self):
        return self.task_stack[-1] if self.task_stack else None
    
    def clear(self):
        self.state.clear()
        self.task_stack.clear()
        self.step_log.clear()


# ============ 统一记忆管理器 ============

class MemoryManager:
    """
    统一记忆管理器：整合三种记忆
    
    使用流程:
    1. 用户对话 → 短期记忆
    2. 重要信息 → 长期记忆
    3. 任务状态 → 工作记忆
    4. 构建 LLM 上下文时，合并三种记忆
    """
    
    def __init__(self, short_max=10, recent_turns=5):
        self.short_term = ShortTermMemory(max_turns=short_max)
        self.long_term = VectorLongTermMemory()
        self.working = WorkingMemory()
        self.summary_memory = SummaryMemory(recent_turns=recent_turns)
    
    def add_message(self, role, content):
        """添加对话消息"""
        self.short_term.add(role, content)
        self.summary_memory.add(role, content)
    
    def remember(self, text, metadata=None):
        """存储到长期记忆"""
        self.long_term.store(text, metadata)
    
    def build_context(self, current_query):
        """
        构建完整的 LLM 上下文
        
        策略: 系统提示 + 长期记忆检索 + 短期对话
        """
        context = []
        
        # 1. 系统提示 + 工作记忆
        system_parts = ["你是一个有帮助的助手。"]
        task = self.working.current_task()
        if task:
            system_parts.append(f"当前任务: {task['name']} - {task['desc']}")
        
        # 2. 长期记忆检索
        relevant = self.long_term.retrieve(current_query)
        if relevant:
            memories = "\n".join([m["text"] for m in relevant])
            system_parts.append(f"相关信息:\n{memories}")
        
        context.append({"role": "system", "content": "\n".join(system_parts)})
        
        # 3. 短期对话
        context.extend(self.short_term.get_context())
        
        return context
    
    def stats(self):
        """记忆状态统计"""
        return {
            "短期记忆": len(self.short_term),
            "长期记忆": len(self.long_term.get_all()),
            "工作记忆": len(self.working.state),
            "当前任务": self.working.current_task(),
        }


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("记忆管理演示")
    print("=" * 60)
    
    mem = MemoryManager()
    
    # 模拟对话
    conversations = [
        ("user", "我叫张三，我在学习Python"),
        ("assistant", "你好张三！Python是很棒的入门语言"),
        ("user", "我想了解列表和字典的区别"),
        ("assistant", "列表是有序的，字典是键值对..."),
        ("user", "那元组呢？"),
        ("assistant", "元组是不可变的有序集合..."),
        ("user", "帮我写一个排序算法"),
    ]
    
    print("\n--- 添加对话到短期记忆 ---")
    for role, content in conversations:
        mem.add_message(role, content)
        print(f"  [{role}] {content[:30]}...")
    
    # 存储到长期记忆
    print("\n--- 存储重要信息到长期记忆 ---")
    mem.remember("张三正在学习Python，关注列表、字典、元组等数据结构", {"topic": "学习记录"})
    mem.remember("张三想了解排序算法，特别是快速排序", {"topic": "算法"})
    
    # 设置工作记忆
    print("\n--- 设置工作记忆 ---")
    mem.working.push_task("排序算法学习", "讲解常见排序算法的实现")
    mem.working.set("current_topic", "排序算法")
    mem.working.set("progress", "刚开始")
    
    # 构建完整上下文
    print("\n--- 构建 LLM 上下文 ---")
    context = mem.build_context("排序算法怎么实现")
    for c in context:
        print(f"  [{c['role']}] {c['content'][:60]}...")
    
    # 状态统计
    print("\n--- 记忆状态 ---")
    stats = mem.stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    demo()
