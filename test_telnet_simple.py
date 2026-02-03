#!/usr/bin/env python3
"""
简单的 Telnet 集成测试
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.remote import RemoteConnectionConfig, AuthType, SessionStatus, ExecutionMode, ConnectionProtocol
from src.remote.connection_manager import ConnectionManager


async def test_telnet_connection():
    """测试 Telnet 连接"""

    print("=" * 60)
    print("Telnet 连接测试")
    print("=" * 60)

    # 创建连接管理器
    conn_mgr = ConnectionManager()

    # 创建连接配置
    config = RemoteConnectionConfig(
        id=1,
        name="Test Telnet Server",
        host="127.0.0.1",
        port=2323,
        username="test",
        password="test123",
        protocol=ConnectionProtocol.TELNET
    )

    print(f"\n配置信息:")
    print(f"  名称: {config.name}")
    print(f"  主机: {config.host}:{config.port}")
    print(f"  协议: {config.protocol.value}")
    print(f"  用户: {config.username}")

    # 测试连接
    try:
        print("\n正在建立连接...")
        session = await conn_mgr.connect(config)
        print(f"连接成功！会话 ID: {session.id}")
        print(f"  状态: {session.status.value}")
        print(f"  主机: {session.host}:{session.port}")

        # 测试命令执行
        print("\n测试命令执行...")
        test_commands = ["whoami", "pwd", "date", "exit"]

        for cmd in test_commands:
            print(f"\n>>> {cmd}")
            try:
                exit_code, output = await conn_mgr.execute_command(cmd, ExecutionMode.INTERACTIVE)
                print(f"退出码: {exit_code}")
                print(f"输出: {output}")

                if cmd.lower() == "exit":
                    break
            except Exception as e:
                print(f"命令执行失败: {e}")

        # 断开连接
        print("\n正在断开连接...")
        await conn_mgr.disconnect()
        print("连接已断开")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    return True


async def main():
    """主函数"""

    # 检查测试服务器是否运行
    import subprocess
    try:
        result = subprocess.run(
            ["pgrep", "-f", "telnet_server.py"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("警告: Telnet 测试服务器未运行")
            print("请先运行: python3 telnet_server.py")
            sys.exit(1)
    except:
        pass

    # 运行测试
    success = await test_telnet_connection()

    if success:
        print("\n测试通过!")
        sys.exit(0)
    else:
        print("\n测试失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
