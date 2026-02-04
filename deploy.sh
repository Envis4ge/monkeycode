#!/bin/bash
# SmartTerm Web UI 一键部署脚本

echo "🚀 SmartTerm Web UI 一键部署"
echo "=============================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose 未安装，尝试使用 docker compose"
    if ! docker compose version &> /dev/null; then
        echo "❌ docker compose 也未安装"
        echo "请安装 docker-compose 或更新 Docker"
        exit 1
    fi
fi

echo "✅ Docker 环境检查通过"

# 创建 Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    openssh-client \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn

# 复制应用代码
COPY . .

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

echo "✅ Dockerfile 创建完成"

# 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  smartterm:
    build: .
    container_name: smartterm-webui
    ports:
      - "8000:8000"
    volumes:
      - smartterm-data:/root/.smart_term
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=info
    restart: unless-stopped

volumes:
  smartterm-data:
EOF

echo "✅ docker-compose.yml 创建完成"

# 构建并启动
echo "🏗️  正在构建并启动 SmartTerm Web UI..."
echo ""

docker-compose up -d

# 等待几秒钟让服务启动
sleep 10

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "🌐 访问地址:"
    echo "   - API 文档: http://localhost:8000/docs"
    echo "   - API 服务: http://localhost:8000"
    echo ""
    echo "📊 服务状态:"
    docker-compose ps
    echo ""
    echo "💡 使用提示:"
    echo "   - 停止服务: docker-compose down"
    echo "   - 查看日志: docker-compose logs -f"
    echo "   - 重新启动: docker-compose up -d"
    echo ""
else
    echo "❌ 部署失败"
    echo "查看日志: docker-compose logs"
    exit 1
fi