/**
 * ============================================================
 * nano-claw 核心代码详解 - ContextBuilder (上下文构建器)
 * ============================================================
 * 
 * ContextBuilder 负责构建发送给 LLM 的上下文，包括：
 * - 系统提示词
 * - 可用技能列表
 * - 可用工具列表
 * - 对话历史
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

import { Message, Skill, ToolDefinition, AgentConfig } from '../types';
import { formatDate } from '../utils/helpers';

/**
 * ============================================================
 * 核心类：ContextBuilder
 * ============================================================
 * 
 * 作用：构建完整的上下文，让 LLM 知道：
 * 1. 它是什么角色（系统提示词）
 * 2. 当前时间
 * 3. 它有什么能力（技能）
 * 4. 它能用什么工具
 * 5. 之前聊了什么（对话历史）
 */
export class ContextBuilder {
  // ==================== 属性 ====================
  
  /** 代理配置 */
  private config: AgentConfig;

  // ==================== 构造函数 ====================
  
  constructor(config: AgentConfig) {
    this.config = config;
  }

  // ==================== 核心方法 ====================

  /**
   * 构建系统提示词
   * @description 组合基础提示词、时间、技能和工具信息
   * 
   * @param skills - 可用技能列表
   * @param tools - 可用工具定义列表
   * @returns 完整的系统提示词字符串
   * 
   * 构建流程：
   * 1. 基础提示词（默认或自定义）
   * 2. 当前时间
   * 3. 技能列表
   * 4. 工具列表
   */
  buildSystemPrompt(skills: Skill[], tools: ToolDefinition[]): string {
    const parts: string[] = [];

    // ===== 第1步：添加基础系统提示词 =====
    if (this.config.systemPrompt) {
      // 使用用户自定义的系统提示词
      parts.push(this.config.systemPrompt);
    } else {
      // 使用默认系统提示词
      parts.push(this.getDefaultSystemPrompt());
    }

    // ===== 第2步：添加当前时间 =====
    parts.push(`\nCurrent time: ${formatDate(new Date())}`);

    // ===== 第3步：添加技能信息 =====
    if (skills.length > 0) {
      parts.push('\n## Available Skills');
      parts.push(
        'You have access to the following skills that provide additional context and capabilities:\n'
      );
      
      // 遍历每个技能，添加名称和描述
      for (const skill of skills) {
        parts.push(`### ${skill.name}`);
        parts.push(skill.description);
        parts.push('');  // 空行分隔
      }
    }

    // ===== 第4步：添加工具信息 =====
    if (tools.length > 0) {
      parts.push('\n## Available Tools');
      parts.push('You can use the following tools to perform actions:\n');
      
      // 遍历每个工具，添加名称和描述
      for (const tool of tools) {
        parts.push(`- **${tool.function.name}**: ${tool.function.description}`);
      }
      parts.push('');
    }

    // 组合所有部分
    return parts.join('\n');
  }

  /**
   * 获取默认系统提示词
   * @returns 默认的系统提示词
   */
  private getDefaultSystemPrompt(): string {
    return `You are a helpful AI assistant powered by nano-claw. You are knowledgeable, precise, and aim to be helpful.

Your capabilities:
- Answer questions accurately and concisely
- Execute tasks using available tools
- Remember context from the conversation
- Use skills to enhance your knowledge and capabilities

Guidelines:
- Be honest if you don't know something
- Use tools when they can help accomplish the task
- Keep responses clear and well-structured
- Respect user privacy and security`;
  }

  /**
   * 构建完整的上下文消息
   * @description 组合系统提示词和对话历史
   * 
   * @param conversationMessages - 对话历史消息
   * @param skills - 可用技能
   * @param tools - 可用工具
   * @returns 完整的消息列表（可发送给 LLM）
   * 
   * 返回格式：
   * [
   *   { role: 'system', content: '你是...' },
   *   { role: 'user', content: '你好' },
   *   { role: 'assistant', content: '你好！' }
   * ]
   */
  buildContextMessages(
    conversationMessages: Message[],
    skills: Skill[],
    tools: ToolDefinition[]
  ): Message[] {
    const messages: Message[] = [];

    // ===== 第1步：添加系统消息（包含完整上下文） =====
    const systemPrompt = this.buildSystemPrompt(skills, tools);
    messages.push({
      role: 'system',
      content: systemPrompt,
    });

    // ===== 第2步：添加对话历史 =====
    messages.push(...conversationMessages);

    return messages;
  }

  /**
   * 截断上下文
   * @description 当上下文过长时，裁剪到合理大小
   * 
   * @param messages - 完整消息列表
   * @param maxLength - 最大字符数
   * @returns 截断后的消息列表
   * 
   * 截断策略：
   * 1. 始终保留系统消息
   * 2. 从后往前保留对话历史
   * 3. 优先保留最近的消息
   */
  truncateContext(messages: Message[], maxLength: number): Message[] {
    // 分离系统消息和其他消息
    const systemMessages = messages.filter((m) => m.role === 'system');
    const otherMessages = messages.filter((m) => m.role !== 'system');

    // 计算总长度
    let totalLength = 0;
    for (const msg of messages) {
      totalLength += msg.content.length;
    }

    // 如果已经小于限制，直接返回
    if (totalLength <= maxLength) {
      return messages;
    }

    // 从后往前保留消息
    const recentMessages: Message[] = [];
    let currentLength = systemMessages.reduce((sum, m) => sum + m.content.length, 0);

    // 如果系统消息本身就超过限制，只返回系统消息
    if (currentLength >= maxLength) {
      return systemMessages;
    }

    // 从最后一条消息开始向前添加
    for (let i = otherMessages.length - 1; i >= 0; i--) {
      const msg = otherMessages[i];
      
      // 如果加上这个消息会超过限制，停止
      if (currentLength + msg.content.length > maxLength) {
        break;
      }
      
      // 添加到开头（保持顺序）
      recentMessages.unshift(msg);
      currentLength += msg.content.length;
    }

    // 合并系统消息和保留的消息
    return [...systemMessages, ...recentMessages];
  }

