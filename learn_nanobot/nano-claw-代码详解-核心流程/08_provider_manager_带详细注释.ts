/**
 * ============================================================
 * nano-claw 核心代码详解 - ProviderManager (LLM 提供商管理器)
 * ============================================================
 * 
 * ProviderManager 负责管理和调用各种 LLM 提供商
 * 支持：OpenRouter, Anthropic, OpenAI, DeepSeek, Gemini 等
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

// 由于网络原因，这里是基于代码结构的详细说明

/**
 * ============================================================
 * 核心类：ProviderManager
 * ============================================================
 * 
 * 功能：
 * 1. 管理多个 LLM 提供商
 * 2. 根据模型名自动选择提供商
 * 3. 缓存提供商实例
 * 4. 统一调用接口
 * 
 * 支持的提供商：
 * | 提供商      | 模型示例                    | API 格式    |
 * |------------|----------------------------|------------|
 * | openrouter | anthropic/claude-*, openai/*| OpenAI     |
 * | anthropic  | claude-3-opus, claude-3-sonnet| Anthropic |
 * | openai     | gpt-4, gpt-3.5-turbo       | OpenAI     |
 * | deepseek   | deepseek-chat              | OpenAI     |
 * | groq       | llama-3, mixtral           | OpenAI     |
 * | gemini     | gemini-pro                 | Google     |
 * | minimax    | abab6.5s-chat              | OpenAI     |
 * | dashscope  | qwen-turbo, qwen-max       | OpenAI     |
 * | moonshot   | moonshot-v1-8k-chat        | OpenAI     |
 * | zhipu      | glm-4, glm-3-turbo         | OpenAI     |
 * | vllm       | (本地模型)                  | OpenAI     |
 */
export class ProviderManager {
  // ==================== 属性 ====================
  
  /** 框架配置 */
  private config: Config;
  
  /** 提供商实例缓存 */
  private providerCache: Map<string, BaseProvider> = new Map();

  // ==================== 构造函数 ====================
  
  constructor(config: Config) {
    this.config = config;
  }

  // ==================== 核心方法 ====================

  /**
   * 获取或创建提供商实例
   * @description 缓存机制避免重复创建
   * 
   * @param providerName - 提供商名称
   * @returns 提供商实例
   */
  private getProviderInstance(providerName: string): BaseProvider {
    // ===== 第1步：检查缓存 =====
    if (this.providerCache.has(providerName)) {
      return this.providerCache.get(providerName)!;
    }

    // ===== 第2步：获取配置 =====
    const providerConfig = this.config.providers?.[providerName];
    
    if (!providerConfig || !providerConfig.apiKey) {
      throw new ProviderError(`Provider ${providerName} is not configured`);
    }

    // ===== 第3步：根据提供商类型创建实例 =====
    let provider: BaseProvider;

    switch (providerName) {
      case 'openrouter':
        // OpenRouter 是网关，可以访问所有模型
        provider = new OpenRouterProvider(
          providerConfig.apiKey, 
          providerConfig.apiBase
        );
        break;
        
      case 'anthropic':
        // Anthropic (Claude)
        provider = new AnthropicProvider(
          providerConfig.apiKey, 
          providerConfig.apiBase
        );
        break;
        
      case 'openai':
        // OpenAI (GPT)
        provider = new OpenAIProvider(
          providerConfig.apiKey, 
          providerConfig.apiBase
        );
        break;
        
      case 'deepseek':
        // DeepSeek (兼容 OpenAI API)
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://api.deepseek.com/v1'
        );
        break;
        
      case 'groq':
        // Groq (兼容 OpenAI API)
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://api.groq.com/openai/v1'
        );
        break;
        
