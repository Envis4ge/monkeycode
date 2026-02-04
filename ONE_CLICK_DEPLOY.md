# SmartTerm Web UI 一键部署方案

## 快速启动 (推荐方案)

如果您没有 Docker，可以使用这个一键启动脚本：

### 启动服务
```bash
# 方法1: 使用Python脚本 (当前已运行)
python3 start_webui.py

# 方法2: 使用Bash脚本
chmod +x simple_deploy.sh
./simple_deploy.sh
```

### 访问服务
- **API文档**: http://localhost:8000/docs
- **API服务**: http://localhost:8000
- **WebSocket终端**: ws://localhost:8000/ws/terminal

### 停止服务
按 `Ctrl+C` 停止服务

## Docker 部署方案 (如果有Docker)

如果您的系统安装了Docker，可以使用以下命令：

```bash
# 1. 创建Dockerfile和docker-compose.yml (已在workspace目录下创建)
# 2. 构建并启动
docker-compose up -d

# 3. 检查状态
docker-compose ps

# 4. 停止服务
docker-compose down
```

## 服务功能
- **AI命令转换**: 自然语言转命令功能
- **SSH/Telnet连接**: 远程连接功能
- **终端仿真**: 实时终端交互
- **配置管理**: 连接配置持久化

## 文件结构
```
/workspace/
├── web_app.py                 # FastAPI后端应用
├── start_webui.py            # Python一键启动脚本
├── simple_deploy.sh          # Bash一键启动脚本
├── deploy.sh                # Docker部署脚本
├── stop.sh                  # Docker停止脚本
├── src/                     # SmartTerm核心代码
└── frontend/                # React前端代码
```

## 状态检查
当前服务已成功运行，监听端口8000，可通过浏览器访问API文档。

## 故障排除
- 端口8000被占用: 使用 `lsof -i :8000` 查找占用进程并终止
- 依赖安装失败: 确保网络连接正常
- 服务启动失败: 检查系统资源和权限
```

该文档说明了如何使用一键部署方案，无论是有Docker还是无Docker环境都能轻松部署SmartTerm Web UI。