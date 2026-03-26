"""
配置管理 — Agent 配置文件
========================
集中管理 LLM 端点、模型参数、系统提示等
"""

import os

# ============ LLM 配置 ============

class LLMConfig:
    """LLM 客户端配置"""
    
    def __init__(self):
        # Ollama 本地部署（推荐）
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.model = os.getenv("LLM_MODEL", "qwen2.5:7b")
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        
        # API Key（如需使用云端 API）
        self.api_key = os.getenv("LLM_API_KEY", "")
        
        # 生成参数
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
        self.top_p = float(os.getenv("LLM_TOP_P", "0.9"))
    
    def __repr__(self):
        return f"LLMConfig(provider={self.provider}, model={self.model})"


# ============ Agent 配置 ============

class AgentConfig:
    """Agent 行为配置"""
    
    def __init__(self):
        # 系统提示
        self.system_prompt = """你是一个智能助手，可以调用工具完成任务。

行为准则:
1. 仔细分析用户需求
2. 只在需要时调用工具
3. 工具调用失败时，告知用户并尝试其他方法
4. 保持回答简洁、准确
5. 不知道的事情不要编造"""

        # 最大推理步数
        self.max_steps = int(os.getenv("AGENT_MAX_STEPS", "10"))
        
        # 是否显示详细日志
        self.verbose = os.getenv("AGENT_VERBOSE", "true").lower() == "true"
        
        # 记忆轮数
        self.memory_turns = int(os.getenv("AGENT_MEMORY_TURNS", "20"))


# ============ 工具配置 ============

class ToolConfig:
    """工具安全配置"""
    
    def __init__(self):
        # 文件读取限制
        self.allowed_extensions = ['.txt', '.md', '.py', '.json', '.csv', '.log']
        self.max_file_size = 10 * 1024  # 10KB
        
        # 计算器限制
        self.max_expression_length = 100
        
        # 搜索限制
        self.max_search_results = 5


# ============ 全局配置 ============

config = {
    "llm": LLMConfig(),
    "agent": AgentConfig(),
    "tools": ToolConfig(),
}


def print_config():
    """打印当前配置"""
    print("=" * 50)
    print("Agent 配置")
    print("=" * 50)
    print(f"LLM 提供商：{config['llm'].provider}")
    print(f"LLM 模型：{config['llm'].model}")
    print(f"LLM 地址：{config['llm'].base_url}")
    print(f"温度：{config['llm'].temperature}")
    print(f"最大步数：{config['agent'].max_steps}")
    print(f"详细日志：{config['agent'].verbose}")
    print("=" * 50)


if __name__ == '__main__':
    print_config()
