/**
 * ============================================================
 * nano-claw 核心代码详解 - ShellTool (Shell 命令执行工具)
 * ============================================================
 * 
 * ShellTool 是内置的工具之一，允许 AI 执行命令行命令
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { BaseTool } from './registry';
import { ToolDefinition, ToolResult } from '../../types';

// 将 exec 转换为 Promise 形式
const execAsync = promisify(exec);

/**
 * ============================================================
 * 核心类：ShellTool
 * ============================================================
 * 
 * 功能：执行 Shell 命令
 * 
 * 用途：
 * - 运行系统命令
 * - 执行脚本
 * - 文件操作（通过 shell 命令）
 * - 安装软件包
 * 
 * 安全特性：
 * - 可配置允许/禁止的命令
 * - 可限制在工作目录
 * - 超时保护
 * - 输出大小限制
 */
export class ShellTool extends BaseTool {
  // ==================== 属性 ====================
  
  /** 工具名称 */
  name = 'shell';
  
  /** 工具描述 */
  description = 'Execute shell commands';

  /** 是否限制在工作目录 */
  private restrictToWorkspace: boolean;
  
  /** 允许的命令列表（可选） */
  private allowedCommands?: string[];
  
  /** 禁止的命令列表（可选） */
  private deniedCommands?: string[];

  // ==================== 构造函数 ====================
  
  /**
   * 构造函数
   * @param restrictToWorkspace - 是否限制在工作目录
   * @param allowedCommands - 允许的命令列表
   * @param deniedCommands - 禁止的命令列表
   */
  constructor(
    restrictToWorkspace = false, 
    allowedCommands?: string[], 
    deniedCommands?: string[]
  ) {
    super();
    this.restrictToWorkspace = restrictToWorkspace;
    this.allowedCommands = allowedCommands;
    this.deniedCommands = deniedCommands;
  }

  // ==================== BaseTool 接口实现 ====================
  
  /**
   * 获取工具定义
   * @description 告诉 LLM 这个工具需要什么参数
   */
  getDefinition(): ToolDefinition {
    return {
      type: 'function',
      function: {
        name: this.name,
        description: this.description,
        parameters: {
          type: 'object',
          properties: {
            command: {
              type: 'string',
              description: 'The shell command to execute',
            },
          },
          required: ['command'],
        },
      },
    };
  }

  /**
   * 执行 Shell 命令
   * @param args - 包含 command 属性的对象
   * @returns 执行结果
   * 
   * 执行流程：
   * 1. 验证参数
   * 2. 安全检查（允许/禁止列表）
   * 3. 执行命令
   * 4. 返回结果
   */
  async execute(args: Record<string, unknown>): Promise<ToolResult> {
    // ===== 第1步：获取并验证命令 =====
    const command = args.command as string;

    if (!command) {
      return this.error('Command is required');
    }

    // ===== 第2步：安全检查 - 禁止的命令 =====
    if (this.deniedCommands) {
      for (const denied of this.deniedCommands) {
        // 检查命令是否包含禁止的关键词
        if (command.includes(denied)) {
          return this.error(`Command contains denied keyword: ${denied}`);
        }
      }
    }

    // ===== 第3步：安全检查 - 允许的命令 =====
    if (this.allowedCommands && this.allowedCommands.length > 0) {
      // 检查命令是否以允许的命令开头
      const isAllowed = this.allowedCommands.some((allowed) => 
        command.startsWith(allowed)
      );
      
      if (!isAllowed) {
        return this.error('Command is not in the allowed list');
      }
    }

    // ===== 第4步：执行命令 =====
    try {
      // 设置执行选项
      const options = {
        timeout: 30000,        // 30 秒超时
        maxBuffer: 1024 * 1024, // 1MB 输出限制
        cwd: this.restrictToWorkspace ? process.cwd() : undefined,  // 工作目录
      };

      // 执行命令
      const { stdout, stderr } = await execAsync(command, options);

      // 组合输出
      const output = stdout + (stderr ? `\nSTDERR:\n${stderr}` : '');
      
      // 返回成功结果
      return this.success(output || 'Command executed successfully (no output)');
    } catch (error) {
      // ===== 错误处理 =====
      const err = error as { 
        stdout?: string; 
        stderr?: string; 
        message: string 
      };
      
      // 尝试获取错误输出
      const output = err.stdout || err.stderr || err.message;
      
      return this.error(`Command failed: ${output}`);
    }
  }
}

