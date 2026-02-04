#!/bin/bash

# SmartTerm Web UI 启动脚本

echo "==========================================="
echo "     SmartTerm Web UI 启动脚本"
echo "==========================================="

# 检查Python依赖
echo "检查后端依赖..."
if ! python3 -c "import fastapi, uvicorn, websockets" &> /dev/null; then
    echo "安装后端依赖..."
    pip3 install fastapi uvicorn websockets --break-system-packages
fi

# 启动后端服务
echo "启动后端服务..."
cd /workspace
uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "后端服务PID: $BACKEND_PID"

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 检查后端是否正常启动
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ 后端服务启动失败!"
    exit 1
fi

echo "✅ 后端服务已启动，访问地址: http://localhost:8000"

# 启动前端服务的提示
echo ""
echo "==========================================="
echo "           启动说明"
echo "==========================================="
echo "后端服务已启动，监听端口: 8000"
echo ""
echo "要启动前端界面，请打开另一个终端窗口并执行:"
echo "  cd /workspace/frontend"
echo "  npm start"
echo ""
echo "前端启动后，访问地址: http://localhost:3000"
echo ""
echo "要停止服务，请按 Ctrl+C"
echo "==========================================="

# 创建清理函数
cleanup() {
    echo ""
    echo "正在关闭服务..."
    kill $BACKEND_PID 2>/dev/null
    echo "服务已关闭"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

# 等待后端进程
wait $BACKEND_PID