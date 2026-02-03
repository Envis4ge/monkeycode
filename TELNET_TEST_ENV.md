# Telnet 测试环境搭建说明

## 概述

本文档描述了为 smart_term 项目搭建的 Telnet 测试环境，用于测试远程终端连接功能。

## 环境信息

- **操作系统**: Debian 12 (bookworm)
- **Python 版本**: Python 3.x
- **Telnet 服务端口**: 127.0.0.1:2323 (使用非标准端口避免权限问题)

## 测试服务器

### 文件位置

`/workspace/telnet_server.py`

### 启动服务器

```bash
python3 telnet_server.py
```

### 服务器功能

- 监听地址: 127.0.0.1:2323
- 支持命令:
  - `help` - 显示帮助信息
  - `whoami` - 显示当前用户
  - `pwd` - 显示当前目录
  - `date` - 显示当前日期时间
  - `exit` - 退出连接

### 启动为后台服务

```bash
python3 telnet_server.py > /tmp/telnet_server.log 2>&1 &
```

查看日志:

```bash
cat /tmp/telnet_server.log
```

停止服务:

```bash
pkill -9 -f "python3 telnet_server.py"
```

## 测试客户端

### 文件位置

`/workspace/telnet_client.py`

### 运行测试

```bash
python3 telnet_client.py
```

### 客户端功能

自动执行以下命令:
1. whoami
2. pwd
3. date
4. exit

## 测试结果示例

```
==================================================
Telnet Client Test
==================================================

Connecting to 127.0.0.1:2323...
Connected!

*** Simple Telnet Test Server ***
Type 'help' for available commands
Commands: help, whoami, pwd, date, exit
$ >>> whoami
root
$ >>> pwd
/workspace
$ >>> date
2026-02-03 09:22:19
$ >>> exit
Goodbye!
$
Closing connection...

==================================================
Test Complete
==================================================
```

## 使用标准 Telnet 客户端测试

```bash
telnet 127.0.0.1 2323
```

## 集成到 smart_term

测试环境可以用于验证 smart_term 的以下功能:

1. **Telnet 连接建立** - 连接到 127.0.0.1:2323
2. **命令执行** - 执行测试命令并验证响应
3. **会话管理** - 管理连接会话和超时
4. **模式切换** - 测试交互模式和 AI 模式

## 注意事项

1. 测试服务器仅监听 127.0.0.1，不接受外部连接
2. 端口 2323 用于避免需要 root 权限的标准端口 23
3. 服务器仅用于测试，不包含完整的安全性措施
4. 生产环境中应避免使用 Telnet（明文传输），推荐使用 SSH

## 下一步

测试环境已准备就绪，可以开始实现 smart_term 的 Telnet 连接功能：

1. 实现 ConnectionManager 中的 Telnet 连接功能
2. 集成到命令处理管道
3. 添加用户界面支持
4. 编写单元测试和集成测试