/**
 * ============================================================
 * 流程图：Shell 命令执行流程
 * ============================================================
 * 
 *              LLM 调用 shell 工具
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ execute({ command: "..." })   │
 *     └────────────┬───────────────────┘
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ 检查 command 参数是否存在      │
 *     └────────────┬───────────────────┘
 *                      │
 *          ┌─────────┴─────────┐
 *          │                   │
 *         存在                 不存在
 *          │                   │
 *          ▼                   ▼
 *   ┌────────────┐    ┌────────────────┐
 *   │ 检查禁止命令 │    │ 返回错误       │
 *   │ deniedCmds │    │ "Command is    │
 *   └─────┬──────┘    │  required"     │
 *         │           └────────────────┘
 *         ▼
 *   ┌────────────────────────────────┐
 *   │ 命令包含禁止关键词？            │
 *   └────────────┬───────────────────┘
 *          ┌─────┴─────┐
 *          │           │
 *         是          否
 *          │           │
 *          ▼           ▼
 *   ┌───────────┐ ┌─────────────────┐
 *   │ 返回错误  │ │ 检查允许命令    │
 *   │ "contains │ │ allowedCommands │
 *   │ denied"   │ └────────┬────────┘
 *   └───────────┘          │
 *                          ▼
 *               ┌─────────────────┐
 *               │ 在允许列表中？  │
 *               └────────┬────────┘
 *                     ┌──┴──┐
 *                     │     │
 *                    是     否
 *                     │     │
 *                     ▼     ▼
 *              ┌──────────┐ ┌────────────┐
 *              │ 执行命令 │ │ 返回错误   │
 *              │ execAsync│ │ "not in    │
 *              └────┬─────┘ │ allowed"   │
 *                   │       └────────────┘
 *                   ▼
 *              ┌──────────┐
 *              │ 成功？   │
 *              └────┬─────┘
 *            ┌──────┴──────┐
 *            │             │
 *           是            否
 *            │             │
 *            ▼             ▼
 *     ┌────────────┐ ┌──────────┐
 *     │ 返回输出   │ │ 返回错误 │
 *     │ success   │ │ "failed" │
 *     └────────────┘ └──────────┘
 * 
 * ============================================================
 * 安全配置示例
 * ============================================================
 * 
 * // 1. 基础配置（允许所有命令）
 * const tool1 = new ShellTool();
 * 
 * // 2. 限制工作目录
 * const tool2 = new ShellTool(true);
 * 
 * // 3. 禁止危险命令
 * const tool3 = new ShellTool(
 *   false,  // 不限制目录
 *   undefined,  // 不限制允许列表
 *   ['rm -rf', 'sudo', 'dd', ':(){:|:&};:']  // 禁止的命令
 * );
 * 
 * // 4. 只允许特定命令
 * const tool4 = new ShellTool(
 *   false,
 *   ['git', 'npm', 'pnpm']  // 只允许这些命令
 * );
 * 
 * // 5. 完整配置
 * const tool5 = new ShellTool(
 *   true,  // 限制工作目录
 *   ['git', 'npm', 'node'],  // 允许的命令
 *   ['rm -rf /', 'sudo', 'dd']  // 禁止的命令
 * );
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建工具实例
 * const shellTool = new ShellTool();
 * 
 * // 2. 执行简单命令
 * const result1 = await shellTool.execute({
 *   command: 'ls -la'
 * });
 * console.log(result1.success);  // true
 * console.log(result1.output);   // 文件列表
 * 
 * // 3. 执行 Node.js 命令
 * const result2 = await shellTool.execute({
 *   command: 'node -v'
 * });
 * 
 * // 4. 执行 Git 命令
 * const result3 = await shellTool.execute({
 *   command: 'git status'
 * });
 * 
 * // 5. 执行失败（命令不存在）
 * const result4 = await shellTool.execute({
 *   command: 'nonexistent-command'
 * });
 * console.log(result4.success);  // false
 * console.log(result4.error);    // "Command failed: ..."
 * 
 * // 6. 获取工具定义
 * const definition = shellTool.getDefinition();
 * // {
 * //   type: 'function',
 * //   function: {
 * //     name: 'shell',
 * //     description: 'Execute shell commands',
 * //     parameters: { ... }
 * //   }
 * // }
 * 
 * ============================================================
 * 限制与安全建议
 * ============================================================
 * 
 * 1. **生产环境建议**：
 *    - 限制工作目录
 *    - 配置允许的命令列表
 *    - 禁止危险命令
 * 
 * 2. **危险命令列表**：
 *    ```javascript
 *    const dangerousCommands = [
 *      'rm -rf',       // 删除文件
 *      'dd',           // 磁盘操作
 *      'mkfs',         // 格式化
 *      '>:',           // Fork 炸弹
 *      'sudo',         // 提权
 *      'chmod 777',    // 权限过大
 *      'wget/curl',    // 下载执行
 *      'chsh',         // 改 Shell
 *    ];
 *    ```
 * 
 * 3. **超时保护**：
 *    - 默认 30 秒超时
 *    - 防止命令无限等待
 * 
 * 4. **输出限制**：
 *    - 默认 1MB 输出限制
 *    - 防止内存溢出
 * 
 * ============================================================
 */