/**
 * ============================================================
 * nano-claw 核心代码详解 - AgentLoop (代理循环)
 * ============================================================
 * 
 * 这个文件是 nano-claw 框架的核心，负责处理用户消息并生成响应
 * 类似于 AI 机器人的"大脑"，执行以下流程：
 * 
 *   接收用户消息 → 构建上下文 → 调用 LLM → 执行工具 → 返回结果
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

// 导入各种类型定义和模块
import { AgentConfig, Message, ToolCall } from '../types';
import { ProviderManager } from '../providers/index';
import { Memory } from './memory';
import { ContextBuilder } from './context';
import { SkillsLoader } from './skills';
import { ToolRegistry } from './tools/registry';
import { ShellTool } from './tools/shell';
import { ReadFileTool, WriteFileTool } from './tools/file';
import { Config } from '../config/schema';
import { logger } from '../utils/logger';

/**
 * ============================================================
 * 类型定义
 * ============================================================
 */

/**
 * 代理响应接口
 * @description LLM 返回的响应结构
 */
export interface AgentResponse {
  content: string;          // 文本内容
  toolCalls?: ToolCall[];   // 工具调用列表（可选）
  finishReason?: string;    // 结束原因
}

/**
 * ============================================================
 * 核心类：AgentLoop (代理循环)
 * ============================================================
 * 
 * 这是 nano-claw 的核心类，负责：
 * 1. 管理对话上下文
 * 2. 与 LLM 通信
 * 3. 执行各种工具
 * 4. 维护对话历史
 */
export class AgentLoop {
  // ==================== 属性声明 ====================
  
  /** 代理配置 */
  private config: AgentConfig;
  
  /** LLM 提供商管理器 */
  private providerManager: ProviderManager;
  
  /** 对话记忆（持久化存储） */
  private memory: Memory;
  
  /** 上下文构建器 */
  private contextBuilder: ContextBuilder;
  
  /** 技能加载器 */
  private skillsLoader: SkillsLoader;
  
  /** 工具注册表 */
  private toolRegistry: ToolRegistry;
  
  /** 最大迭代次数（防止无限循环） */
  private maxIterations: number;

  // ==================== 构造函数 ====================
  
  /**
   * 构造函数
   * @param sessionId - 会话ID，用于标识不同的对话
   * @param config - 框架配置
   * @param agentConfig - 代理自定义配置（可选）
   * @param maxIterations - 最大迭代次数（默认10次）
   */
  constructor(
    sessionId: string,
    config: Config,
    agentConfig?: Partial<AgentConfig>,
    maxIterations = 10
  ) {
    // 合并配置：使用默认配置 + 用户自定义配置
    this.config = {
      // 默认模型
      model: config.agents?.defaults?.model || 'anthropic/claude-opus-4-5',
      // 默认温度（创造性程度）
      temperature: config.agents?.defaults?.temperature || 0.7,
      // 默认最大token数
      maxTokens: config.agents?.defaults?.maxTokens || 4096,
      // 系统提示词
      systemPrompt: config.agents?.defaults?.systemPrompt,
      // 合并用户自定义配置
      ...agentConfig,
    };

    // 初始化各个模块
    this.providerManager = new ProviderManager(config);  // LLM 提供商管理
    this.memory = new Memory(sessionId);                  // 记忆系统
    this.contextBuilder = new ContextBuilder(this.config); // 上下文构建
    this.skillsLoader = new SkillsLoader();               // 技能加载
    this.toolRegistry = new ToolRegistry();               // 工具注册
    this.maxIterations = maxIterations;

    // 注册内置工具
    this.registerBuiltInTools(config);
  }

  // ==================== 核心方法 ====================

  /**
   * 注册内置工具
   * @description 框架自带的基础工具
   */
  private registerBuiltInTools(config: Config): void {
    const toolsConfig = config.tools;

    // Shell 工具 - 执行命令行
    this.toolRegistry.register(
      new ShellTool(
        toolsConfig?.restrictToWorkspace,      // 是否限制在工作目录
        toolsConfig?.allowedCommands,          // 允许的命令
        toolsConfig?.deniedCommands            // 禁止的命令
      )
    );

    // 文件读取工具
    this.toolRegistry.register(new ReadFileTool());
    
    // 文件写入工具
    this.toolRegistry.register(new WriteFileTool());
  }

