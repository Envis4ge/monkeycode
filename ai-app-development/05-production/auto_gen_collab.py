"""
AutoGen 多 Agent 协作 — 团队式任务解决
======================================
目标：理解多 Agent 协作的架构和实现

核心概念：
- 多 Agent：多个 LLM 分工协作，像一个团队
- 角色分工：每个 Agent 有专长（编码、审查、决策）
- 消息总线：Agent 之间通过消息通信
- 群聊管理：决定下一个发言的 Agent
"""

import json
import time
from typing import Optional, List, Dict

# ============ 消息总线 ============

class Message:
    """Agent 间传递的消息"""
    def __init__(self, sender: str, content: str, receiver: str = "all", msg_type: str = "text"):
        self.sender = sender
        self.content = content
        self.receiver = receiver
        self.msg_type = msg_type
        self.timestamp = time.time()
    
    def __repr__(self):
        target = "所有人" if self.receiver == "all" else self.receiver
        return f"[{self.sender} → {target}] {self.content[:50]}"


class MessageBus:
    """
    消息总线：管理 Agent 间的消息传递
    
    支持:
    - 广播：发送给所有 Agent
    - 定向：发送给指定 Agent
    - 历史：记录所有消息
    """
    
    def __init__(self):
        self.history: List[Message] = []
        self.subscribers: Dict[str, callable] = {}
    
    def subscribe(self, agent_name: str, callback: callable):
        self.subscribers[agent_name] = callback
    
    def send(self, message: Message):
        self.history.append(message)
        
        if message.receiver == "all":
            for name, callback in self.subscribers.items():
                if name != message.sender:
                    callback(message)
        elif message.receiver in self.subscribers:
            self.subscribers[message.receiver](message)
    
    def get_history(self, last_n: int = 10):
        return self.history[-last_n:]


# ============ Agent 基类 ============

class Agent:
    """
    Agent 基类
    
    每个 Agent 有:
    - 名称：唯一标识
    - 角色：描述职责
    - 系统提示：定义行为
    - 消息处理函数
    """
    
    def __init__(self, name: str, role: str, system_prompt: str, llm_func=None):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm_func = llm_func
        self.inbox: List[Message] = []
        self.bus: Optional[MessageBus] = None
    
    def connect(self, bus: MessageBus):
        self.bus = bus
        bus.subscribe(self.name, self.on_message)
    
    def on_message(self, message: Message):
        """收到消息时的回调"""
        self.inbox.append(message)
    
    def send(self, content: str, receiver: str = "all"):
        """发送消息"""
        if self.bus:
            msg = Message(self.name, content, receiver)
            self.bus.send(msg)
    
    def think(self) -> str:
        """思考并生成响应"""
        if self.llm_func:
            context = "\n".join([f"{m.sender}: {m.content}" for m in self.inbox[-5:]])
            prompt = f"{self.system_prompt}\n\n最近消息:\n{context}\n\n你的回应:"
            return self.llm_func(prompt)
        return f"[{self.name}] 收到消息，正在思考..."
    
    def __repr__(self):
        return f"Agent({self.name}, role={self.role})"


# ============ 群聊管理器 ============

class GroupChatManager:
    """
    群聊管理器：决定下一个发言的 Agent
    
    策略:
    - 轮流发言
    - 根据内容决定
    - 最后发言的 Agent 不能连续发言
    """
    
    def __init__(self, agents: List[Agent], bus: MessageBus, llm_func=None):
        self.agents = {a.name: a for a in agents}
        self.bus = bus
        self.llm_func = llm_func
        self.last_speaker = None
    
    def select_next(self) -> Optional[Agent]:
        """选择下一个发言的 Agent"""
        # 简单策略：轮换，跳过上一个发言的
        for name, agent in self.agents.items():
            if name != self.last_speaker and agent.inbox:
                return agent
        return None
    
    def run_round(self, max_turns: int = 5):
        """运行一轮对话"""
        for turn in range(max_turns):
            next_agent = self.select_next()
            if not next_agent:
                break
            
            response = next_agent.think()
            next_agent.send(response)
            self.last_speaker = next_agent.name
            
            # 检查是否达成共识
            if self._check_complete():
                print(f"✅ 任务完成，共 {turn + 1} 轮")
                return
        
        print(f"⏰ 达到最大轮数 ({max_turns})")
    
    def _check_complete(self) -> bool:
        """检查任务是否完成"""
        history = self.bus.get_history()
        if history:
            last = history[-1]
            keywords = ["完成", "可以了", "没问题", "approved", "done"]
            return any(k in last.content.lower() for k in keywords)
        return False


