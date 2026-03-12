/**
 * ============================================================
 * nano-claw 核心代码详解 - SkillsLoader (技能加载器)
 * ============================================================
 * 
 * SkillsLoader 负责从磁盘加载技能（Skills），技能是
 * 以 Markdown 文件形式存储的知识和能力扩展。
 * 
 * 作者：nano-claw 学习团队
 * 适合：初学者
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { Skill } from '../types';
import { getSkillsDir } from '../utils/helpers';
import { logger } from '../utils/logger';

/**
 * ============================================================
 * 核心类：SkillsLoader
 * ============================================================
 * 
 * 功能：
 * 1. 扫描 skills 目录
 * 2. 读取 .md 文件
 * 3. 解析为 Skill 对象
 * 4. 提供查询接口
 * 
 * 技能目录：~/.nano-claw/skills/
 */
export class SkillsLoader {
  // ==================== 属性 ====================
  
  /** 技能目录路径 */
  private skillsDir: string;
  
  /** 技能存储 Map */
  private skills: Map<string, Skill> = new Map();

  // ==================== 构造函数 ====================
  
  /**
   * 构造函数
   * @param skillsDir - 技能目录路径（可选，默认从配置获取）
   */
  constructor(skillsDir?: string) {
    // 使用传入路径或获取默认路径
    this.skillsDir = skillsDir || getSkillsDir();
    
    // 初始化时加载所有技能
    this.loadSkills();
  }

  // ==================== 核心方法 ====================

  /**
   * 加载所有技能
   * @description 扫描目录，加载所有 .md 文件
   * 
   * 加载流程：
   * 1. 检查目录是否存在
   * 2. 扫描目录中的 .md 文件
   * 3. 逐个读取解析
   * 4. 存入 Map
   */
  private loadSkills(): void {
    // 检查目录是否存在
    if (!existsSync(this.skillsDir)) {
      logger.debug({ dir: this.skillsDir }, 'Skills directory does not exist');
      return;
    }

    try {
      // 读取目录内容
      const files = readdirSync(this.skillsDir);
      
      // 筛选 .md 文件
      const skillFiles = files.filter((f) => f.endsWith('.md'));

      // 逐个加载
      for (const file of skillFiles) {
        const skillPath = join(this.skillsDir, file);
        const skill = this.loadSkillFile(skillPath);
        
        if (skill) {
          // 存入 Map，key 是技能名
          this.skills.set(skill.name, skill);
        }
      }

      logger.info({ count: this.skills.size }, 'Skills loaded');
    } catch (error) {
      logger.error({ error, dir: this.skillsDir }, 'Failed to load skills');
    }
  }

  /**
   * 加载单个技能文件
   * @description 解析 Markdown 文件，提取技能信息
   * 
   * 解析规则：
   * - 第一个 # 标题 = 技能名称
   * - 第一段描述 = 技能描述
   * - 完整内容 = 技能内容
   * 
   * @param path - 文件路径
   * @returns Skill 对象或 null
   */
  private loadSkillFile(path: string): Skill | null {
    try {
      // 读取文件内容
      const content = readFileSync(path, 'utf-8');

      // ===== 解析 Markdown =====
      const lines = content.split('\n');
      let name = '';           // 技能名称
      let description = '';    // 技能描述
      let inDescription = false;  // 是否在读取描述

      for (const line of lines) {
        // 第一个 # 标题是技能名称
        if (line.startsWith('# ')) {
          name = line.substring(2).trim();
          inDescription = true;
        } 
        // 读取描述（第一段非空文本）
        else if (inDescription && line.trim() && !line.startsWith('#')) {
          description = line.trim();
          break;  // 找到描述后停止
        }
      }

      // 如果没有找到名称，使用文件名
      if (!name) {
        name = path.split('/').pop()?.replace('.md', '') || 'unknown';
      }

      // 如果没有描述，使用默认
      if (!description) {
        description = 'No description available';
      }

      // 返回技能对象
      return {
        name,
        description,
        content,
        path,
      };
    } catch (error) {
      logger.error({ error, path }, 'Failed to load skill file');
      return null;
    }
  }

  // ==================== 查询方法 ====================

  /**
   * 获取所有技能
   * @returns 技能数组
   */
  getSkills(): Skill[] {
    return Array.from(this.skills.values());
  }

  /**
   * 根据名称获取技能
   * @param name - 技能名称
   * @returns 技能对象或 undefined
   */
  getSkill(name: string): Skill | undefined {
    return this.skills.get(name);
  }

  /**
   * 获取技能数量
   * @returns 技能总数
   */
  getSkillCount(): number {
    return this.skills.size;
  }

  // ==================== 管理方法 ====================

