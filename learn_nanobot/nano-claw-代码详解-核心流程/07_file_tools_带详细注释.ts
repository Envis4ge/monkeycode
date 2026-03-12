/**
 * ============================================================
 * nano-claw 核心代码详解 - File Tools (文件读写工具)
 * ============================================================
 * 
 * 文件工具包括：
 * - ReadFileTool: 读取文件
 * - WriteFileTool: 写入文件
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { dirname } from 'path';
import { BaseTool } from './registry';
import { ToolDefinition, ToolResult } from '../../types';

/**
 * ============================================================
 * 工具1：ReadFileTool (文件读取工具)
 * ============================================================
 * 
 * 功能：读取文件内容
 * 
 * 用途：
 * - 读取代码文件
 * - 读取配置文件
 * - 读取数据文件
 */
export class ReadFileTool extends BaseTool {
  // ==================== 属性 ====================
  
  name = 'read_file';
  description = 'Read contents of a file';

  // ==================== BaseTool 接口实现 ====================
  
  /**
   * 获取工具定义
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
            path: {
              type: 'string',
              description: 'Path to the file to read',
            },
          },
          required: ['path'],
        },
      },
    };
  }

  /**
   * 执行读取
   * @param args - 包含文件路径
   */
  async execute(args: Record<string, unknown>): Promise<ToolResult> {
    const path = args.path as string;
    
    // 参数验证
    if (!path) {
      return this.error('Path is required');
    }

    try {
      // 检查文件是否存在
      if (!existsSync(path)) {
        return this.error(`File not found: ${path}`);
      }

      // 读取文件内容
      const content = readFileSync(path, 'utf-8');
      
      return this.success(content);
    } catch (error) {
      return this.error(`Failed to read file: ${(error as Error).message}`);
    }
  }
}

/**
 * ============================================================
 * 工具2：WriteFileTool (文件写入工具)
 * ============================================================
 * 
 * 功能：写入内容到文件
 * 
 * 用途：
 * - 创建新文件
 * - 修改文件
 * - 生成代码
 * 
 * 特性：
 * - 自动创建目录
 * - 支持覆盖写入
 */
export class WriteFileTool extends BaseTool {
  // ==================== 属性 ====================
  
  name = 'write_file';
  description = 'Write content to a file';

  // ==================== BaseTool 接口实现 ====================
  
  /**
   * 获取工具定义
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
            path: {
              type: 'string',
              description: 'Path to the file to write',
            },
            content: {
              type: 'string',
              description: 'Content to write to the file',
            },
          },
          required: ['path', 'content'],
        },
      },
    };
  }

  /**
   * 执行写入
   * @param args - 包含路径和内容
   */
  async execute(args: Record<string, unknown>): Promise<ToolResult> {
    const path = args.path as string;
    const content = args.content as string;

    // 参数验证
    if (!path) {
      return this.error('Path is required');
    }
    if (content === undefined) {
      return this.error('Content is required');
    }

    try {
      // 获取目录路径
      const dir = dirname(path);
      
      // 如果目录不存在，创建它
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }

      // 写入文件
      writeFileSync(path, content, 'utf-8');
      
      return this.success(`File written successfully: ${path}`);
    } catch (error) {
      return this.error(`Failed to write file: ${(error as Error).message}`);
    }
  }
}

