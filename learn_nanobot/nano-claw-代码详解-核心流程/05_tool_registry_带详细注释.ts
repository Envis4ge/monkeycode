/**
 * ============================================================
 * nano-claw 核心代码详解 - ToolRegistry (工具注册表)
 * ============================================================
 * 
 * ToolRegistry 是工具管理系统，负责：
 * - 注册工具
 * - 存储工具
 * - 提供工具定义给 LLM
 * - 执行工具
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

import { ToolDefinition, ToolResult } from '../../types';
import { logger } from '../../utils/logger';

/**
 * ============================================================
 * 类型定义
 * ============================================================
 */

/**
 * 工具结果
 * @description 工具执行后的返回结果
 */
interface ToolResult {
  success: boolean;    // 是否成功
  output: string;      // 输出内容
  error?: string;      // 错误信息（可选）
}

/**
 * 工具定义
 * @description 供 LLM 了解工具的元数据
 */
interface ToolDefinition {
  type: string;
  function: {
    name: string;          // 工具名称
    description: string;   // 工具描述
    parameters: object;    // 参数 schema
  };
}

/**
 * ============================================================
 * 基类：BaseTool
 * ============================================================
 * 
 * 所有工具的基类，定义工具的接口规范
 * 
 * 为什么要用基类？
 * - 统一工具的行为
 * - 代码复用
 * - 便于扩展
 */
export abstract class BaseTool {
  /** 工具名称 */
  abstract name: string;
  
  /** 工具描述 */
  abstract description: string;

  /**
   * 获取工具定义
   * @description 供 LLM 了解工具有什么能力
   * @returns 工具定义对象
   */
  abstract getDefinition(): ToolDefinition;

  /**
   * 执行工具
   * @description 实际执行工具逻辑
   * @param args - 工具参数
   * @returns 执行结果
   */
  abstract execute(args: Record<string, unknown>): Promise<ToolResult>;

  /**
   * 辅助方法：创建成功结果
   */
  protected success(output: string): ToolResult {
    return {
      success: true,
      output,
    };
  }

  /**
   * 辅助方法：创建错误结果
   */
  protected error(error: string): ToolResult {
    return {
      success: false,
      output: '',
      error,
    };
  }
}

/**
 * ============================================================
 * 核心类：ToolRegistry (工具注册表)
 * ============================================================
 * 
 * 就像一个"工具箱"，管理所有可用的工具
 * 
 * 功能：
 * 1. 注册新工具
 * 2. 根据名称查找工具
 * 3. 获取所有工具定义
 * 4. 执行工具
 */
export class ToolRegistry {
  // ==================== 属性 ====================
  
  /** 工具存储 Map，key 是工具名 */
  private tools: Map<string, BaseTool> = new Map();

  // ==================== 核心方法 ====================

  /**
   * 注册工具
   * @description 将工具添加到注册表
   * 
   * @param tool - 工具实例（必须继承 BaseTool）
   * 
   * 示例：
   * registry.register(new ShellTool());
   * registry.register(new ReadFileTool());
   */
  register(tool: BaseTool): void {
    // key 是工具名，value 是工具实例
    this.tools.set(tool.name, tool);
    logger.debug({ tool: tool.name }, 'Tool registered');
  }

  /**
   * 根据名称获取工具
   * @param name - 工具名称
   * @returns 工具实例或 undefined
   */
  get(name: string): BaseTool | undefined {
    return this.tools.get(name);
  }

  /**
   * 获取所有工具定义
   * @description 用于告知 LLM 有哪些工具可用
   * @returns 工具定义数组
   * 
   * 返回格式示例：
   * [
   *   {
   *     type: 'function',
   *     function: {
   *       name: 'shell',
   *       description: 'Execute shell commands',
   *       parameters: { type: 'object', properties: {...} }
   *     }
   *   },
   *   {
   *     type: 'function',
   *     function: {
   *       name: 'read_file',
   *       description: 'Read contents of a file',
   *       parameters: { type: 'object', properties: {...} }
   *     }
   *   }
   * ]
   */
  getDefinitions(): ToolDefinition[] {
    // 遍历所有工具，获取每个工具的定义
    return Array.from(this.tools.values()).map((tool) => tool.getDefinition());
  }

