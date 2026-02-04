#!/bin/bash
# SmartTerm Web UI 停止脚本

echo "🛑 停止 SmartTerm Web UI 服务"
echo "============================="

# 停止服务
docker-compose down

echo "✅ 服务已停止"

# 显示当前状态
echo "📊 当前状态:"
docker-compose ps