  /**
   * ============================================================
   * 核心方法：processMessage (处理消息)
   * ============================================================
   * 
   * 这是代理的主要入口方法，处理用户消息的完整流程：
   * 
   * ┌─────────────────┐
   * │  1. 接收消息    │
   * └────────┬────────┘
   *          ▼
   * ┌─────────────────┐
   * │  2. 添加到记忆  │
   * └────────┬────────┘
   *          ▼
   * ┌─────────────────┐
   * │  3. 进入循环    │◄──────────────┐
   * └────────┬────────┘               │
   *          ▼                        │
   * ┌─────────────────┐               │
   * │  4. 构建上下文  │               │
   * └────────┬────────┘               │
   *          ▼                        │
   * ┌─────────────────┐               │
   * │  5. 调用 LLM    │               │
   * └────────┬────────┘               │
   *          ▼                        │
   *    ┌─────────────┐                │
   *    │ LLM 要调用   │               │
   *    │   工具吗？   │               │
   *    └──────┬──────┘                │
   *           │                        │
   *     是 ◄──┴──► 否                  │
   *     │          │                  │
   *     ▼          ▼                  │
   * ┌────────┐ ┌────────────┐          │
   * │执行工具│ │ 返回结果   │──────────┘
   * │ 循环   │ │ 结束循环   │
   * └────────┘ └────────────┘
   * 
   * @param userMessage - 用户输入的消息
   * @returns 代理响应
   */
  async processMessage(userMessage: string): Promise<AgentResponse> {
    // ===== 第1步：将用户消息添加到记忆 =====
    this.memory.addMessage({
      role: 'user',
      content: userMessage,
    });

    // ===== 第2步：开始代理循环 =====
    let iteration = 0;           // 当前迭代次数
    let continueLoop = true;     // 是否继续循环
    let finalResponse: AgentResponse | null = null;  // 最终响应

    // ===== 第3步：循环执行，直到满足退出条件 =====
    while (continueLoop && iteration < this.maxIterations) {
      iteration++;
      logger.debug({ iteration, maxIterations: this.maxIterations }, 'Agent loop iteration');

      try {
        // ===== 3.1 构建上下文 =====
        // 获取技能列表
        const skills = this.skillsLoader.getSkills();
        
        // 获取工具定义（供 LLM 了解有哪些工具可用）
        const tools = this.toolRegistry.getDefinitions();
        
        // 获取对话历史
        const conversationMessages = this.memory.getMessages();
        
        // 构建发送给 LLM 的上下文消息
        const rawContextMessages = this.contextBuilder.buildContextMessages(
          conversationMessages,
          skills,
          tools
        );

        // ===== 3.2 截断上下文 =====
        // 防止超出模型的上下文窗口
        // 估算：maxTokens * 4 字符/token * 4 (上下文与响应比例)
        const CHARS_PER_TOKEN = 4;
        const CONTEXT_TO_RESPONSE_RATIO = 4;
        const maxContextChars = (this.config.maxTokens || 4096) * CHARS_PER_TOKEN * CONTEXT_TO_RESPONSE_RATIO;
        
        // 截断到合理长度
        const contextMessages = this.contextBuilder.truncateContext(
          rawContextMessages,
          maxContextChars
        );

        // ===== 3.3 调用 LLM =====
        const response = await this.providerManager.complete(
          contextMessages,
          this.config.model,
          this.config.temperature,
          this.config.maxTokens,
          tools
        );

        logger.debug(
          {
            iteration,
            hasContent: !!response.content,
            toolCallsCount: response.toolCalls?.length || 0,
            finishReason: response.finishReason,
          },
          'LLM response received'
        );

        // ===== 3.4 检查 LLM 是否要调用工具 =====
        if (response.toolCalls && response.toolCalls.length > 0) {
          // ===== 3.4.1 LLM 要求调用工具 =====
          
          // 将助手的消息（包含工具调用）添加到记忆
          this.memory.addMessage({
            role: 'assistant',
            content: response.content || '',
            tool_calls: response.toolCalls,
          });

          // ===== 3.4.2 执行每个工具调用 =====
          for (const toolCall of response.toolCalls) {
            const toolName = toolCall.function.name;
            let toolArgs: Record<string, unknown>;
            
            // 解析工具参数（JSON 字符串 → 对象）
            try {
              toolArgs = JSON.parse(toolCall.function.arguments) as Record<string, unknown>;
            } catch {
              // 参数解析失败，记录错误
              logger.warn(
                { tool: toolName, arguments: toolCall.function.arguments },
                'Invalid JSON in tool arguments, skipping tool call'
              );
              this.memory.addMessage({
                role: 'tool',
                content: `Error: Invalid JSON arguments for tool ${toolName}`,
                name: toolName,
                tool_call_id: toolCall.id,
              });
              continue;
            }

            logger.info({ tool: toolName, args: toolArgs }, 'Executing tool');

            // 执行工具
            const toolResult = await this.toolRegistry.execute(toolName, toolArgs);

            // ===== 3.4.3 将工具执行结果添加到记忆 =====
            this.memory.addMessage({
              role: 'tool',
              // 成功：返回输出，失败：返回错误信息
              content: toolResult.success ? toolResult.output : `Error: ${toolResult.error}`,
              name: toolName,
              tool_call_id: toolCall.id,
            });
          }

          // ===== 3.4.4 继续循环，获取最终响应 =====
          continueLoop = true;
        } else {
          // ===== 3.5 LLM 不需要调用工具，这就是最终响应 =====
          
          // 将助手消息添加到记忆
          this.memory.addMessage({
            role: 'assistant',
            content: response.content,
          });

          // 设置最终响应
          finalResponse = {
            content: response.content,
            finishReason: response.finishReason,
          };

          // 退出循环
          continueLoop = false;
        }
      } catch (error) {
        // ===== 错误处理 =====
        logger.error({ error, iteration }, 'Error in agent loop');
        throw error;
      }
    }

    // ===== 第4步：处理循环结束的情况 =====
    if (iteration >= this.maxIterations) {
      logger.warn({ maxIterations: this.maxIterations }, 'Max iterations reached');
    }

    // 如果没有获得有效响应，返回默认消息
    if (!finalResponse) {
      finalResponse = {
        content: 'I apologize, but I was unable to complete your request.',
        finishReason: 'max_iterations',
      };
    }

    return finalResponse;
  }

