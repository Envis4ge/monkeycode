# SmartTerm Web UI 完整环境 Docker 部署

## 概述

这个Docker环境包含了完整的SmartTerm Web UI应用，包括所有依赖、配置和数据持久化。

## 包含内容

- 完整的SmartTerm Web UI源代码
- 所有Python依赖
- FastAPI后端服务
- 配置数据库 (SQLite)
- 数据持久化卷
- 完整的部署脚本

## 快速部署

### 1. 构建完整环境
```bash
# 给予脚本执行权限
chmod +x build_complete_env.sh

# 运行构建脚本
./build_complete_env.sh
```

### 2. 手动部署
```bash
# 构建镜像
docker build -f Dockerfile.full -t smartterm-webui-complete:latest .

# 运行容器
docker run -d \
  --name smartterm-complete \
  -p 8000:8000 \
  -v smartterm-data:/root/.smart_term \
  smartterm-webui-complete:latest
```

### 3. 使用Docker Compose
```bash
# 使用完整版compose文件
docker-compose -f docker-compose-full.yml up -d
```

## 镜像特性

### 端口
- `8000`: API服务和Web界面

### 卷
- `smartterm-data`: 持久化配置和连接数据

### 环境变量
- `PYTHONPATH`: /app
- `LOG_LEVEL`: info

## 访问服务

### Web界面
- **API文档**: http://localhost:8000/docs
- **API服务**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws/terminal

## 管理命令

### 启动
```bash
docker run -d --name smartterm-complete -p 8000:8000 smartterm-webui-complete:latest
```

### 停止
```bash
docker stop smartterm-complete
```

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

## 数据持久化

配置数据存储在 `/root/.smart_term` 目录，并通过 `smartterm-data` Docker卷持久化，确保重启后配置不会丢失。

## 安全考虑

- 所有密码存储在加密的SQLite数据库中
- 连接配置持久化在专用卷中
- 服务运行在非特权容器中

## 自定义配置

如需自定义，可以：

1. 修改Dockerfile.full中的配置
2. 调整docker-compose-full.yml中的参数
3. 在构建前添加自己的配置文件

## 更新镜像

```bash
# 拉取最新代码
git pull origin main

# 重新构建
docker build -f Dockerfile.full -t smartterm-webui-complete:latest .

# 重启服务
docker stop smartterm-complete
docker rm smartterm-complete
docker run -d --name smartterm-complete -p 8000:8000 smartterm-webui-complete:latest
```

## 故障排除

### 检查服务状态
```bash
docker ps | grep smartterm-complete
```

### 查看详细日志
```bash
docker logs smartterm-complete --tail 50
```

### 检查健康状态
```bash
docker inspect --format='{{json .State.Health}}' smartterm-complete
```

### 连接测试
```bash
curl http://localhost:8000/
```

## 卸载

```bash
# 停止并删除容器
docker stop smartterm-complete
docker rm smartterm-complete

# 删除镜像（可选）
docker rmi smartterm-webui-complete:latest

# 删除数据卷（会删除所有配置）
docker volume rm smartterm-data
```

## 版本信息

- **基础镜像**: python:3.11-slim
- **应用版本**: SmartTerm Web UI 1.0
- **API版本**: FastAPI 0.128.0
- **构建时间**: $(date)

这个Docker环境提供了一个完整、独立的SmartTerm Web UI部署方案，无需额外依赖即可运行整个应用。