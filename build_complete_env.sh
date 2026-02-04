#!/bin/bash
# SmartTerm Web UI 完整环境构建和部署脚本

echo "==================================================="
echo "    SmartTerm Web UI 完整环境 Docker 构建脚本"
echo "==================================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 复制当前完整项目到新的构建目录
BUILD_DIR="./build-environment"

echo "📦 准备构建环境..."

# 创建构建目录
mkdir -p $BUILD_DIR

# 复制所有项目文件
rsync -av --exclude='build-environment' --exclude='.git' . $BUILD_DIR/

# 使用 Dockerfile.full 作为构建文件
cp Dockerfile.full $BUILD_DIR/Dockerfile

echo "✅ 构建环境准备完成"

echo ""
echo "🏗️  构建完整环境镜像..."
echo ""

# 构建镜像
cd $BUILD_DIR
docker build -t smartterm-webui-complete:latest .

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

echo "✅ 镜像构建完成"
echo "   镜像名称: smartterm-webui-complete:latest"

echo ""
echo "🐳 启动完整环境..."
echo ""

# 启动容器
docker run -d \
  --name smartterm-complete \
  -p 8000:8000 \
  -v smartterm-data:/root/.smart_term \
  smartterm-webui-complete:latest

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查容器状态
CONTAINER_STATUS=$(docker ps --filter "name=smartterm-complete" --format "{{.Status}}" 2>/dev/null)

if [[ $CONTAINER_STATUS == *"Up"* ]]; then
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "🌐 访问地址:"
    echo "   - API 服务: http://localhost:8000"
    echo "   - API 文档: http://localhost:8000/docs"
    echo ""
    echo "💾 数据持久化:"
    echo "   - 配置数据存储在: smartterm-data Docker 卷"
    echo ""
    echo "⚙️  常用命令:"
    echo "   - 查看日志: docker logs -f smartterm-complete"
    echo "   - 停止服务: docker stop smartterm-complete"
    echo "   - 重启服务: docker restart smartterm-complete"
    echo "   - 进入容器: docker exec -it smartterm-complete bash"
    echo ""
else
    echo "❌ 容器启动失败"
    echo "查看日志: docker logs smartterm-complete"
    exit 1
fi

echo "==================================================="
echo "SmartTerm Web UI 完整环境已准备就绪！"
echo "==================================================="