# ============ 多 Agent 协作场景 ============

def demo_code_review():
    """场景：代码审查（Coder + Reviewer + Manager）"""
    print("=" * 60)
    print("多 Agent 协作演示：代码审查")
    print("=" * 60)
    
    bus = MessageBus()
    
    # 模拟 LLM
    responses_iter = iter([
        "我写了一个排序函数：\ndef sort_list(lst):\n    return sorted(lst)",
        "代码简洁，但建议：1. 添加类型注解 2. 添加 docstring 3. 处理空列表",
        "根据审查意见修改：\ndef sort_list(lst: list) -> list:\n    '''对列表排序'''\n    if not lst:\n        return []\n    return sorted(lst)",
        "修改后的代码质量很好，审查通过。completed",
    ])
    
    def mock_llm(prompt):
        try:
            return next(responses_iter)
        except StopIteration:
            return "completed"
    
    # 创建 Agent
    coder = Agent("Coder", "编码", "你是编码专家，负责编写和修改代码。", mock_llm)
    reviewer = Agent("Reviewer", "审查", "你是代码审查专家，负责检查代码质量。", mock_llm)
    manager = Agent("Manager", "管理", "你是项目管理者，负责协调和决策。", mock_llm)
    
    # 连接消息总线
    for agent in [coder, reviewer, manager]:
        agent.connect(bus)
    
    # 初始化任务
    manager.send("请编写一个 Python 排序函数")
    
    # 运行协作
    manager_llm = GroupChatManager([coder, reviewer, manager], bus, mock_llm)
    
    # 手动演示流程
    print(f"\n{bus.history[-1]}")
    
    # Coder 写代码
    coder.send(coder.think())
    print(f"{bus.history[-1]}")
    
    # Reviewer 审查
    reviewer.send(reviewer.think(), "Coder")
    print(f"{bus.history[-1]}")
    
    # Coder 修改
    coder.send(coder.think())
    print(f"{bus.history[-1]}")
    
    # Manager 确认
    manager.send(manager.think())
    print(f"{bus.history[-1]}")
    
    print(f"\n消息历史 ({len(bus.history)} 条):")
    for msg in bus.history:
        print(f"  {msg}")


def demo_research():
    """场景：研究分析（Researcher + Analyst + Writer）"""
    print("\n" + "=" * 60)
    print("多 Agent 协作演示：研究分析")
    print("=" * 60)
    
    bus = MessageBus()
    
    researcher = Agent("Researcher", "研究", "你是研究专家，负责收集和整理信息。")
    analyst = Agent("Analyst", "分析", "你是数据分析专家，负责分析数据得出结论。")
    writer = Agent("Writer", "写作", "你是写作专家，负责将分析结果写成报告。")
    
    for agent in [researcher, analyst, writer]:
        agent.connect(bus)
    
    # 模拟协作流程
    researcher.send("已完成关于大语言模型趋势的调研，主要发现：1) Agent 架构兴起 2) 多模态成为标配 3) 小模型性能提升")
    print(f"{bus.history[-1]}")
    
    analyst.send("分析结论：Agent 是下一个增长点，建议重点投入。市场规模预计 2027 年达到 50 亿美元。")
    print(f"{bus.history[-1]}")
    
    writer.send("报告草稿已完成，核心观点：'2026年将是 Agent 元年'。请审阅。")
    print(f"{bus.history[-1]}")
    
    researcher.send("数据部分准确，可以发布。completed")
    print(f"{bus.history[-1]}")


# ============ AutoGen 风格代码 ============

AUTOGEN_CODE = '''
# pip install pyautogen

import autogen

# 配置 LLM
config = {
    "model": "gpt-4o-mini",
    "api_key": "sk-xxx",
}

# 创建 Agent
coder = autogen.AssistantAgent(
    name="Coder",
    system_message="你是 Python 编码专家。写代码要简洁、高效、有注释。",
    llm_config=config,
)

reviewer = autogen.AssistantAgent(
    name="Reviewer",
    system_message="你是代码审查专家。检查代码质量、安全性和性能。",
    llm_config=config,
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "workspace"},
)

# 创建群聊
groupchat = autogen.GroupChat(
    agents=[user_proxy, coder, reviewer],
    messages=[],
    max_round=10,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=config)

# 启动对话
user_proxy.initiate_chat(
    manager,
    message="写一个 Python 函数，计算斐波那契数列的第 n 项",
)
'''


if __name__ == '__main__':
    demo_code_review()
    demo_research()
    print("\n" + "=" * 60)
    print("AutoGen 框架代码示例")
    print("=" * 60)
    print(AUTOGEN_CODE)
