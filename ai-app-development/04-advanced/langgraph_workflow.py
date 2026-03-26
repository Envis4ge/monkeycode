"""
LangGraph 状态机工作流 — 精确流程控制
======================================
目标：理解 LangGraph 的状态机模型，构建复杂 Agent 工作流

核心概念：
- State（状态）：工作流中传递的数据
- Node（节点）：一个处理步骤
- Edge（边）：节点间的连接，可以是固定或条件的
- Graph（图）：节点 + 边的组合

LangGraph vs LangChain Chains:
- Chains: A→B→C（线性，固定流程）
- LangGraph: 支持循环、条件分支、并行（灵活流程）
"""

# ============ 核心概念图解 ============

WORKFLOW_DIAGRAM = """
Agent 工作流图:

    START
      ↓
   thinking ←──────┐
      ↓             │
   判断 ────────────┤
      ↓             │
   tool_call ──→ after_tool
      ↓             │
   generate ───────┘ (循环)
      ↓
     END
"""


# ============ 简化版状态机实现 ============

class State:
    """工作流状态"""
    def __init__(self):
        self.messages = []
        self.current_step = "start"
        self.tool_calls = []
        self.iteration = 0
        self.max_iterations = 10
    
    def to_dict(self):
        return {
            "messages": self.messages,
            "step": self.current_step,
            "iteration": self.iteration,
        }


class Node:
    """工作流节点"""
    def __init__(self, name, func):
        self.name = name
        self.func = func
    
    def execute(self, state):
        return self.func(state)


class Edge:
    """节点间边"""
    def __init__(self, from_node, to_node, condition=None):
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition  # 条件函数


class Graph:
    """工作流图"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.start = None
        self.end_nodes = set()
    
    def add_node(self, name, func):
        self.nodes[name] = Node(name, func)
    
    def set_start(self, name):
        self.start = name
    
    def add_end(self, name):
        self.end_nodes.add(name)
    
    def add_edge(self, from_node, to_node, condition=None):
        self.edges.append(Edge(from_node, to_node, condition))
    
    def get_next(self, current_node, state):
        """根据当前节点和状态找下一个节点"""
        for edge in self.edges:
            if edge.from_node == current_node:
                if edge.condition is None or edge.condition(state):
                    return edge.to_node
        return None
    
    def run(self, initial_state):
        """执行工作流"""
        if not self.start:
            raise ValueError("未设置起始节点")
        
        state = initial_state
        current = self.start
        
        while current and current not in self.end_nodes:
            if current in self.nodes:
                state = self.nodes[current].execute(state)
            current = self.get_next(current, state)
            state.iteration += 1
            
            if state.iteration >= state.max_iterations:
                print("⚠️ 达到最大迭代次数")
                break
        
        return state


# ============ Agent 工作流示例 ============

def build_agent_graph(tools, llm_func):
    """
    构建 Agent 工作流图
    
    节点:
    - thinking: LLM 思考下一步
    - tool_call: 执行工具
    - generate: 生成最终回答
    """
    graph = Graph()
    
    def thinking_node(state):
        """思考节点：LLM 决定下一步行动"""
        response = llm_func(state.messages, tools)
        state.messages.append({"role": "assistant", "content": response.get("content", ""), "tool_calls": response.get("tool_calls")})
        state.tool_calls = response.get("tool_calls", [])
        state.current_step = "thinking"
        return state
    
    def tool_call_node(state):
        """工具调用节点"""
        for tc in state.tool_calls:
            name = tc["function"]["name"]
            args = tc["function"]["arguments"]
            if name in tools:
                result = tools[name](**eval(args))
                state.messages.append({"role": "tool", "content": str(result)})
        state.tool_calls = []
        state.current_step = "tool_call"
        return state
    
    def generate_node(state):
        """生成最终回答"""
        state.current_step = "generate"
        return state
    
    # 注册节点
    graph.add_node("thinking", thinking_node)
    graph.add_node("tool_call", tool_call_node)
    graph.add_node("generate", generate_node)
    
    # 设置边和条件
    graph.set_start("thinking")
    
    # thinking → 有工具调用则 tool_call，否则 generate
    graph.add_edge("thinking", "tool_call", condition=lambda s: bool(s.tool_calls))
    graph.add_edge("thinking", "generate", condition=lambda s: not s.tool_calls)
    
    # tool_call → 回到 thinking（循环）
    graph.add_edge("tool_call", "thinking")
    
    graph.add_end("generate")
    
    return graph


# ============ LangChain LangGraph 代码示例 ============

LANGGRAPH_CODE = '''
# pip install langgraph langchain langchain-openai

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 定义工具
@tool
def calculator(expression: str) -> str:
    """执行数学计算"""
    return str(eval(expression))

@tool
def search(query: str) -> str:
    """搜索信息"""
    return f"关于 {query} 的搜索结果..."

tools = [calculator, search]

# 创建 LLM
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# 定义节点
def agent_node(state: AgentState):
    """Agent 节点：LLM 决策"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState):
    """工具节点：执行工具调用"""
    from langgraph.prebuilt import ToolNode
    tool_node = ToolNode(tools)
    return tool_node.invoke(state)

# 构建图
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

# 条件边：LLM 有工具调用则走 tools，否则结束
def should_continue(state: AgentState):
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return END

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")  # 工具执行后回到 agent

# 编译运行
app = graph.compile()
result = app.invoke({"messages": [("user", "帮我计算 25*4+10")]})
print(result)
'''


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("LangGraph 工作流演示（简化版）")
    print("=" * 60)
    
    # 模拟工具
    def calculator_tool(expression):
        try:
            return str(eval(expression))
        except:
            return "计算错误"
    
    tools = {"calculator": calculator_tool}
    
    # 模拟 LLM
    call_count = [0]
    def mock_llm(messages, tools_defs):
        call_count[0] += 1
        last_msg = messages[-1] if messages else {}
        content = last_msg.get("content", "")
        
        if call_count[0] == 1:
            # 第一次：调用工具
            import json
            return {
                "tool_calls": [{
                    "function": {
                        "name": "calculator",
                        "arguments": json.dumps({"expression": "25*4+10"})
                    }
                }]
            }
        else:
            # 第二次：生成回答
            return {"content": f"计算结果是 110"}
    
    # 构建并运行图
    graph = build_agent_graph(tools, mock_llm)
    
    state = State()
    state.messages = [{"role": "user", "content": "帮我计算 25*4+10"}]
    
    print(f"\n初始状态: {state.to_dict()}")
    result = graph.run(state)
    print(f"\n最终状态: {result.to_dict()}")
    print(f"\n✅ 工作流执行完成")


if __name__ == '__main__':
    demo()
    print("\n" + WORKFLOW_DIAGRAM)
    print("\n" + "=" * 60)
    print("LangChain LangGraph 完整代码示例")
    print("=" * 60)
    print(LANGGRAPH_CODE)
