/**
 * ============================================================
 * nano-claw 核心代码详解 - Memory (记忆系统)
 * ============================================================
 * 
 * Memory 是 nano-claw 的记忆模块，负责：
 * - 持久化存储对话历史
 * - 管理会话上下文
 * - 自动清理旧消息
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { Message } from '../types';
import { getMemoryDir } from '../utils/helpers';
import { logger } from '../utils/logger';

/**
 * ============================================================
 * 类型定义
 * ============================================================
 */

/**
 * 消息结构
 * @description 对话中的每条消息
 */
interface Message {
  role: 'system' | 'user' | 'assistant' | 'tool';  // 消息角色
  content: string;                                  // 消息内容
  tool_calls?: ToolCall[];                          // 工具调用（可选）
  name?: string;                                    // 工具名称（可选）
  tool_call_id?: string;                            // 工具调用ID（可选）
}

/**
 * 工具调用结构
 */
interface ToolCall {
  id: string;                    // 调用ID
  type: string;                  // 调用类型
  function: {
    name: string;                // 函数名
    arguments: string;           // 函数参数（JSON字符串）
  };
}

/**
 * ============================================================
 * 核心类：Memory (记忆)
 * ============================================================
 * 
 * 功能：
 * 1. 加载历史对话记录
 * 2. 添加新消息
 * 3. 自动保存到磁盘
 * 4. 自动清理旧消息
 * 
 * 存储位置：~/.nano-claw/memory/{sessionId}.json
 */
export class Memory {
  // ==================== 属性 ====================
  
  /** 会话ID（用于区分不同对话） */
  private sessionId: string;
  
  /** 内存中的消息列表 */
  private messages: Message[] = [];
  
  /** 最大消息数量（超过则清理旧消息） */
  private maxMessages: number;
  
  /** 记忆文件路径 */
  private memoryPath: string;

  // ==================== 构造函数 ====================
  
  /**
   * 构造函数
   * @param sessionId - 会话ID
   * @param maxMessages - 最大保存消息数（默认100条）
   */
  constructor(sessionId: string, maxMessages = 100) {
    this.sessionId = sessionId;
    this.maxMessages = maxMessages;

    // 获取记忆存储目录
    const memoryDir = getMemoryDir();
    
    // 如果目录不存在，创建它
    if (!existsSync(memoryDir)) {
      mkdirSync(memoryDir, { recursive: true });
    }

    // 设置文件路径：~/.nano-claw/memory/{sessionId}.json
    this.memoryPath = join(memoryDir, `${sessionId}.json`);
    
    // 加载历史消息
    this.load();
  }

  // ==================== 核心方法 ====================

  /**
   * 从磁盘加载消息
   * @description 启动时自动调用，加载历史对话
   * 
   * 流程：
   * 1. 检查文件是否存在
   * 2. 读取文件内容
   * 3. 解析 JSON
   * 4. 存入内存
   */
  private load(): void {
    // 检查记忆文件是否存在
    if (existsSync(this.memoryPath)) {
      try {
        // 读取文件
        const data = readFileSync(this.memoryPath, 'utf-8');
        
        // 解析 JSON
        const parsed = JSON.parse(data) as Message[];
        
        // 存入内存
        this.messages = parsed;
        
        logger.debug({ sessionId: this.sessionId, count: this.messages.length }, 'Memory loaded');
      } catch (error) {
        // 加载失败，记录错误，使用空记忆
        logger.error({ error, sessionId: this.sessionId }, 'Failed to load memory');
        this.messages = [];
      }
    }
  }

  /**
   * 保存消息到磁盘
   * @description 每次添加消息后自动调用
   * 
   * 流程：
   * 1. 将消息列表转为 JSON 字符串
   * 2. 写入文件
   * 
   * 文件格式示例：
   * [
   *   {"role": "user", "content": "你好"},
   *   {"role": "assistant", "content": "你好！有什么可以帮你的？"}
   * ]
   */
  private save(): void {
    try {
      // 转换为格式化的 JSON 字符串
      const data = JSON.stringify(this.messages, null, 2);
      
      // 写入文件
      writeFileSync(this.memoryPath, data, 'utf-8');
      
      logger.debug({ sessionId: this.sessionId, count: this.messages.length }, 'Memory saved');
    } catch (error) {
      // 保存失败，记录错误
      logger.error({ error, sessionId: this.sessionId }, 'Failed to save memory');
    }
  }

  /**
   * 添加消息到记忆
   * @param message - 要添加的消息
   * 
   * 添加流程：
   * 1. 将消息加入列表末尾
   * 2. 检查是否超过最大数量
   * 3. 如果超过，删除最旧的消息（保留系统消息）
   * 4. 保存到磁盘
   */
  addMessage(message: Message): void {
    // 添加到列表末尾
    this.messages.push(message);

    // 检查是否超过最大数量
    if (this.messages.length > this.maxMessages) {
      // ===== 自动清理策略 =====
      
      // 1. 保留所有系统消息（系统消息很重要，不能删除）
      const systemMessages = this.messages.filter((m) => m.role === 'system');
      
      // 2. 从非系统消息中保留最近的消息
      const otherMessages = this.messages
        .filter((m) => m.role !== 'system')
        .slice(-this.maxMessages);  // 只保留最近 N 条
      
      // 3. 合并
      this.messages = [...systemMessages, ...otherMessages];
    }

    // 保存到磁盘
    this.save();
  }

