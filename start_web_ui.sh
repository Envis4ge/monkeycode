#!/bin/bash

echo "Starting SmartTerm Web UI..."

# 启动后端服务
echo "Starting backend service..."
cd /workspace
uvicorn web_app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 启动前端开发服务器
echo "Starting frontend development server..."
cd /workspace/frontend
npm start &
FRONTEND_PID=$!

# 创建清理函数
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

# 等待后台进程
wait $BACKEND_PID $FRONTEND_PID