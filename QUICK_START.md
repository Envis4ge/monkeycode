# SmartTerm Web UI 快速开始

## 一键启动 (无Docker版)

### 环境要求
- Python 3.8+
- pip 包管理器

### 启动步骤
1. **克隆或复制项目文件**
2. **运行启动脚本**:
   ```bash
   python3 start_webui.py
   ```
3. **访问服务**:
   - API 文档: http://localhost:8000/docs
   - API 服务: http://localhost:8000

### 停止服务
按 `Ctrl+C` 停止服务

## 功能使用

### 1. API 访问
- `GET /` - 检查服务状态
- `GET /docs` - API 文档界面
- `GET /api/configs` - 获取连接配置
- `POST /api/connect` - 连接远程主机
- `POST /api/command` - 执行命令
- `WS /ws/terminal` - WebSocket终端连接

### 2. 前端连接
您可以使用任何WebSocket客户端连接到 `ws://localhost:8000/ws/terminal`

### 3. AI功能测试
```bash
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "我想查看当前目录的文件", "mode": "ai"}'
```

## 验证部署

服务启动后，您会看到类似以下输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
SmartTerm Web API started successfully!
```

此时服务已准备好接收请求。

## 常见问题

1. **端口被占用**: 确保端口8000未被其他服务使用
2. **依赖问题**: 确保已安装 fastapi, uvicorn, websockets
3. **权限问题**: 确保有足够的权限运行Python脚本

## 完整启动脚本

`start_webui.py` 脚本将自动:
- 检查端口可用性
- 安装所需依赖
- 启动后端服务
- 提供访问地址信息
- 处理优雅停机