  // ==================== 查询方法 ====================

  /**
   * 获取所有消息
   * @returns 消息列表（副本）
   */
  getMessages(): Message[] {
    // 返回副本，防止外部修改内部数据
    return [...this.messages];
  }

  /**
   * 获取最近 N 条消息
   * @param count - 消息数量
   * @returns 最近的消息列表
   */
  getRecentMessages(count: number): Message[] {
    return this.messages.slice(-count);
  }

  /**
   * 获取消息数量
   * @returns 消息总数
   */
  getMessageCount(): number {
    return this.messages.length;
  }

  // ==================== 管理方法 ====================

  /**
   * 清空所有消息
   * @description 用于开始新对话
   */
  clear(): void {
    this.messages = [];
    this.save();
  }

  /**
   * 更新最后一条消息
   * @param content - 新的内容
   * @description 用于修正或补充 AI 的回复
   */
  updateLastMessage(content: string): void {
    if (this.messages.length > 0) {
      this.messages[this.messages.length - 1].content = content;
      this.save();
    }
  }
}

/**
 * ============================================================
 * 流程图：记忆系统工作流程
 * ============================================================
 * 
 *                    ┌─────────────────┐
 *                    │  创建 Memory    │
 *                    │   实例          │
 *                    └────────┬────────┘
 *                             │
 *                             ▼
 *                    ┌─────────────────┐
 *                    │   检查记忆文件   │
 *                    │ 是否存在？       │
 *                    └────────┬────────┘
 *                             │
 *                    ┌────────┴────────┐
 *                    │                 │
 *                   是                 否
 *                    │                 │
 *                    ▼                 ▼
 *            ┌─────────────┐   ┌─────────────┐
 *            │  加载历史   │   │  初始化空   │
 *            │  消息       │   │  消息列表   │
 *            └──────┬──────┘   └──────┬──────┘
 *                   │                 │
 *                   └────────┬────────┘
 *                            │
 *                            ▼
 *                   ┌─────────────────┐
 *                   │   addMessage()  │
 *                   │   被调用        │
 *                   └────────┬────────┘
 *                            │
 *                            ▼
 *                   ┌─────────────────┐
 *                   │  添加消息到     │
 *                   │  列表末尾       │
 *                   └────────┬────────┘
 *                            │
 *                            ▼
 *                   ┌─────────────────┐
 *                   │ 消息数量超过   │
 *                   │ maxMessages?    │
 *                   └────────┬────────┘
 *                            │
 *                   ┌────────┴────────┐
 *                   │                 │
 *                  是                 否
 *                   │                 │
 *                   ▼                 ▼
 *           ┌─────────────┐   ┌─────────────┐
 *           │  保留系统消息 │   │  save()    │
 *           │  + 最近N条   │   │  保存到磁盘 │
 *           │  (自动清理)  │   └────────┬────────┘
 *           └──────┬──────┘            │
 *                  │                   │
 *                  └────────┬────────┘
 *                           │
 *                           ▼
 *                   ┌─────────────────┐
 *                   │    完成 ✅      │
 *                   └─────────────────┘
 * 
 * ============================================================
 * 消息角色说明
 * ============================================================
 * 
 * | 角色       | 说明                 | 示例                    |
 * |------------|----------------------|------------------------|
 * | system     | 系统提示词           | "你是一个有帮助的助手"  |
 * | user       | 用户消息             | "帮我写个程序"          |
 * | assistant  | AI 助手回复          | "好的，我来帮你..."     |
 * | tool       | 工具执行结果         | "文件已创建成功"        |
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建记忆实例
 * const memory = new Memory('session-001', 100);
 * 
 * // 2. 添加用户消息
 * memory.addMessage({
 *   role: 'user',
 *   content: '你好'
 * });
 * 
 * // 3. 添加助手回复
 * memory.addMessage({
 *   role: 'assistant',
 *   content: '你好！有什么可以帮你的？'
 * });
 * 
 * // 4. 获取所有消息
 * const messages = memory.getMessages();
 * 
 * // 5. 获取最近5条消息
 * const recent = memory.getRecentMessages(5);
 * 
 * // 6. 查看消息数量
 * console.log(memory.getMessageCount()); // 2
 * 
 * // 7. 清空对话
 * memory.clear();
 * 
 * ============================================================
 * 文件存储格式
 * ============================================================
 * 
 * 存储位置: ~/.nano-claw/memory/session-001.json
 * 
 * 文件内容示例:
 * ```json
 * [
 *   {
 *     "role": "system",
 *     "content": "你是一个有帮助的AI助手"
 *   },
 *   {
 *     "role": "user",
 *     "content": "帮我写一个Hello World"
 *   },
 *   {
 *     "role": "assistant", 
 *     "content": "好的，我来帮你写一个Hello World程序..."
 *   },
 *   {
 *     "role": "tool",
 *     "content": "文件已创建: /path/to/hello.js",
 *     "name": "write_file",
 *     "tool_call_id": "call_abc123"
 *   }
 * ]
 * ```
 * 
 * ============================================================
 */