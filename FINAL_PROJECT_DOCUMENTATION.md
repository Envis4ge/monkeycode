# SmartTerm - 智能终端增强工具

## 项目概述

SmartTerm 是一个功能强大的终端增强工具，提供自然语言命令转换、智能提示、远程连接管理等多种功能。该项目同时支持直接连接终端交互和通过AI驱动的自然语言交互两种模式。

## 核心功能

### 1. 远程连接管理
- **SSH 客户端**: 支持密码认证和密钥认证
- **Telnet 客户端**: 支持传统Telnet连接
- **连接配置持久化**: 保存连接配置到SQLite数据库
- **多连接管理**: 同时管理多个远程连接
- **安全检查**: 自动检测连接配置的安全问题

### 2. 智能交互
- **AI 模式**: 通过AI理解自然语言执行命令
- **交互式模式**: 传统的命令行交互模式
- **智能补全**: 提供命令自动补全功能
- **命令历史**: 支持方向键浏览历史命令

### 3. 会话管理
- **多会话支持**: 同时管理多个远程会话
- **会话状态追踪**: 记录会话的连接状态和统计信息
- **命令记录**: 详细记录每个会话执行的命令

### 4. 设备产品类别管理
- **预定义类别**: 内置多种设备产品类别（网关、OLT等）
- **自动分类**: 根据连接配置自动标记设备产品类型
- **分类统计**: 提供各类设备的使用统计数据

### 5. 安全功能
- **密码加密**: 支持连接密码的加密存储
- **主机密钥验证**: SSH主机密钥验证
- **安全检查**: 检测连接配置中的安全问题
- **威胁检测**: 识别潜在的安全威胁

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基础命令

```bash
# 查看帮助
python -m src.main --help

# 连接到远程服务器
python -m src.main connect --host 192.168.1.100 --username user --password pass

# 保存连接配置
python -m src.main add --name "production-server" --host 192.168.1.100 --port 22 --username root --password mypassword

# 列出所有配置
python -m src.main list

# 删除配置
python -m src.main delete --name "server-name"
```

### 会话管理

```bash
# 列出活动会话
python -m src.main session list

# 查看会话历史
python -m src.main session history
```

### 交互式Shell

```bash
# 连接到服务器后，进入交互式模式
python -m src.main shell
```

### AI驱动模式

```bash
# 连接到服务器后，进入AI模式
# 在此模式下可以使用自然语言描述您的意图
python -m src.main ai

# 示例对话:
# [AI@user@server:22]> 我想查看当前目录有哪些文件
# 🧠 正在分析您的请求: 我想查看当前目录有哪些文件
# 📋 转换为命令: ls -la
# 💡 说明: 列出当前目录所有文件（包括隐藏文件）及其详细信息
# 🔍 置信度: 0.90
# ✅ 是否执行此命令? [Y/n]: Y
```

## 项目结构

```
src/
├── main.py                 # 主程序入口
├── ai/                     # AI模块
│   ├── __init__.py         # AI模块初始化
│   └── command_converter.py # 自然语言命令转换器
├── models/
│   └── remote/
│       └── __init__.py     # 远程连接数据模型
├── remote/                 # 远程连接模块
│   ├── __init__.py         # 模块初始化
│   ├── ssh_client.py       # SSH客户端实现
│   ├── telnet_client.py    # Telnet客户端实现
│   ├── connection_manager.py # 连接管理器
│   ├── session_manager.py   # 会话管理器
│   ├── category_manager.py  # 分类管理器
│   ├── command_history.py   # 命令历史记录功能
│   ├── command_history_db.py # 命令历史数据库
│   ├── db.py               # 配置数据库
│   └── security_manager.py  # 安全管理器
└── docs/                   # 文档目录
    └── device_categories.md # 设备类别文档
```

## 技术特性

### AI驱动的自然语言处理
- 基于正则表达式的自然语言到命令转换
- 针对不同设备类别的专用命令优化
- 智能置信度评估机制
- 交互式命令确认

### 安全机制
- 密码加密存储
- SSH主机密钥验证
- 连接安全问题检测
- 弱密码和常见安全风险警告

### 可扩展架构
- 模块化设计，易于扩展
- 设备类别管理系统
- 命令历史和审计功能
- 插件系统预留接口

## 扩展开发

### 添加新设备类别
在 `src/docs/device_categories.md` 中添加新的设备类别支持，并扩展 `src/ai/command_converter.py` 中的 `_convert_based_on_category` 方法。

### 扩展AI转换规则
修改 `src/ai/command_converter.py` 来添加新的自然语言转换规则。

## 安全注意事项

1. **密码存储**: 尽管提供了密码加密功能，但仍然建议使用SSH密钥认证
2. **Telnet警告**: Telnet协议以明文传输数据，不推荐在生产环境中使用
3. **主机验证**: 使用SSH时，确保验证主机密钥以防止中间人攻击
4. **网络隔离**: 在安全的网络环境中使用远程连接功能

## 许可证

该项目仅供学习和研究使用。使用时请遵守相关法律法规和目标系统的使用政策。