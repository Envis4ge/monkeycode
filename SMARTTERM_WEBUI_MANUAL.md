# SmartTerm Web UI - 智能终端增强工具

## 项目概述

SmartTerm Web UI 是一个功能强大的终端增强工具，提供自然语言命令转换、智能提示、远程连接管理等多种功能。该项目将传统的命令行工具转换为现代化的Web界面，用户可以通过浏览器访问所有功能。

## 🌟 核心功能

### 1. AI驱动的自然语言命令转换
- **智能转换**：将用户的自然语言描述自动转换为相应的系统命令
- **高准确度**：内置AI模型，对常见操作具有高置信度识别
- **设备优化**：根据不同设备类别（如OLT、网关等）提供专门的命令优化

### 2. 远程连接管理
- **SSH客户端**：支持密码和密钥认证方式
- **Telnet客户端**：支持传统Telnet连接
- **连接配置持久化**：通过SQLite数据库保存连接配置
- **多连接管理**：同时管理多个远程连接

### 3. 智能交互
- **Web终端**：基于xterm.js的实时终端仿真
- **AI模式**：用户可以用自然语言描述操作意图
- **命令历史**：支持命令历史记录和方向键浏览
- **智能补全**：提供命令自动补全功能

### 4. 会话管理
- **多会话支持**：同时管理多个远程会话
- **状态跟踪**：实时记录会话连接状态和统计信息
- **命令记录**：详细记录每个会话执行的命令

## 🏗️ 系统架构

### 前端 (React)
- **现代化UI**：基于React和Bootstrap的响应式设计
- **Web终端**：集成xterm.js提供真实的终端体验
- **实时交互**：通过WebSocket实现实时命令执行
- **AI助手界面**：直观的自然语言交互面板

### 后端 (FastAPI)
- **REST API**：提供连接管理、会话管理等功能接口
- **WebSocket服务**：实现双向实时通信
- **组件集成**：与原生SmartTerm核心组件深度集成
- **数据持久化**：SQLite数据库存储连接配置

## 📁 项目结构

```
/workspace/
├── web_app.py                 # FastAPI后端应用
├── Dockerfile                 # Docker容器配置
├── docker-compose.yml         # Docker服务编排
├── start_webui.py            # Python一键启动脚本
├── simple_deploy.sh          # Bash一键启动脚本
├── deploy.sh                 # Docker部署脚本
├── stop.sh                   # Docker停止脚本
├── src/                      # SmartTerm核心代码
│   ├── ai/
│   │   └── command_converter.py  # AI命令转换器
│   ├── models/
│   │   └── remote/
│   │       └── __init__.py       # 数据模型
│   ├── remote/
│   │   ├── connection_manager.py # 连接管理器
│   │   ├── db.py                # 配置数据库
│   │   ├── ssh_client.py        # SSH客户端
│   │   ├── telnet_client.py     # Telnet客户端
│   │   └── ...                  # 其他组件
│   └── main.py                # 主程序入口
├── frontend/                 # React前端应用
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── index.js
│       └── components/
│           ├── Terminal.js
│           ├── AiPanel.js
│           └── ...
└── requirements.txt          # Python依赖
```

## 🚀 部署方式

### 方式一：一键启动 (无Docker环境)
```bash
# Python一键启动
python3 start_webui.py

# Bash一键启动
chmod +x simple_deploy.sh
./simple_deploy.sh
```

### 方式二：Docker部署
```bash
# 构建并启动
docker-compose up -d

# 检查状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🌐 访问地址

### 服务端口
- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **WebSocket终端**: ws://localhost:8000/ws/terminal

### Web界面 (前端单独部署)
- **前端服务**: http://localhost:3000 (需单独启动前端)

## 🛡️ 安全特性

- **密码加密**：连接密码加密存储
- **主机验证**：SSH主机密钥验证
- **安全检查**：自动检测连接配置中的安全问题
- **协议安全**：推荐使用SSH而非Telnet

## 🔧 API 接口

### REST API 端点
- `GET /` - 服务状态检查
- `GET /api/configs` - 获取连接配置
- `POST /api/configs` - 添加连接配置
- `DELETE /api/configs/{id}` - 删除连接配置
- `POST /api/connect` - 连接远程主机
- `POST /api/disconnect` - 断开当前连接
- `POST /api/command` - 执行命令

### WebSocket 端点
- `WS /ws/terminal` - 实时终端连接

## 💡 使用示例

### AI命令转换
```bash
# 请求
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "我想查看当前目录的文件", "mode": "ai"}'

# 响应
{
  "original_request": "我想查看当前目录的文件",
  "converted_command": "ls -la",
  "explanation": "列出当前目录的所有文件和详细信息",
  "confidence": 0.9,
  "exit_code": 0,
  "output": "..."
}
```

### 连接管理
```bash
# 获取所有配置
curl http://localhost:8000/api/configs

# 添加连接配置
curl -X POST http://localhost:8000/api/configs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-server",
    "host": "192.168.1.100",
    "port": 22,
    "username": "user",
    "protocol": "ssh"
  }'
```

## 🚀 开发说明

### 本地开发环境设置
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install

# 启动后端服务
uvicorn web_app:app --host 0.0.0.0 --port 8000

# 启动前端服务
npm start
```

### 测试
```bash
# 功能验证
python3 core_validation.py
```

## 📊 技术栈

- **后端**: Python, FastAPI, WebSocket, SQLite
- **前端**: React, xterm.js, Bootstrap
- **AI组件**: 规则引擎支持自然语言处理
- **远程协议**: SSH, Telnet客户端
- **容器化**: Docker, Docker Compose

## 🎯 应用场景

### 系统管理员
- 通过Web界面管理多台服务器
- 使用自然语言快速执行管理命令
- 保存常用连接配置

### 开发人员
- 远程服务器开发环境访问
- 快速执行开发相关命令
- 会话历史记录便于调试

### 网络工程师
- 使用专业网络设备命令
- 设备类别优化的命令转换
- 批量设备管理

## 🛠️ 维护与扩展

### 数据持久化
- 连接配置存储在SQLite数据库中
- 配置数据保存在 `~/.smart_term/` 目录

### 日志
- 后端日志可通过Docker日志查看
- 错误日志记录详细信息便于调试

### 扩展性
- 前后端分离架构便于独立扩展
- AI命令转换器易于添加新规则
- 模块化设计支持功能扩展

## ⚠️ 注意事项

1. **安全性**: 虽然提供了密码加密功能，但建议使用SSH密钥认证
2. **Telnet警告**: Telnet协议以明文传输数据，生产环境不推荐使用
3. **主机验证**: 使用SSH时确保验证主机密钥以防止中间人攻击
4. **网络隔离**: 在安全的网络环境中使用远程连接功能

## 📄 许可证

该项目仅供学习和研究使用。使用时请遵守相关法律法规和目标系统的使用政策。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目功能和文档。

---
**项目完成日期**: 2026年2月4日
**版本**: 1.0.0
**状态**: ✅ 已完成并验证