  // ==================== 辅助方法 ====================

  /**
   * 获取对话历史
   * @returns 消息列表
   */
  getHistory(): Message[] {
    return this.memory.getMessages();
  }

  /**
   * 清空对话历史
   */
  clearHistory(): void {
    this.memory.clear();
  }

  /**
   * 获取记忆实例（用于外部访问）
   */
  getMemory(): Memory {
    return this.memory;
  }

  /**
   * 获取工具注册表（用于外部访问）
   */
  getToolRegistry(): ToolRegistry {
    return this.toolRegistry;
  }

  /**
   * 获取技能加载器（用于外部访问）
   */
  getSkillsLoader(): SkillsLoader {
    return this.skillsLoader;
  }
}

/**
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建配置
 * const config = {
 *   providers: {
 *     openrouter: { apiKey: 'sk-or-v1-xxx' }
 *   },
 *   agents: {
 *     defaults: {
 *       model: 'anthropic/claude-opus-4-5',
 *       temperature: 0.7,
 *       maxTokens: 4096
 *     }
 *   }
 * };
 * 
 * // 2. 创建代理实例
 * const agent = new AgentLoop('session-123', config);
 * 
 * // 3. 处理用户消息
 * const response = await agent.processMessage('帮我写一个Hello World程序');
 * console.log(response.content);  // AI 的回复
 * 
 * // 4. 查看对话历史
 * const history = agent.getHistory();
 * 
 * // 5. 清空对话
 * agent.clearHistory();
 * 
 * ============================================================
 * 流程图：完整的消息处理流程
 * ============================================================
 * 
 *                    用户发送消息
 *                         │
 *                         ▼
 *            ┌────────────────────────┐
 *            │  AgentLoop.processMessage │
 *            └────────────┬───────────┘
 *                         │
 *                         ▼
 *            ┌────────────────────────┐
 *            │   添加到 Memory        │
 *            │ (对话历史持久化)       │
 *            └────────────┬───────────┘
 *                         │
 *                         ▼
 *            ┌────────────────────────┐
 *            │   开始循环 (max 10次)   │
 *            └────────────┬───────────┘
 *                         │
 *           ┌─────────────┴─────────────┐
 *           │                           │
 *           ▼                           ▼
 *    ┌─────────────┐            ┌─────────────┐
 *    │ 构建上下文   │            │  调用 LLM   │
 *    │ (Skills +   │───────────►│ (Provider)  │
 *    │  Tools)     │            └──────┬──────┘
 *    └─────────────┘                   │
 *                                       │
 *                                       ▼
 *                              ┌───────────────┐
 *                              │ LLM 返回响应   │
 *                              └───────┬───────┘
 *                                      │
 *                          ┌───────────┴───────────┐
 *                          │                       │
 *                          ▼                       ▼
 *                   ┌─────────────┐         ┌─────────────┐
 *                   │ 需要调用工具 │         │ 不需要工具  │
 *                   │   (是)      │         │   (否)      │
 *                   └──────┬──────┘         └──────┬──────┘
 *                          │                       │
 *                          ▼                       ▼
 *                   ┌─────────────┐         ┌─────────────┐
 *                   │ 工具注册表   │         │  返回结果   │
 *                   │ ToolRegistry│         │  结束循环   │
 *                   │  执行工具   │         └─────────────┘
 *                   └──────┬──────┘
 *                          │
 *                          ▼
 *                   ┌─────────────┐
 *                   │ 结果加入记忆 │
 *                   │ 继续循环    │
 *                   └──────┬──────┘
 *                          │
 *                          └──────────► (返回循环开始)
 * 
 * ============================================================
 */