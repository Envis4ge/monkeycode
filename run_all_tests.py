#!/usr/bin/env python3
"""
完整测试运行脚本
自动管理 Telnet 测试服务器的启动和停止
"""

import sys
import os
import subprocess
import time
import signal
import atexit

sys.path.insert(0, os.path.dirname(__file__))

# 存储后台进程
background_processes = []


def cleanup():
    """清理后台进程"""
    for proc in background_processes:
        if proc.poll() is None:
            print(f"停止进程: {proc.args[0]}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


atexit.register(cleanup)


def start_telnet_server():
    """启动 Telnet 测试服务器"""
    print("=" * 60)
    print("启动 Telnet 测试服务器")
    print("=" * 60)

    # 检查是否已经在运行
    result = subprocess.run(
        ["pgrep", "-f", "telnet_server.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ Telnet 测试服务器已在运行")
        return None

    print("启动 Telnet 测试服务器...")
    proc = subprocess.Popen(
        ["python3", "telnet_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    background_processes.append(proc)

    # 等待服务器启动
    for i in range(10):
        time.sleep(0.5)
        # 使用 ss 命令检查端口（如果没有 ss 则跳过检查）
        try:
            result = subprocess.run(
                ["ss", "-tuln"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if "2323" in result.stdout:
                print("✓ Telnet 测试服务器启动成功 (监听 127.0.0.1:2323)")
                return proc
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    print("✓ Telnet 测试服务器启动成功")
    return proc


def run_pytest(tests="tests/"):
    """运行 pytest 测试"""
    print("\n" + "=" * 60)
    print("运行 Pytest 测试")
    print("=" * 60)
    print()

    cmd = ["python3", "-m", "pytest", "-v"]
    if tests:
        cmd.append(tests)

    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    """主函数"""

    # 1. 启动 Telnet 测试服务器
    telnet_proc = start_telnet_server()

    try:
        # 2. 运行测试
        success = run_pytest()

        # 3. 输出结果
        print("\n" + "=" * 60)
        if success:
            print("✅ 所有测试通过！")
        else:
            print("❌ 部分测试失败")
        print("=" * 60)

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n测试被中断")
        return 1
    finally:
        # 清理
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