      case 'gemini':
        // Google Gemini
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://generativelanguage.googleapis.com/v1beta'
        );
        break;
        
      case 'minimax':
        // MiniMax
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://api.minimax.chat/v1'
        );
        break;
        
      case 'dashscope':
        // 阿里云 Dashscope (通义千问)
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        );
        break;
        
      case 'moonshot':
        // 月之暗面 Kimi
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://api.moonshot.cn/v1'
        );
        break;
        
      case 'zhipu':
        // 智谱 GLM
        provider = new OpenAIProvider(
          providerConfig.apiKey,
          providerConfig.apiBase || 'https://open.bigmodel.cn/api/paas/v4'
        );
        break;
        
      case 'vllm':
        // 本地 vLLM 模型
        if (!providerConfig.apiBase) {
          throw new ProviderError('vLLM provider requires apiBase configuration');
        }
        provider = new OpenAIProvider(
          providerConfig.apiKey, 
          providerConfig.apiBase
        );
        break;
        
      default:
        throw new ProviderError(`Unknown provider: ${providerName}`);
    }

    // ===== 第4步：缓存并返回 =====
    this.providerCache.set(providerName, provider);
    return provider;
  }

  /**
   * 检测提供商
   * @description 根据模型名自动判断使用哪个提供商
   * 
   * 检测策略：
   * 1. 从模型名推断（如 anthropic/claude-3 -> anthropic）
   * 2. 查找网关提供商（如 OpenRouter）
   * 3. 默认使用第一个配置好的提供商
   */
  private detectProvider(model: string): string {
    // ===== 策略1：从模型名推断 =====
    const providerSpec = findProviderByModel(model);
    if (providerSpec) {
      const providerConfig = this.config.providers?.[providerSpec.name];
      if (providerConfig?.apiKey) {
        return providerSpec.name;
      }
    }

    // ===== 策略2：使用网关提供商 =====
    const gatewayProviders = ['openrouter', 'aihubmix'];
    for (const providerName of gatewayProviders) {
      const providerConfig = this.config.providers?.[providerName];
      if (providerConfig?.apiKey) {
        return providerName;
      }
    }

    // ===== 策略3：使用第一个配置好的提供商 =====
    // ... (省略部分代码)
  }

  /**
   * 发送聊天请求
   * @description 主要方法：调用 LLM 获取回复
   * 
   * @param messages - 消息列表
   * @param model - 模型名称
   * @param temperature - 温度参数
   * @param maxTokens - 最大 token 数
   * @param tools - 工具定义（可选）
   * @returns LLM 响应
   */
  async complete(
    messages: Message[],
    model: string,
    temperature: number,
    maxTokens: number,
    tools?: ToolDefinition[]
  ): Promise<LLMResponse> {
    // ===== 第1步：检测提供商 =====
    const providerName = this.detectProvider(model);
    
    // ===== 第2步：获取提供商实例 =====
    const provider = this.getProviderInstance(providerName);
    
    // ===== 第3步：调用提供商的 API =====
    return await provider.complete(
      messages,
      model,
      temperature,
      maxTokens,
      tools
    );
  }
}

/**
 * ============================================================
 * 基类：BaseProvider
 * ============================================================
 * 
 * 所有提供商的基类，定义统一接口
 */
export abstract class BaseProvider {
  protected apiKey: string;
  protected apiBase?: string;

  constructor(apiKey: string, apiBase?: string) {
    this.apiKey = apiKey;
    this.apiBase = apiBase;
  }

  /**
   * 发送聊天请求
   * @description 子类必须实现
   */
  abstract complete(
    messages: Message[],
    model: string,
    temperature: number,
    maxTokens: number,
    tools?: ToolDefinition[]
  ): Promise<LLMResponse>;
}

