#!/usr/bin/env python3
"""
简化版 Telnet 测试服务端
用于测试 telnet 连接功能
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def handle_client(reader, writer):
    """处理客户端连接"""
    addr = writer.get_extra_info('peername')
    logger.info(f"Client connected from {addr}")

    try:
        # 发送欢迎消息
        welcome = "\r\n*** Simple Telnet Test Server ***\r\n"
        welcome += "Type 'help' for available commands\r\n"
        welcome += "Commands: help, whoami, pwd, date, exit\r\n"
        welcome += "$ "
        writer.write(welcome.encode())
        await writer.drain()

        while True:
            # 读取客户端输入
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=60.0)
                if not data:
                    logger.info(f"Client {addr} disconnected (EOF)")
                    break

                command = data.strip().decode(errors='ignore')
                logger.info(f"Received command: '{command}'")

                # 处理命令
                response = process_command(command)

                # 发送响应
                output = f"\r\n{response}\r\n$ "
                writer.write(output.encode())
                await writer.drain()

                if command.lower() == 'exit':
                    logger.info(f"Client {addr} requested exit")
                    break

            except asyncio.TimeoutError:
                logger.info(f"Client {addr} timeout")
                break
            except Exception as e:
                logger.error(f"Error handling client {addr}: {e}")
                break

    except Exception as e:
        logger.error(f"Connection error with {addr}: {e}")
    finally:
        logger.info(f"Client {addr} disconnected")
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass


def process_command(command):
    """处理命令"""
    if not command:
        return ""

    cmd = command.lower()
    if cmd == 'help':
        return "Available commands: help, whoami, pwd, date, exit"
    elif cmd == 'whoami':
        return "root"
    elif cmd == 'pwd':
        return "/workspace"
    elif cmd == 'date':
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif cmd == 'exit':
        return "Goodbye!"
    else:
        return f"Unknown command: {command}"


async def start_server(host='127.0.0.1', port=2323):
    """启动服务器"""
    server = await asyncio.start_server(
        handle_client,
        host=host,
        port=port
    )

    addr = server.sockets[0].getsockname()
    logger.info(f"Telnet server listening on {addr[0]}:{addr[1]}")
    return server


async def main():
    """主函数"""
    print("Starting Simple Telnet Test Server...")
    print("Server will listen on 127.0.0.1:2323")
    print("Press Ctrl+C to stop server\n")

    telnet_server = await start_server(host='127.0.0.1', port=2323)

    async with telnet_server:
        await telnet_server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down...")
