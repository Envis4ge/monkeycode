"""
Agent 演示入口
==============
运行方式:
  python3 demo.py --demo        # 演示模式（模拟 LLM）
  python3 demo.py --interactive # 交互模式（需要 Ollama）
"""

import argparse
import sys
from pathlib import Path

# 导入本地模块
sys.path.insert(0, str(Path(__file__).parent))
from agent import Agent, ReActAgent
from tools import TOOLS
from config import config


class MockLLM:
    """
    模拟 LLM 客户端
    
    用于演示，不需要真实 API。
    根据用户问题返回预设的响应，展示完整的工具调用流程。
    """
    
    def __init__(self):
        self.call_count = 0
    
    def chat(self, messages, tools):
        """Function Calling 模式"""
        self.call_count += 1
        
        # 检查是否有工具结果（tool role）
        has_tool_result = any(m.get("role") == "tool" for m in messages)
        
        if has_tool_result:
            # 已经有工具结果了，生成最终回答
            tool_results = [m for m in messages if m.get("role") == "tool"]
            results_text = "; ".join([m.get("content", "") for m in tool_results])
            return {"content": f"根据工具返回：{results_text}"}
        
        # 获取最后一条用户消息
        last_user = None
        for m in reversed(messages):
            if m["role"] == "user":
                last_user = m["content"]
                break
        
        if not last_user:
            return {"content": "我没理解你的问题"}
        
        msg = last_user.lower()
        
        # 计算需求
        if any(c in msg for c in ['计算', '算', '+', '-', '*', '/']):
            import re
            expr_match = re.search(r'[\d+\-*/().\s]+', last_user)
            if expr_match:
                expr = expr_match.group().strip()
                return {
                    "tool_calls": [{
                        "id": f"call_{self.call_count}",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": f'{{"expression": "{expr}"}}'
                        }
                    }]
                }
        
        # 搜索需求
        if any(w in msg for w in ['什么是', '介绍', '搜索', '了解', '知道']):
            topic = last_user.replace('什么是', '').replace('介绍', '').replace('搜索', '').strip()
            return {
                "tool_calls": [{
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": f'{{"query": "{topic}"}}'
                    }
                }]
            }
        
        # 默认直接回答
        return {"content": f"我理解了：{last_user}。有什么我可以帮你的吗？"}
    
    def complete(self, prompt):
        """纯文本补全模式（ReAct）"""
        return "Thought: 我可以直接回答\nFinal Answer: 这是一个模拟回答"


def run_demo():
    """演示模式：展示工具调用流程"""
    print("\n" + "=" * 60)
    print("Agent 演示模式")
    print("=" * 60)
    
    llm = MockLLM()
    
    questions = [
        "帮我计算 25 * 4 + 10",
        "什么是机器学习？",
        "Python 有什么特点？",
    ]
    
    for q in questions:
        agent = Agent(llm, TOOLS, max_steps=5)
        answer = agent.run(q)
        print(f"\n最终回答: {answer}")
    
    print("\n✅ 演示完成！")


def run_interactive():
    """交互模式：需要真实的 LLM"""
    print("\n" + "=" * 60)
    print("Agent 交互模式")
    print("=" * 60)
    print("提示: 输入 'quit' 或 'exit' 退出\n")
    
    try:
        from ollama import Client
        client = Client(host=config.llm.base_url)
        
        class OllamaLLM:
            def chat(self, messages, tools):
                response = client.chat(
                    model=config.llm.model,
                    messages=messages,
                    tools=tools,
                )
                return response.message.to_dict()
        
        llm = OllamaLLM()
        agent = Agent(llm, TOOLS, max_steps=5)
        
        while True:
            try:
                user_input = input("你: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                
                if not user_input:
                    continue
                
                agent.run(user_input)
            
            except KeyboardInterrupt:
                print("\n再见！")
                break
    
    except ImportError:
        print("❌ 错误: 需要安装 ollama 库")
        print("   运行: pip install ollama")
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("请确保 Ollama 服务已启动: ollama serve")


def main():
    parser = argparse.ArgumentParser(description="Agent 演示")
    parser.add_argument('--demo', action='store_true', help='演示模式（模拟 LLM）')
    parser.add_argument('--interactive', action='store_true', help='交互模式（需要 Ollama）')
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.interactive:
        run_interactive()
    else:
        print("用法: python3 demo.py --demo  或  python3 demo.py --interactive")
        print("\n示例:")
        print("  python3 demo.py --demo        # 快速体验（无需 API）")
        print("  python3 demo.py --interactive # 真实对话（需要 Ollama）")


if __name__ == '__main__':
    main()