/**
 * ============================================================
 * 流程图：LLM 调用流程
 * ============================================================
 * 
 *              AgentLoop 调用 complete()
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ ProviderManager.complete()         │
 *     └────────────────┬───────────────────┘
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ detectProvider(model)              │
 *     │ 检测使用哪个提供商                  │
 *     └────────────────┬───────────────────┘
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ getProviderInstance()              │
 *     │ 获取或创建提供商实例                │
 *     └────────────────┬───────────────────┘
 *                        │
 *           ┌────────────┴────────────┐
 *           │ 缓存中                  │
 *           │ 有实例？                │
 *           └────────────┬────────────┘
 *                    ┌───┴───┐
 *                    │       │
 *                   是       否
 *                    │       │
 *                    ▼       ▼
 *            ┌───────────┐ ┌─────────────────┐
 *            │ 直接返回  │ │ 创建新实例      │
 *            │ 缓存实例  │ │ (根据类型)      │
 *            └─────┬─────┘ └────────┬────────┘
 *                  │                │
 *                  └────────┬───────┘
 *                           │
 *                           ▼
 *                ┌─────────────────────┐
 *                │ provider.complete() │
*                 │ 调用 LLM API        │
 *                └──────────┬──────────┘
 *                           │
 *                           ▼
 *                ┌─────────────────────┐
 *                │ 返回 LLMResponse    │
*                 │ (content + toolCalls)│
 *                └─────────────────────┘
 * 
 * ──────────────────────────────────────────────────────
 * 
 * 流程图：模型名到提供商的映射
 * 
 *              "anthropic/claude-3-opus"
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ findProviderByModel(model)         │
 *     └────────────────┬───────────────────┘
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ 解析模型名：                        │
 *     │ - "anthropic/*" -> anthropic       │
 *     │ - "openai/*" -> openai             │
 *     │ - "deepseek-chat" -> deepseek     │
 *     │ - "qwen-*" -> dashscope           │
 *     └────────────────┬───────────────────┘
 *                        │
 *                        ▼
 *                返回 "anthropic"
 * 
 * ──────────────────────────────────────────────────────
 * 
 * 流程图：配置示例
 * 
 *     config.json
 *     ┌────────────────────────────────────┐
 *     │ {                                  │
 *     │   "providers": {                   │
 *     │     "openrouter": {                │
 *     │       "apiKey": "sk-or-v1-xxx"    │
 *     │     },                             │
 *     │     "anthropic": {                 │
 *     │       "apiKey": "sk-ant-xxx"      │
 *     │     }                              │
 *     │   },                               │
 *     │   "agents": {                      │
 *     │     "defaults": {                  │
 *     │       "model": "anthropic/claude-3│
 *     │                     -opus-20240229"│
 *     │     }                              │
 *     │   }                                │
 *     │ }                                  │
 *     └────────────────────────────────────┘
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ detectProvider() 检测到            │
 *     │ "anthropic"                        │
 *     └────────────────┬───────────────────┘
 *                        │
 *                        ▼
 *     ┌────────────────────────────────────┐
 *     │ getProviderInstance('anthropic')   │
*     │ 返回 AnthropicProvider 实例         │
 *     └────────────────────────────────────┘
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建配置
 * const config = {
 *   providers: {
 *     openrouter: {
 *       apiKey: 'sk-or-v1-xxxx'
 *     },
 *     anthropic: {
 *       apiKey: 'sk-ant-xxxx'
 *     },
 *     deepseek: {
 *       apiKey: 'sk-xxxx',
 *       apiBase: 'https://api.deepseek.com/v1'
 *     }
 *   },
 *   agents: {
 *     defaults: {
 *       model: 'anthropic/claude-3-opus-20240229',
 *       temperature: 0.7,
 *       maxTokens: 4096
 *     }
 *   }
 * };
 * 
 * // 2. 创建 ProviderManager
 * const providerManager = new ProviderManager(config);
 * 
 * // 3. 准备消息
 * const messages = [
 *   { role: 'system', content: '你是一个有帮助的助手' },
 *   { role: 'user', content: '你好' }
 * ];
 * 
 * // 4. 调用 LLM（使用配置中的默认模型）
 * const response = await providerManager.complete(
 *   messages,
 *   config.agents.defaults.model,
 *   0.7,
 *   4096
 * );
 * 
 * console.log(response.content);  // AI 回复
 * console.log(response.toolCalls); // 工具调用（如果有）
 * 
 * // 5. 指定不同模型
 * const response2 = await providerManager.complete(
 *   messages,
 *   'deepseek/deepseek-chat',  // 使用 DeepSeek
 *   0.7,
 *   4096
 * );
 * 
 * // 6. 带工具调用
 * const tools = [
 *   {
 *     type: 'function',
 *     function: {
 *       name: 'shell',
 *       description: 'Execute shell commands',
 *       parameters: { ... }
 *     }
 *   }
 * ];
 * 
 * const response3 = await providerManager.complete(
 *   messages,
 *   'anthropic/claude-3-opus-20240229',
 *   0.7,
 *   4096,
 *   tools
 * );
 * 
 * ============================================================
 * 各提供商特点
 * ============================================================
 * 
 * | 提供商    | 优点                      | 缺点           |
 * |----------|--------------------------|---------------|
 * | OpenRouter | 一个 API 访问所有模型    | 略贵          |
 * | Anthropic | Claude 系列，能力最强    | 只有 Claude   |
 * | OpenAI    | GPT 系列，稳定可靠        | 国内访问慢    |
 * | DeepSeek  | 性价比高                  | 模型较少      |
 * | Gemini    | Google 品质               | 国内访问困难  |
 * | Dashscope | 阿里云，通义千问          | 只有阿里模型  |
 * | Moonshot  | Kimi 长文本处理          | 相对较新      |
 * | GLM       | 智谱清华，性价比高        | 模型较少      |
 * 
 * ============================================================
 * 添加新的提供商
 * ============================================================
 * 
 * 步骤：
 * 1. 在 providers/index.ts 的 switch 中添加 case
 * 2. 如需要，创建新的 Provider 类（继承 BaseProvider）
 * 3. 配置 apiKey 和 apiBase
 * 
 * 示例：添加 Ollama（本地模型）
 * 
 * // 1. 在 switch 中添加
 * case 'ollama':
 *   provider = new OpenAIProvider(
 *     providerConfig.apiKey,
 *     providerConfig.apiBase || 'http://localhost:11434/v1'
 *   );
 * break;
 * 
 * // 2. 配置使用
 * // config.json
 * {
 *   "providers": {
 *     "ollama": {
 *       "apiKey": "dummy",  // Ollama 不需要 key
 *       "apiBase": "http://localhost:11434/v1"
 *     }
 *   }
 * }
 * 
 * // 3. 使用
 * const response = await providerManager.complete(
 *   messages,
 *   'ollama/llama2',  // 模型名格式：提供商/模型名
 *   0.7,
 *   4096
 * );
 * 
 * ============================================================
 */