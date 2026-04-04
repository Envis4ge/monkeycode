# MEMORY.md — 长期记忆

## 用户工作习惯偏好
1. **任务管理**：希望我将任务和进度记录到文档中，避免遗忘
2. **质量保障**：每个任务完成后需要查错验证，确保信息可靠
3. **进度汇报**：主动告知任务进度，保持透明
4. **自主执行**：不逐节点确认，除非遇到需要决策的问题
5. **文档输出**：偏好将学习资料同步到飞书知识库（wiki_space: my_library）
6. **GitHub 同步**：学习任务的代码和文档需同步到 GitHub `monkeycode` 仓库
   - AI 应用开发代码 → `ai-app-development/`
   - Python 教程代码 → `python-tutorial/`
7. **⚠️ 禁止擅自删除文件**：生成的文档/代码，无论是否已上传飞书，**必须经过用户许可才能删除**。上传成功不代表可以清理本地文件。
8. **配置修改需确认**：修改 openclaw.json 等配置文件前，必须先给用户说明方案（改什么、什么影响），经用户确认后再执行，不能直接修改。

## 已完成的学习任务
- **Python 教程学习（廖雪峰）** — 2026-03-27 启动 ✅ **全部完成**
  - 状态：✅ 已完成全部 14 个阶段（阶段1-14）
  - 任务跟踪文档: https://www.feishu.cn/wiki/LB5LwIR2xixeAsk73oOcJg6Xn2c
  - 产出：**29 篇飞书文档**（全部在 `my_library` 知识库） + **14 个代码文件（871行）**
  - GitHub: https://github.com/Envis4ge/monkeycode/tree/master/python-tutorial
  - 覆盖章节：基础语法 → 函数 → OOP → IO → 网络 → Web → 异步 → 实战
  - 代码已验证：全部测试通过

- **Python 教程文档增强拓展** — 2026-03-28 完成 ✅ **全部增强完成**
  - 增强范围：28 篇内容文档（覆盖 23 章 92 小节）
  - 增强内容：每篇文档增加四大拓展板块：
    - ⚠️ 注意事项（重要细节与边界情况）
    - 🚫 常见错误（初学者易犯错误及解决方案）
    - 💡 实战技巧（生产环境实用技巧）
    - 🔗 进阶用法（超出基础教程的拓展知识）
  - 执行方式：API 批量更新，保持现有文档结构（92小节合并为28篇文档）
  - ⚠️ 质量问题修复（03:29-04:05）：用户发现12篇文档拓展内容不完整或缺失，已全部修复
  - 📌 教训：批量增强后必须逐篇验证完整性
  - 5.1 调用函数 ✅: https://www.feishu.cn/wiki/HATMwQsldiGZv5kTX5pcWbtrnwb
  - 5.2 函数的参数 ✅: https://www.feishu.cn/wiki/XghDw1D1IiX2pvkQoVNcsWkJnXb
  - 5.3 递归函数 ✅: https://www.feishu.cn/wiki/HM0Fwf7ddiybAbkz75fc8MGLnyf
  - 6.1 切片 ✅: https://www.feishu.cn/wiki/L2wPwkDpPibV4ok3i6kcnzbfnCf
  - 6.2 迭代 ✅: https://www.feishu.cn/wiki/IfB5wSgniiSyVVkeUG6cWwCUnhg
  - 6.3 列表生成式 ✅: https://www.feishu.cn/wiki/LYcAw55LFiCGJwkbhu1cC1Dbnhg
  - 6.4 生成器 ✅: https://www.feishu.cn/wiki/QlR5wIPsJiaOZ7kNk7Ac3JyinRh
  - 6.5 迭代器 ✅: https://www.feishu.cn/wiki/J76owjPDuijmspkZGBIcrlzfnWg
  - 7.1-7.3 高阶函数 ✅: https://www.feishu.cn/wiki/BRcgwf2NAiM5ygkDHNwccpsknIe
  - 7.4-7.7 闭包/lambda/装饰器/偏函数 ✅: https://www.feishu.cn/wiki/FsLjw4IzqiUBC2knnLccvMBDntb
  - 8.1-8.2 模块 ✅: https://www.feishu.cn/wiki/OHshw9yAEidszXkgR1lcTBKcn3c

- **AI应用开发学习路线图** — 2026-03-24 启动 ✅ **全部完成**
  - 状态：✅ 已完成（28/28项）
  - 飞书文档：https://www.feishu.cn/wiki/QzV7wnNp0izfiBkhZY6cvkm7njT
  - 任务跟踪：ai-learning-tasks.md
  - 涵盖5个阶段：入门→基础→中级→进阶→高级
  - 产出：20个Python教学文件，5115行代码，7个飞书知识库文档
  - ⚠️ 2026-03-25：本地代码曾被误删，已重新生成并验证通过，代码保留在 `ai-learning/` 目录

## 技术环境
- 飞书已连接，个人知识库可写入
- 当前会话：微信渠道，使用 xiaomi/mimo-v2-pro
- 妙搭云电脑环境，支持Python、Shell等开发操作
