#!/usr/bin/env python3
"""
简化版 Telnet 客户端测试脚本
用于测试 telnet 连接功能
"""

import asyncio


async def telnet_client(host='127.0.0.1', port=2323):
    """Telnet 客户端"""
    print(f"Connecting to {host}:{port}...")

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        print("Connection timeout!")
        return
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("Connected!\n")

    try:
        # 读取欢迎消息
        welcome = await asyncio.wait_for(reader.read(1024), timeout=5.0)
        print(welcome.decode(errors='ignore'), end='')

        # 发送测试命令
        commands = ['whoami', 'pwd', 'date', 'exit']

        for cmd in commands:
            print(f">>> {cmd}")
            writer.write(cmd.encode() + b'\n')
            await writer.drain()

            # 读取响应
            response = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            print(response.decode(errors='ignore'), end='')

            if cmd.lower() == 'exit':
                break

    except asyncio.TimeoutError:
        print("\nTimeout waiting for response")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nClosing connection...")
        writer.close()
        await writer.wait_closed()


async def main():
    """主函数"""
    print("=" * 50)
    print("Telnet Client Test")
    print("=" * 50 + "\n")

    await telnet_client()

    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)


if __name__ == '__main__':
    asyncio.run(main())
