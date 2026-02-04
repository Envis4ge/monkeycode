# SmartTerm Web UI - 完整 Docker 环境

这个完整的Docker环境允许您一键部署整个SmartTerm Web UI应用，包含所有必要的组件和依赖。

## 🚀 快速开始

### 方法1: 使用构建脚本
```bash
# 1. 克隆项目
git clone <your-repo-url>
cd <project-directory>

# 2. 构建并启动完整环境
chmod +x build_complete_env.sh
./build_complete_env.sh
```

### 方法2: 手动构建
```bash
# 1. 构建镜像
docker build -f Dockerfile.full -t smartterm-webui-complete:latest .

# 2. 运行容器
docker run -d \
  --name smartterm-complete \
  -p 8000:8000 \
  -v smartterm-data:/root/.smart_term \
  smartterm-webui-complete:latest
```

### 方法3: 使用Docker Compose
```bash
docker-compose -f docker-compose-full.yml up -d
```

## 🌐 访问服务

服务启动后，您可以通过以下地址访问：

- **API文档**: http://localhost:8000/docs
- **API服务**: http://localhost:8000
- **WebSocket终端**: ws://localhost:8000/ws/terminal

## 📦 镜像内容

完整Docker镜像包含：

- **应用代码**: SmartTerm Web UI完整源代码
- **依赖**: 所有Python依赖 (FastAPI, uvicorn, websockets等)
- **系统工具**: SSH客户端, 网络工具
- **数据库**: SQLite (用于配置持久化)
- **配置**: 预配置的应用设置

## 🗂️ 数据持久化

- **配置数据**: 保存在 `/root/.smart_term` 目录
- **Docker卷**: `smartterm-data` (重启后数据不会丢失)

## 🔧 管理命令

### 查看日志
```bash
docker logs -f smartterm-complete
```

### 进入容器
```bash
docker exec -it smartterm-complete bash
```

### 重启服务
```bash
docker restart smartterm-complete
```

### 停止服务
```bash
docker stop smartterm-complete
```

## ⚙️ 环境变量

- `PYTHONPATH=/app` - 应用路径
- `LOG_LEVEL=info` - 日志级别

## 🧪 验证部署

部署完成后，验证服务是否正常运行：

```bash
curl http://localhost:8000/
```

应该返回JSON响应：
```json
{"message":"SmartTerm Web API","version":"1.0.0"}
```

## 🛠️ 自定义

如需自定义配置：

1. 修改 `Dockerfile.full` 以调整构建配置
2. 修改 `docker-compose-full.yml` 以调整运行参数
3. 在构建前添加自定义配置文件

## 🗑️ 清理

### 删除容器
```bash
docker stop smartterm-complete
docker rm smartterm-complete
```

### 删除镜像
```bash
docker rmi smartterm-webui-complete:latest
```

### 删除数据卷 (警告：这会删除所有配置数据)
```bash
docker volume rm smartterm-data
```

## 📚 了解更多

详细使用说明请参考: [DOCKER_ENVIRONMENT_MANUAL.md](DOCKER_ENVIRONMENT_MANUAL.md)

## ✅ 验证成功

完成以上步骤后，您将拥有一个完整的SmartTerm Web UI环境，具备：
- AI驱动的自然语言命令转换
- SSH/Telnet远程连接管理
- Web终端仿真
- 配置持久化
- 完整的API服务

现在您可以通过Web界面享受智能终端增强工具的全部功能！ 🚀