  /**
   * 格式化工具结果
   * @description 用于日志或调试显示
   */
  formatToolResult(toolName: string, result: string): string {
    return `[Tool: ${toolName}]\n${result}`;
  }
}

/**
 * ============================================================
 * 流程图：上下文构建流程
 * ============================================================
 * 
 *                  AgentLoop 调用 buildContextMessages
 *                               │
 *                               ▼
 *              ┌────────────────────────────────┐
 *              │   buildContextMessages()       │
 *              └─────────────┬──────────────────┘
 *                            │
 *                            ▼
 *              ┌────────────────────────────────┐
 *              │   buildSystemPrompt()          │
 *              │   构建系统提示词               │
 *              └─────────────┬──────────────────┘
 *                            │
 *              ┌─────────────┴─────────────┐
 *              │                           │
 *              ▼                           ▼
 *      ┌───────────────┐          ┌───────────────┐
 *      │ 自定义提示词？ │          │ 添加当前时间  │
 *      │               │          │               │
 *      └───────┬───────┘          └───────┬───────┘
 *              │                           │
 *             是                           │
 *              │                           │
 *              ▼                           │
 *      ┌───────────────┐                   │
 *      │ 使用自定义    │                   │
 *      └───────┬───────┘                   │
 *              │                           │
 *              └─────────────┬─────────────┘
 *                            │
 *                            ▼
 *              ┌────────────────────────────────┐
 *              │   添加技能信息 (Skills)        │
 *              │   "## Available Skills"        │
 *              └─────────────┬──────────────────┘
 *                            │
 *                            ▼
 *              ┌────────────────────────────────┐
 *              │   添加工具信息 (Tools)         │
 *              │   "## Available Tools"         │
 *              └─────────────┬──────────────────┘
 *                            │
 *                            ▼
 *              ┌────────────────────────────────┐
 *              │   返回完整的系统提示词         │
 *              └─────────────┬──────────────────┘
 *                            │
 *                            ▼
 *              ┌────────────────────────────────┐
 *              │   组合成完整消息列表           │
 *              │   [system, user, assistant...] │
 *              └─────────────┬──────────────────┘
 *                            │
 *                            ▼
 *              ┌────────────────────────────────┐
 *              │   truncateContext()            │
 *              │   检查是否需要截断             │
 *              └─────────────┬──────────────────┘
 *                            │
 *              ┌─────────────┴─────────────┐
 *              │                           │
 *             是                           否
 *              │                           │
 *              ▼                           ▼
 *      ┌───────────────┐          ┌───────────────┐
 *      │ 保留系统消息  │          │ 返回完整列表  │
 *      │ + 最近消息    │          │               │
 *      └───────┬───────┘          └───────┬───────┘
 *              │                           │
 *              └─────────────┬─────────────┘
 *                            │
 *                            ▼
 *                  返回给 AgentLoop
 * 
 * ============================================================
 * 系统提示词示例
 * ============================================================
 * 
 * 生成的系统提示词大致如下：
 * 
 * ```
 * You are a helpful AI assistant powered by nano-claw. You are knowledgeable, 
 * precise, and aim to be helpful.
 * 
 * Your capabilities:
 * - Answer questions accurately and concisely
 * - Execute tasks using available tools
 * - Remember context from the conversation
 * - Use skills to enhance your knowledge and capabilities
 * 
 * Guidelines:
 * - Be honest if you don't know something
 * - Use tools when they can help accomplish the task
 * - Keep responses clear and well-structured
 * - Respect user privacy and security
 * 
 * Current time: 2026-03-12 10:30:00
 * 
 * ## Available Skills
 * You have access to the following skills that provide additional context and capabilities:
 * 
 * ### GitHub
 * GitHub 操作技能，支持 issues、PR 等
 * 
 * ### Weather
 * 查询天气信息
 * 
 * ## Available Tools
 * You can use the following tools to perform actions:
 * 
 * - **shell**: Execute shell commands
 * - **read_file**: Read contents of a file
 * - **write_file**: Write content to a file
 * ```
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建配置
 * const config: AgentConfig = {
 *   model: 'anthropic/claude-opus-4-5',
 *   temperature: 0.7,
 *   maxTokens: 4096
 * };
 * 
 * // 2. 创建上下文构建器
 * const contextBuilder = new ContextBuilder(config);
 * 
 * // 3. 准备数据
 * const skills = [
 *   { name: 'GitHub', description: 'GitHub 操作技能', content: '...', path: '/path' }
 * ];
 * const tools = [
 *   { type: 'function', function: { name: 'shell', description: '执行命令', parameters: {...} } }
 * ];
 * const conversationMessages = [
 *   { role: 'user', content: '你好' },
 *   { role: 'assistant', content: '你好！' }
 * ];
 * 
 * // 4. 构建上下文
 * const messages = contextBuilder.buildContextMessages(
 *   conversationMessages,
 *   skills,
 *   tools
 * );
 * 
 * // 5. 发送给 LLM
 * const response = await llm.complete(messages);
 * 
 * ============================================================
 */