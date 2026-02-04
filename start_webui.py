#!/usr/bin/env python3
"""
SmartTerm Web UI 一键启动脚本
"""
import subprocess
import sys
import os
import threading
import time
import signal
import socket
from urllib.request import urlopen

def check_port(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def start_backend():
    """启动后端服务"""
    print("🚀 启动 SmartTerm Web UI 后端服务...")

    if not check_port(8000):
        print("⚠️  端口 8000 已被占用，请先关闭占用该端口的服务")
        return False

    # 安装依赖
    print("📦 安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "websockets"])
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

    # 启动后端
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "web_app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])

        print(f"✅ 后端服务已启动 (PID: {process.pid})")
        print("🌐 API 访问地址: http://localhost:8000")
        print("📊 API 文档: http://localhost:8000/docs")

        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return False

def test_connection():
    """测试连接"""
    time.sleep(3)  # 等待服务启动
    try:
        response = urlopen("http://localhost:8000/")
        if response.getcode() == 200:
            print("✅ 服务连接测试成功!")
            print("🎉 SmartTerm Web UI 启动完成!")
            print("📝 使用 Ctrl+C 停止服务")
        else:
            print("⚠️  服务启动但连接测试失败")
    except Exception:
        print("⚠️  服务可能未完全启动，请稍等片刻")

def main():
    print("🚀 SmartTerm Web UI 一键启动")
    print("=" * 40)

    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        return

    # 测试连接
    test_thread = threading.Thread(target=test_connection)
    test_thread.daemon = True
    test_thread.start()

    try:
        # 等待后端进程
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("✅ 服务已停止")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        if backend_process:
            backend_process.terminate()

if __name__ == "__main__":
    main()