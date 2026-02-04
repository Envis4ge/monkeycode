# SmartTerm - 智能终端增强工具

## 项目概述

SmartTerm 是一个功能强大的终端增强工具，提供自然语言命令转换、智能提示、远程连接管理等多种功能。

## 项目结构

```
workspace/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── ai/                # AI模块
│   │   ├── __init__.py
│   │   └── command_converter.py # 自然语言转命令
│   ├── models/            # 数据模型
│   │   └── remote/
│   │       └── __init__.py
│   ├── remote/            # 远程连接模块
│   │   ├── __init__.py
│   │   ├── ssh_client.py     # SSH客户端
│   │   ├── telnet_client.py  # Telnet客户端
│   │   ├── connection_manager.py # 连接管理器
│   │   ├── session_manager.py    # 会话管理器
│   │   ├── category_manager.py   # 设备类别管理器
│   │   ├── command_history.py    # 命令历史功能
│   │   ├── command_history_db.py # 命令历史数据库
│   │   ├── db.py               # 配置数据库
│   │   └── security_manager.py # 安全管理器
│   └── docs/              # 文档目录
│       └── device_categories.md # 设备类别文档
├── README.md             # 项目说明文档
├── demo.py               # 演示脚本
├── requirements.txt      # 依赖列表
└── .gitignore           # Git忽略配置
```

## 功能说明

### 核心功能

1. **远程连接管理**:
   - SSH客户端支持密码认证和密钥认证
   - Telnet客户端支持
   - 连接配置持久化到SQLite数据库
   - 多连接和会话管理

2. **智能交互**:
   - AI模式: 使用自然语言执行命令
   - 交互式Shell模式: 传统命令行交互
   - 命令历史记录和自动补全

3. **设备产品类别管理**:
   - 预定义设备类别（网关、OLT等）
   - 根据设备类型定制命令

4. **安全功能**:
   - 密码加密存储
   - 连接安全检查
   - SSH主机密钥验证

## 使用方法

### 基本命令

```bash
# 查看帮助
python -m src.main --help

# 连接到远程服务器
python -m src.main connect --host 192.168.1.100 --username user

# 保存连接配置
python -m src.main add --name "server" --host 192.168.1.100 --username user

# 进入交互式模式
python -m src.main shell

# 进入AI模式
python -m src.main ai
```

### AI模式示例

在AI模式下，您可以使用自然语言表达意图：

```
[AI@user@server:22]> 我想查看当前目录的文件
🧠 正在分析您的请求: 我想查看当前目录的文件
📋 转换为命令: ls -la
💡 说明: 列出当前目录所有文件（包括隐藏文件）及其详细信息
🔍 置信度: 0.90
✅ 是否执行此命令? [Y/n]: Y
```

## 依赖安装

```bash
pip install -r requirements.txt
```

## 扩展开发

### 添加新设备类别

在 `src/docs/device_categories.md` 中添加新的设备类别支持：

```markdown
## 新设备类型名称

### 常用命令
- `command1` - 描述
- `command2` - 描述
```

### 扩展AI转换器

修改 `src/ai/command_converter.py` 来添加新的自然语言转换规则。

## 安全注意事项

1. SSH密钥认证比密码认证更安全
2. 避免在生产环境中使用Telnet
3. 定期更新密码和密钥
4. 验证SSH主机密钥以防止中间人攻击
```

## 许可证

该项目仅供学习和研究使用。