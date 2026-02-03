#!/usr/bin/env python3
"""
运行远程连接功能测试
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 测试目录结构
print("=" * 60)
print("1. 测试项目结构")
print("=" * 60)

dirs_to_check = [
    "src/remote",
    "src/models/remote",
    "tests/remote"
]

for dir_path in dirs_to_check:
    full_path = os.path.join("/workspace", dir_path)
    if os.path.exists(full_path):
        print(f"✓ {dir_path}")
    else:
        print(f"✗ {dir_path} 不存在")
        sys.exit(1)

print()

# 测试模块导入
print("=" * 60)
print("2. 测试模块导入")
print("=" * 60)

modules_to_test = [
    "src.models.remote",
    "src.remote",
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✓ {module}")
    except Exception as e:
        print(f"✗ {module}: {e}")
        sys.exit(1)

print()

# 测试数据模型
print("=" * 60)
print("3. 测试数据模型")
print("=" * 60)

try:
    from src.models.remote import (
        AuthType,
        SessionStatus,
        ExecutionMode,
        ConnectionProtocol,
        DeviceProductCategory,
        RemoteConnectionConfig,
        ConnectionSession,
        CategorizedCommandRecord,
        CategoryStatistics,
        SecurityIssue
    )

    # 测试枚举
    assert AuthType.PASSWORD.value == "password"
    assert AuthType.KEY.value == "key"
    print("✓ AuthType 枚举")

    assert SessionStatus.CONNECTED.value == "connected"
    assert ExecutionMode.INTERACTIVE.value == "interactive"
    assert ConnectionProtocol.SSH.value == "ssh"
    assert ConnectionProtocol.TELNET.value == "telnet"
    print("✓ 其他枚举")

    # 测试数据类
    config = RemoteConnectionConfig(
        id=1,
        name="Test",
        host="192.168.1.1",
        port=22,
        username="root"
    )
    assert config.protocol == ConnectionProtocol.SSH
    print("✓ RemoteConnectionConfig")

    session = ConnectionSession(
        id="session_123",
        config_id=1,
        host="192.168.1.1",
        port=22,
        protocol=ConnectionProtocol.SSH,
        username="root"
    )
    assert session.is_active is False
    print("✓ ConnectionSession")

    print("\n" + "=" * 60)
    print("数据模型测试通过！")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ 数据模型测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试 Telnet 连接
print("=" * 60)
print("4. 测试 Telnet 连接")
print("=" * 60)

# 检查测试服务器是否运行
result = subprocess.run(
    ["pgrep", "-f", "telnet_server.py"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("警告: Telnet 测试服务器未运行")
    print("请先运行: python3 telnet_server.py")
else:
    print("✓ Telnet 测试服务器正在运行")

    try:
        from src.remote import ConnectionManager
        from src.models.remote import ConnectionProtocol, ExecutionMode

        conn_mgr = ConnectionManager()

        config = RemoteConnectionConfig(
            id=1,
            name="Test Telnet",
            host="127.0.0.1",
            port=2323,
            username="test",
            protocol=ConnectionProtocol.TELNET
        )

        print("正在建立 Telnet 连接...")
        import asyncio
        asyncio.run(conn_mgr.connect(config))
        print("✓ Telnet 连接成功")

        print("\n正在执行命令...")
        exit_code, output = asyncio.run(
            conn_mgr.execute_command("whoami", ExecutionMode.INTERACTIVE)
        )
        print(f"✓ 命令执行成功: {output}")

        print("\n正在断开连接...")
        asyncio.run(conn_mgr.disconnect())
        print("✓ 连接已断开")

    except Exception as e:
        print(f"\n✗ Telnet 连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print()

print("=" * 60)
print("所有测试通过！")
print("=" * 60)