  /**
   * 执行工具
   * @description 根据名称和参数执行对应的工具
   * 
   * @param name - 工具名称
   * @param args - 工具参数
   * @returns 执行结果
   * 
   * 执行流程：
   * 1. 查找工具
   * 2. 调用工具的 execute 方法
   * 3. 返回结果
   */
  async execute(name: string, args: Record<string, unknown>): Promise<ToolResult> {
    // ===== 第1步：查找工具 =====
    const tool = this.tools.get(name);
    
    // 如果工具不存在
    if (!tool) {
      return {
        success: false,
        output: '',
        error: `Tool not found: ${name}`,
      };
    }

    // ===== 第2步：执行工具 =====
    try {
      logger.info({ tool: name, args }, 'Executing tool');
      
      // 调用工具的 execute 方法
      return await tool.execute(args);
    } catch (error) {
      // ===== 错误处理 =====
      logger.error({ error, tool: name }, 'Tool execution failed');
      
      return {
        success: false,
        output: '',
        error: `Tool execution failed: ${(error as Error).message}`,
      };
    }
  }

  /**
   * 获取工具数量
   * @returns 注册的工具总数
   */
  getToolCount(): number {
    return this.tools.size;
  }
}

/**
 * ============================================================
 * 流程图：工具注册与执行流程
 * ============================================================
 * 
 * ┌─────────────────────────────────────────────────────────┐
 *                    工具注册流程
 * └─────────────────────────────────────────────────────────┘
 * 
 *          AgentLoop 构造函数
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ registerBuiltInTools() │
 *     └────────────┬───────────┘
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ new ShellTool()        │◄── 创建工具实例
 *     │ new ReadFileTool()     │
 *     │ new WriteFileTool()    │
 *     └────────────┬───────────┘
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ toolRegistry.register()│
 *     └────────────┬───────────┘
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ tools.set(name, tool)  │
 *     │ 存入 Map               │
 *     └────────────────────────┘
 * 
 * ──────────────────────────────────────────────────────────
 * 
 * ┌─────────────────────────────────────────────────────────┐
 *                    工具执行流程
 * └─────────────────────────────────────────────────────────┘
 * 
 *              LLM 返回 tool_calls
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │  AgentLoop.processMessage()    │
 *     │  for (toolCall of toolCalls)   │
 *     └────────────┬───────────────────┘
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ toolRegistry.execute(name, args)│
 *     └────────────┬───────────────────┘
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │  tools.get(name) 查找工具       │
 *     └────────────┬───────────────────┘
 *                      │
 *          ┌─────────┴─────────┐
 *          │                   │
 *         存在                 不存在
 *          │                   │
 *          ▼                   ▼
 *   ┌────────────┐    ┌────────────────┐
 *   │ tool.execute│    │ 返回错误       │
 *   │   (args)   │    │ "Tool not found"│
 *   └─────┬──────┘    └────────────────┘
 *         │
 *         ▼
 *   ┌────────────┐
 *   │ 返回结果   │
 *   │ success    │
 *   │ output     │
 *   │ error      │
 *   └─────┬──────┘
 *         │
 *         ▼
 *   ┌────────────────────────────────┐
 *   │ 添加到 Memory (role: 'tool')   │
 *   └────────────────────────────────┘
 * 
 * ──────────────────────────────────────────────────────────
 * 
 * ┌─────────────────────────────────────────────────────────┐
 *                 LLM 获取工具列表流程
 * └─────────────────────────────────────────────────────────┘
 * 
 *              构建上下文时
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ toolRegistry.getDefinitions()│
 *     └────────────┬───────────┘
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ 遍历 tools.values()    │
 *     │ map(tool => tool.getDefinition())│
 *     └────────────┬───────────┘
 *                  │
 *                  ▼
 *     ┌────────────────────────┐
 *     │ 返回 ToolDefinition[]  │
 *     │ 发送给 LLM             │
 *     └────────────────────────┘
 * 
 * ============================================================
 * 工具定义示例
 * ============================================================
 * 
 * Shell 工具的定义：
 * ```json
 * {
 *   "type": "function",
 *   "function": {
 *     "name": "shell",
 *     "description": "Execute shell commands",
 *     "parameters": {
 *       "type": "object",
 *       "properties": {
 *         "command": {
 *           "type": "string",
 *           "description": "The shell command to execute"
 *         }
 *       },
 *       "required": ["command"]
 *     }
 *   }
 * }
 * ```
 * 
 * ReadFile 工具的定义：
 * ```json
 * {
 *   "type": "function",
 *   "function": {
 *     "name": "read_file",
 *     "description": "Read contents of a file",
 *     "parameters": {
 *       "type": "object",
 *       "properties": {
 *         "path": {
 *           "type": "string",
 *           "description": "Path to the file to read"
 *         }
 *       },
 *       "required": ["path"]
 *     }
 *   }
 * }
 * ```
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建工具注册表
 * const registry = new ToolRegistry();
 * 
 * // 2. 注册工具
 * registry.register(new ShellTool());
 * registry.register(new ReadFileTool());
 * registry.register(new WriteFileTool());
 * 
 * // 3. 查看工具数量
 * console.log(registry.getToolCount()); // 3
 * 
 * // 4. 获取所有工具定义（供 LLM 使用）
 * const definitions = registry.getDefinitions();
 * 
 * // 5. 执行工具
 * // 5.1 执行 shell 命令
 * const shellResult = await registry.execute('shell', {
 *   command: 'ls -la'
 * });
 * console.log(shellResult.success);  // true
 * console.log(shellResult.output);   // 文件列表
 * 
 * // 5.2 读取文件
 * const readResult = await registry.execute('read_file', {
 *   path: '/path/to/file.txt'
 * });
 * 
 * // 5.3 写入文件
 * const writeResult = await registry.execute('write_file', {
 *   path: '/path/to/file.txt',
 *   content: 'Hello World'
 * });
 * 
 * // 6. 获取特定工具
 * const shellTool = registry.get('shell');
 * if (shellTool) {
 *   // 进一步操作...
 * }
 * 
 * // 7. 执行不存在的工具
 * const badResult = await registry.execute('nonexistent', {});
 * console.log(badResult.success);  // false
 * console.log(badResult.error);    // "Tool not found: nonexistent"
 * 
 * ============================================================
 * 内置工具列表
 * ============================================================
 * 
 * | 工具名称      | 功能               | 参数                  |
 * |--------------|-------------------|----------------------|
 * | shell        | 执行 Shell 命令    | command: string     |
 * | read_file    | 读取文件           | path: string        |
 * | write_file   | 写入文件           | path, content       |
 * 
 * 扩展自定义工具：
 * 
 * class MyTool extends BaseTool {
 *   name = 'my_tool';
 *   description = '我的自定义工具';
 *   
 *   getDefinition() {
 *     return {
 *       type: 'function',
 *       function: {
 *         name: this.name,
 *         description: this.description,
 *         parameters: {
 *           type: 'object',
 *           properties: {
 *             param1: { type: 'string', description: '参数1' }
 *           },
 *           required: ['param1']
 *         }
 *       }
 *     };
 *   }
 *   
 *   async execute(args) {
 *     // 自定义逻辑
 *     return this.success('执行成功');
 *   }
 * }
 * 
 * // 注册自定义工具
 * registry.register(new MyTool());
 * 
 * ============================================================
 */