  /**
   * 重新加载所有技能
   * @description 用于热重载技能
   */
  reload(): void {
    this.skills.clear();
    this.loadSkills();
  }
}

/**
 * ============================================================
 * 流程图：技能加载流程
 * ============================================================
 * 
 *                    创建 SkillsLoader 实例
 *                               │
 *                               ▼
 *                    ┌────────────────────────┐
 *                    │   构造函数调用         │
 *                    │   loadSkills()         │
 *                    └────────────┬───────────┘
 *                                 │
 *                                 ▼
 *                    ┌────────────────────────┐
 *                    │   检查 skills 目录     │
 *                    │   是否存在？           │
 *                    └────────────┬───────────┘
 *                                 │
 *                    ┌────────────┴────────────┐
 *                    │                         │
 *                   是                         否
 *                    │                         │
 *                    ▼                         ▼
 *            ┌───────────────┐        ┌───────────────┐
 *            │ 读取目录内容  │        │  返回（无技能）│
 *            │ readdirSync  │        └───────────────┘
 *            └───────┬───────┘
 *                    │
 *                    ▼
 *            ┌───────────────────┐
 *            │ 筛选 .md 文件     │
 *            │ files.filter(...) │
 *            └─────────┬─────────┘
 *                      │
 *                      ▼
 *            ┌───────────────────┐
 *            │  遍历每个文件     │
 *            └─────────┬─────────┘
 *                      │
 *          ┌───────────┴───────────┐
 *          │                       │
 *          ▼                       ▼
 *   ┌─────────────┐        ┌─────────────┐
 *   │ loadSkillFile │        │  加载完成   │
 *   │  解析 .md    │        │  返回技能   │
 *   └──────┬──────┘        └─────────────┘
 *          │
 *          ▼
 *   ┌─────────────────────────────────┐
 *   │   解析规则：                     │
 *   │   # 技能名称                     │
 *   │   第一段描述...                  │
 *   │   ## 其他内容...                │
 *   └─────────────────────────────────┘
 *          │
 *          ▼
 *   ┌─────────────┐
 *   │ 存入 Map    │
 *   │ skills.set()│
 *   └──────┬──────┘
 *          │
 *          └──────────► (遍历下一个文件)
 *                      │
 *                      ▼
 *              ┌─────────────┐
 *              │ getSkills() │
 *              │   可用      │
 *              └─────────────┘
 * 
 * ============================================================
 * 技能文件格式
 * ============================================================
 * 
 * 文件位置：~/.nano-claw/skills/github.md
 * 
 * 文件内容示例：
 * ```markdown
 * # GitHub
 * GitHub 操作技能，支持 issues、PR、仓库管理等
 * 
 * ## 功能
 * - 创建 Issue
 * - 创建 Pull Request
 * - 查看仓库信息
 * 
 * ## 使用方法
 * 使用 GitHub 技能需要提供相关参数...
 * ```
 * 
 * 解析结果：
 * ```javascript
 * {
 *   name: 'GitHub',
 *   description: 'GitHub 操作技能，支持 issues、PR、仓库管理等',
 *   content: '完整 Markdown 内容...',
 *   path: '/path/to/github.md'
 * }
 * ```
 * 
 * ============================================================
 * 使用示例
 * ============================================================
 * 
 * // 1. 创建技能加载器
 * const skillsLoader = new SkillsLoader();
 * 
 * // 2. 获取所有技能
 * const skills = skillsLoader.getSkills();
 * console.log(skills.length); // 技能数量
 * 
 * // 3. 遍历技能
 * for (const skill of skills) {
 *   console.log(`${skill.name}: ${skill.description}`);
 * }
 * 
 * // 4. 获取特定技能
 * const github = skillsLoader.getSkill('GitHub');
 * if (github) {
 *   console.log(github.content);  // 完整内容
 * }
 * 
 * // 5. 重新加载（修改技能后）
 * skillsLoader.reload();
 * 
 * // 6. 获取数量
 * console.log(skillsLoader.getSkillCount());
 * 
 * ============================================================
 * 与 AgentLoop 的集成
 * ============================================================
 * 
 * 在 AgentLoop 中：
 * 
 * 1. 创建 SkillsLoader 实例
 *    this.skillsLoader = new SkillsLoader();
 * 
 * 2. 在构建上下文时获取技能
 *    const skills = this.skillsLoader.getSkills();
 * 
 * 3. 将技能信息加入系统提示词
 *    // ContextBuilder.buildSystemPrompt() 中
 *    for (const skill of skills) {
 *      parts.push(`### ${skill.name}`);
 *      parts.push(skill.description);
 *    }
 * 
 * 4. LLM 就能知道有哪些可用技能
 * 
 * ============================================================
 */