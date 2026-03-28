# ZXA10 C680&C600&C650&C620 命令参考手册 - 知识库

> 中兴光接入局端汇聚设备命令行知识库 | 版本 V1.2.1 | 5211条命令

---

## 📖 项目简介

本知识库基于 ZXA10 C680/C600/C650/C620 光接入局端汇聚设备的官方命令参考手册（V1.2.1）构建。

### 设备型号
- ZXA10 C680
- ZXA10 C600
- ZXA10 C650
- ZXA10 C620

### 数据统计
| 指标 | 数值 |
|------|------|
| 总命令数 | 5211 条 |
| 章节数 | 13 个 |
| 场景覆盖 | 23 个 |
| 数据总量 | ~13 MB |

---

## 📁 目录结构

```
knowledge_base/
├── README.md                      ← 本文件
├── CATALOG.md                     ← 知识库目录
├── devices/                       ← 设备知识库
│   └── ZXA10_OLT/               ← 中兴OLT设备
│       ├── README.md             ← 设备说明
│       ├── AI_SYSTEM_PROMPT.md   ← AI查询指南
│       ├── docs/                 ← 文档
│       ├── indexes/              ← 索引
│       ├── chapters/             ← 章节
│       └── commands/             ← JSON数据
├── docs/                          ← 通用文档
└── tools/                         ← 工具脚本
    ├── cache_manager.py          ← 缓存管理
    ├── kb_ai_assistant.py       ← AI助手
    └── kb_agent.py              ← Agent集成
```

---

## 🚀 快速开始

### Python调用

```python
from tools.kb_agent import KnowledgeBaseAgent

agent = KnowledgeBaseAgent()
result = agent.ask("如何配置BGP？")

print(result["answer"])
print(result["source"])
```

### 查询方式

| 方式 | 说明 |
|------|------|
| query() | 自然语言查询 |
| query_by_scenario() | 场景查询 |
| query_by_keyword() | 关键字查询 |
| query_command() | 命令详情查询 |

---

## 📅 版本信息

| 项目 | 内容 |
|------|------|
| 源文档版本 | V1.2.1 |
| 出版日期 | 2020-08-31 |
| 设备厂商 | 中兴通讯 |
| 知识库版本 | 1.0 |
| 构建日期 | 2026-03-28 |

---

*本知识库由 AI 自动构建*
