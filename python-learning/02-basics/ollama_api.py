"""
Ollama API — 大模型本地调用
===========================
目标：在本地运行大模型并调用 API

核心内容：
- Ollama 安装与配置
- REST API 调用
- 流式响应处理
- 模型管理
"""

import json
import urllib.request
import urllib.error

# ============ 配置 ============

OLLAMA_BASE = "http://localhost:11434"

# ============ API 封装 ============

def list_models():
    """列出本地所有可用模型"""
    url = f"{OLLAMA_BASE}/api/tags"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            return data.get('models', [])
    except urllib.error.URLError:
        print("❌ 无法连接 Ollama，请确保已启动: ollama serve")
        return []


def chat(model, messages, stream=False):
    """
    与模型对话（Chat API）
    
    model: 模型名称，如 'llama3', 'qwen2', 'gemma2'
    messages: 消息列表，格式 [{"role": "user", "content": "..."}]
    stream: 是否使用流式响应
    """
    url = f"{OLLAMA_BASE}/api/chat"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": stream,
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as resp:
            if stream:
                # 流式：逐 token 返回
                full_response = ""
                for line in resp:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print()  # 换行
                return full_response
            else:
                # 非流式：一次性返回
                data = json.loads(resp.read())
                return data.get("message", {}).get("content", "")
    except urllib.error.URLError as e:
        return f"❌ 错误: {e}"


def generate(model, prompt, stream=False):
    """
    简单文本生成（Generate API）
    
    与 chat 不同，generate 只接受单个 prompt，不支持多轮对话
    """
    url = f"{OLLAMA_BASE}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": stream,
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as resp:
            if stream:
                full_response = ""
                for line in resp:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print()
                return full_response
            else:
                data = json.loads(resp.read())
                return data.get("response", "")
    except urllib.error.URLError as e:
        return f"❌ 错误: {e}"


def pull_model(model):
    """下载模型"""
    url = f"{OLLAMA_BASE}/api/pull"
    payload = json.dumps({"model": model, "stream": True}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    print(f"正在下载模型: {model}")
    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                data = json.loads(line)
                status = data.get("status", "")
                if "total" in data and "completed" in data:
                    pct = data["completed"] / data["total"] * 100
                    print(f"  {status}: {pct:.1f}%", end="\r")
                else:
                    print(f"  {status}")
        print(f"\n✅ {model} 下载完成")
    except urllib.error.URLError as e:
        print(f"❌ 下载失败: {e}")


def show_model(model):
    """查看模型详细信息"""
    url = f"{OLLAMA_BASE}/api/show"
    payload = json.dumps({"model": model}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"模型: {model}")
            print(f"  模型架构: {data.get('details', {}).get('family', 'unknown')}")
            print(f"  参数量: {data.get('details', {}).get('parameter_size', 'unknown')}")
            print(f"  量化: {data.get('details', {}).get('quantization_level', 'unknown')}")
            if 'license' in data:
                print(f"  许可证: {data['license'][:50]}...")
            return data
    except urllib.error.URLError as e:
        print(f"❌ 错误: {e}")
        return None


# ============ 多轮对话封装 ============

class ChatSession:
    """简单的多轮对话会话管理"""
    
    def __init__(self, model="llama3", system="你是一个有帮助的助手。"):
        self.model = model
        self.messages = []
        if system:
            self.messages.append({"role": "system", "content": system})
    
    def ask(self, question, stream=True):
        """发送问题并获取回复"""
        self.messages.append({"role": "user", "content": question})
        response = chat(self.model, self.messages, stream=stream)
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def reset(self):
        """重置对话"""
        self.messages = []


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("Ollama API 演示")
    print("=" * 60)
    
    # 1. 列出模型
    print("\n--- 本地可用模型 ---")
    models = list_models()
    if not models:
        print("没有找到模型。请先安装 Ollama 并下载模型:")
        print("  1. 安装: https://ollama.com")
        print("  2. 下载模型: ollama pull llama3")
        print("  3. 启动服务: ollama serve")
        print("\n以下展示 API 调用方式（需要 Ollama 运行中）")
        return
    
    for m in models:
        size_gb = m.get('size', 0) / (1024**3)
        print(f"  📦 {m['name']} ({size_gb:.1f} GB)")
    
    # 2. 简单对话
    model_name = models[0]['name']
    print(f"\n--- 简单对话 (使用 {model_name}) ---")
    
    prompt = "用一句话解释什么是机器学习"
    print(f"问题: {prompt}")
    print("回答: ", end="")
    answer = generate(model_name, prompt, stream=True)
    
    # 3. 多轮对话
    print(f"\n--- 多轮对话 ---")
    session = ChatSession(model=model_name, system="你是Python专家，回答简洁。")
    
    questions = [
        "Python中列表和元组有什么区别？",
        "那集合呢？",
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        print("A: ", end="")
        session.ask(q, stream=True)


if __name__ == '__main__':
    demo()