/**
 * ============================================================
 * 流程图：文件读取流程
 * ============================================================
 * 
 *              LLM 调用 read_file
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ execute({ path: "..." })       │
 *     └────────────┬───────────────────┘
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ 检查 path 参数                 │
 *     └────────────┬───────────────────┘
 *                      │
 *          ┌─────────┴─────────┐
 *          │                   │
 *         存在                 不存在
 *          │                   │
 *          ▼                   ▼
 *   ┌────────────┐    ┌────────────────┐
 *   │ existsSync │    │ 返回错误       │
 *   │ (检查文件) │    │ "Path is       │
 *   └─────┬──────┘    │  required"     │
 *         │           └────────────────┘
 *         ▼
 *   ┌────────────┐
 *   │ 文件存在？ │
 *   └─────┬──────┘
 *    ┌────┴────┐
 *    │         │
 *   是        否
 *    │         │
 *    ▼         ▼
 * ┌──────┐ ┌────────────────┐
 * │read  │ │ 返回错误       │
 * │File  │ │ "File not      │
 * │Sync  │ │  found"        │
 * └──┬───┘ └────────────────┘
 *    │
 *    ▼
 * ┌──────────┐
 * │ 返回内容 │
 * │ success  │
 * └──────────┘
 * 
 * ──────────────────────────────────────────────────────────
 * 
 * 流程图：文件写入流程
 * 
 *              LLM 调用 write_file
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ execute({                      │
 *     │   path: "...",                 │
 *     │   content: "..."               │
 *     │ })                             │
 *     └────────────┬───────────────────┘
 *                      │
 *                      ▼
 *     ┌────────────────────────────────┐
 *     │ 检查 path 和 content 参数      │
 *     └────────────┬───────────────────┘
 *                      │
 *          ┌─────────┴─────────┐
 *          │                   │
 *         是                   否
 *          │                   │
 *          ▼                   ▼
 *   ┌────────────┐    ┌────────────────┐
 *   │ dirname()  │    │ 返回错误       │
 *   │ 获取目录   │    │ "参数缺失"     │
 *   └─────┬──────┘    └────────────────┘
 *         │
 *         ▼
 *   ┌────────────┐
 *   │ 目录存在？ │
 *   └─────┬──────┘
 *    ┌────┴────┐
 *    │         │
 *   否        是
 *    │         │
 *    ▼         ▼
 * ┌──────┐ ┌────────────┐
 * │mkdir │ │ writeFile  │
 * │Sync  │ │ (写入文件) │
 * └──┬───┘ └─────┬──────┘
 *    │           │
 *    └─────┬─────┘
 *          │
 *          ▼
 *   ┌────────────┐
 *   │ 返回成功   │
 *   │ "File      │
 *   │ written    │
 *   │ successfully"│
 *   └────────────┘
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建工具实例
 * const readTool = new ReadFileTool();
 * const writeTool = new WriteFileTool();
 * 
 * // 2. 读取文件
 * const readResult = await readTool.execute({
 *   path: '/path/to/file.txt'
 * });
 * 
 * if (readResult.success) {
 *   console.log(readResult.output);  // 文件内容
 * } else {
 *   console.error(readResult.error); // 错误信息
 * }
 * 
 * // 3. 写入文件
 * const writeResult = await writeTool.execute({
 *   path: '/path/to/newfile.txt',
 *   content: 'Hello, World!'
 * });
 * 
 * if (writeResult.success) {
 *   console.log(writeResult.output);  // "File written successfully: ..."
 * }
 * 
 * // 4. 写入多行内容
 * const codeContent = `
 * function hello() {
 *   console.log("Hello, World!");
 * }
 * 
 * hello();
 * `;
 * 
 * await writeTool.execute({
 *   path: '/path/to/hello.js',
 *   content: codeContent
 * });
 * 
 * // 5. 自动创建目录
 * // 写入 /new/dir/file.txt 时，
 * // 会自动创建 /new/dir 目录
 * await writeTool.execute({
 *   path: '/new/dir/file.txt',
 *   content: 'content'
 * });
 * 
 * ============================================================
 * 注意事项
 * ============================================================
 * 
 * 1. **路径处理**：
 *    - 使用绝对路径更安全
 *    - 注意路径分隔符（Windows 用 \，Linux 用 /）
 * 
 * 2. **文件编码**：
 *    - 默认使用 UTF-8 编码
 *    - 如需其他编码请自行修改
 * 
 * 3. **安全问题**：
 *    - 生产环境应限制写入目录
 *    - 避免覆盖重要系统文件
 *    - 建议添加路径白名单
 * 
 * 4. **目录自动创建**：
 *    - WriteFileTool 会自动创建父目录
 *    - 使用 recursive: true 选项
 * 
 * ============================================================
 */