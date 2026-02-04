#!/bin/bash
# SmartTerm Web UI 一键启动脚本 (适用于没有Docker的环境)

echo "🚀 SmartTerm Web UI 一键启动 (无Docker版)"
echo "========================================="

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查端口占用
if lsof -Pi :8000 -sTCP:LISTEN -t &> /dev/null; then
    echo "⚠️  端口 8000 已被占用"
    echo "请先停止占用该端口的进程"
    exit 1
fi

echo "📦 安装依赖..."
pip3 install fastapi uvicorn websockets --break-system-packages

echo "🏗️  启动 SmartTerm Web UI 后端服务..."
echo ""

# 启动服务
python3 -c "
import subprocess
import sys
import os
import time
import threading

def check_server():
    time.sleep(3)  # 等待服务器启动
    try:
        import urllib.request
        response = urllib.request.urlopen('http://localhost:8000/')
        if response.getcode() == 200:
            print('')
            print('✅ 服务启动成功!')
            print('🌐 访问地址: http://localhost:8000')
            print('📊 API文档: http://localhost:8000/docs')
            print('📝 按 Ctrl+C 停止服务')
    except:
        print('⚠️  服务启动中，请稍等...')

# 启动检查线程
checker = threading.Thread(target=check_server, daemon=True)
checker.start()

# 启动服务器
subprocess.run([sys.executable, '-m', 'uvicorn', 'web_app:app', '--host', '0.0.0.0', '--port', '8000'])
"

echo ""
echo "🎯 SmartTerm Web UI 启动完成!"
echo "🌐 访问地址: http://localhost:8000"
echo "📊 API文档: http://localhost:8000/docs"