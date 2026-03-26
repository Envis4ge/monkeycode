"""
Function Calling — LLM 工具调用
================================
目标：理解 LLM 如何以 JSON 格式调用外部工具

核心内容：
- 工具定义（JSON Schema）
- 参数解析
- 并行调用
- 错误处理
"""

import json
from typing import Any

# ============ 工具注册 ============

class FunctionRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self.functions = {}   # name → callable
        self.schemas = []     # 工具定义列表
    
    def register(self, name, description, parameters, required=None):
        """注册工具（装饰器）"""
        def decorator(func):
            self.functions[name] = func
            schema = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": parameters,
                        "required": required or list(parameters.keys()),
                    }
                }
            }
            self.schemas.append(schema)
            return func
        return decorator
    
    def get_tools(self):
        """返回工具定义列表（给 LLM）"""
        return self.schemas
    
    def call(self, name, arguments):
        """执行工具"""
        if name not in self.functions:
            return {"error": f"未知工具: {name}"}
        try:
            result = self.functions[name](**arguments)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


# ============ 创建工具 ============

registry = FunctionRegistry()

@registry.register(
    name="calculator",
    description="执行数学计算",
    parameters={
        "expression": {
            "type": "string",
            "description": "数学表达式，如 '2 + 3 * 4'"
        }
    }
)
def calculator(expression):
    allowed = set('0123456789+-*/.() ')
    if not all(c in allowed for c in expression):
        return "错误：包含不允许的字符"
    return str(eval(expression))


@registry.register(
    name="get_weather",
    description="获取指定城市的天气信息",
    parameters={
        "city": {
            "type": "string",
            "description": "城市名称"
        },
        "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "温度单位"
        }
    }
)
def get_weather(city, unit="celsius"):
    # 模拟返回
    temps = {"北京": 15, "上海": 20, "深圳": 25}
    temp = temps.get(city, 18)
    if unit == "fahrenheit":
        temp = temp * 9/5 + 32
    return f"{city}: {temp}°{'C' if unit == 'celsius' else 'F'}"


@registry.register(
    name="search_web",
    description="搜索网页信息",
    parameters={
        "query": {
            "type": "string",
            "description": "搜索关键词"
        },
        "num_results": {
            "type": "integer",
            "description": "返回结果数量，默认3"
        }
    },
    required=["query"]
)
def search_web(query, num_results=3):
    return f"找到 {num_results} 条关于 '{query}' 的结果: [模拟数据]"


# ============ 模拟 LLM 响应 ============

class FunctionCaller:
    """
    模拟 LLM 的 Function Calling
    
    实际项目中，这由 LLM API 完成。
    这里模拟是为了演示整个流程。
    """
    
    def __init__(self, registry):
        self.registry = registry
    
    def generate_tool_calls(self, user_message):
        """
        根据用户消息生成工具调用
        
        实际流程:
        1. 用户消息 + 工具定义 → 发送给 LLM
        2. LLM 返回 tool_calls (JSON)
        3. 解析并执行工具
        4. 将结果返回给 LLM
        5. LLM 生成最终回答
        """
        msg = user_message.lower()
        tool_calls = []
        
        # 天气查询
        if '天气' in msg or 'weather' in msg:
            for city in ['北京', '上海', '深圳']:
                if city in msg:
                    tool_calls.append({
                        "id": "call_weather_001",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": json.dumps({"city": city})
                        }
                    })
        
        # 数学计算
        elif any(c in msg for c in ['计算', '算', '+', '-', '*', '/']):
            import re
            expr = re.search(r'[\d+\-*/().]+', user_message)
            if expr:
                tool_calls.append({
                    "id": "call_calc_001",
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "arguments": json.dumps({"expression": expr.group()})
                    }
                })
        
        # 搜索
        elif any(w in msg for w in ['搜索', '搜', '查找', '了解']):
            query = user_message.replace('搜索', '').replace('查找', '').replace('帮我', '').strip()
            tool_calls.append({
                "id": "call_search_001",
                "type": "function",
                "function": {
                    "name": "search_web",
                    "arguments": json.dumps({"query": query})
                }
            })
        
        return tool_calls


# ============ 完整流程 ============

def process_message(user_message):
    """
    完整的 Function Calling 流程
    
    步骤:
    1. 用户发送消息
    2. LLM 决定是否需要调用工具
    3. 如果需要 → 生成 tool_calls
    4. 执行工具
    5. 将工具结果发回 LLM
    6. LLM 生成最终回答
    """
    print(f"\n用户: {user_message}")
    print("-" * 40)
    
    caller = FunctionCaller(registry)
    
    # Step 1: LLM 决定调用哪些工具
    tool_calls = caller.generate_tool_calls(user_message)
    
    if not tool_calls:
        print("LLM: 我可以直接回答，不需要工具")
        return
    
    print(f"LLM 决定调用 {len(tool_calls)} 个工具:")
    
    # Step 2: 执行工具
    tool_results = []
    for call in tool_calls:
        func_name = call["function"]["name"]
        arguments = json.loads(call["function"]["arguments"])
        
        print(f"\n  调用: {func_name}({arguments})")
        result = registry.call(func_name, arguments)
        print(f"  结果: {result}")
        
        tool_results.append({
            "tool_call_id": call["id"],
            "role": "tool",
            "name": func_name,
            "content": json.dumps(result, ensure_ascii=False),
        })
    
    # Step 3: 将结果返回给 LLM 生成最终回答
    print(f"\n  → 将工具结果返回给 LLM 生成最终回答")
    for r in tool_results:
        data = json.loads(r["content"])
        if "result" in data:
            print(f"LLM: 根据工具返回，{data['result']}")


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("Function Calling 演示")
    print("=" * 60)
    
    # 显示注册的工具
    print("\n已注册的工具:")
    for schema in registry.get_tools():
        func = schema["function"]
        print(f"  📌 {func['name']}: {func['description']}")
    
    # 测试调用
    messages = [
        "北京今天天气怎么样？",
        "帮我计算 25 * 4 + 10",
        "搜索 Python 教程",
    ]
    
    for msg in messages:
        process_message(msg)


def demo_parallel():
    """演示并行工具调用"""
    print("\n" + "=" * 60)
    print("并行工具调用演示")
    print("=" * 60)
    
    print("\n用户: 比较一下北京和上海的天气")
    print("-" * 40)
    
    # LLM 同时调用两个工具
    calls = [
        {"id": "call_1", "function": {"name": "get_weather", "arguments": '{"city": "北京"}'}},
        {"id": "call_2", "function": {"name": "get_weather", "arguments": '{"city": "上海"}'}},
    ]
    
    print("LLM 决定并行调用 2 个工具:")
    for call in calls:
        name = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        result = registry.call(name, args)
        print(f"  {name}({args}) → {result}")
    
    print("\n  → 两次调用可以并行执行，节省时间")


if __name__ == '__main__':
    demo()
    demo_parallel()
