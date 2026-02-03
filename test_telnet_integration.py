#!/usr/bin/env python3
"""
Telnet 集成测试
测试远程连接管理器的 Telnet 功能
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.remote import RemoteConnectionConfig, AuthType, SessionStatus, ExecutionMode
from src.remote.connection_manager import ConnectionManager


async def test_telnet_connection():
    """测试 Telnet 连接"""

    print("=" * 60)
    print("Telnet 集成测试")
    print("=" * 60 + "\n")

    # 创建连接管理器
    conn_mgr = ConnectionManager()

    # 创建连接配置
    from src.models.remote import ConnectionProtocol
    config = RemoteConnectionConfig(
        id=1,
        name="Test Telnet Server",
        host="127.0.0.1",
        port=2323,
        username="test",
        password="test123",
        protocol=ConnectionProtocol.TELNET
    )

    print(f"配置信息:")
    print(f"  名称: {config.name}")
    print(f"  主机: {config.host}:{config.port}")
    if config.protocol:
        print(f"  协议: {config.protocol.value}")
    else:
        print(f"  协议: unknown")
    print(f"  用户: {config.username}")
    print(f"  认证方式: {config.auth_type.value}")
    print()

    # 测试连接
    try:
        print("正在建立连接...")
        session = await conn_mgr.connect(config)
        print(f"连接成功！会话 ID: {session.id}")
        print(f"  状态: {session.status.value}")
        print(f"  主机: {session.host}:{session.port}")
        print(f"  用户: {session.username}")
        print(f"  模式: {session.current_mode.value}")
        print()

        # 测试命令执行
        print("测试命令执行...")
        test_commands = ["help", "whoami", "pwd", "date", "exit"]

        for cmd in test_commands:
            print(f"\n>>> {cmd}")
            try:
                exit_code, output = await conn_mgr.execute_command(cmd, ExecutionMode.INTERACTIVE)
                print(f"退出码: {exit_code}")
                print(f"输出:\n{output}")

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


async def test_multiple_sessions():
    """测试多会话管理"""

    print("\n\n" + "=" * 60)
    print("多会话测试")
    print("=" * 60 + "\n")

    conn_mgr = ConnectionManager()

    config = RemoteConnectionConfig(
        id=1,
        name="Test Server",
        host="127.0.0.1",
        port=2323,
        username="test"
    )

    try:
        # 第一个会话
        print("创建第一个会话...")
        session1 = await conn_mgr.connect(config)
        print(f"会话 1 已创建: {session1.id}")

        # 尝试创建第二个会话（应该失败）
        print("\n尝试创建第二个会话...")
        try:
            session2 = await conn_mgr.connect(config)
            print(f"错误：应该不允许创建第二个会话")
            return False
        except ConnectionError as e:
            print(f"预期的错误: {e}")

        # 断开第一个会话
        print(f"\n断开会话 {session1.id}...")
        await conn_mgr.disconnect()
        print(f"会话 {session1.id} 已断开")

        # 创建新的会话（应该成功）
        print("\n创建新会话...")
        session3 = await conn_mgr.connect(config)
        print(f"会话 2 已创建: {session3.id}")

        # 断开连接
        await conn_mgr.disconnect()

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n多会话测试通过")
    return True


async def main():
    """主函数"""

    # 确保测试服务器正在运行
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
    success = True

    success &= await test_telnet_connection()
    success &= await test_multiple_sessions()

    if success:
        print("\n所有测试通过!")
        sys.exit(0)
    else:
        print("\n部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
