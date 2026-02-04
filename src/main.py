#!/usr/bin/env python3
"""
smart_term 主程序
智能终端增强工具，提供自然语言命令转换、智能提示和命令解释等功能
"""

import asyncio
import argparse
import sys
import os
from typing import Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.remote import ConnectionManager, SessionManager, CategoryManager
from src.remote.command_history import InteractiveCommandInput
from src.models.remote import RemoteConnectionConfig, AuthType, ConnectionProtocol


class SmartTermCLI:
    """SmartTerm命令行界面"""

    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.session_manager = SessionManager()
        self.category_manager = CategoryManager()
        self.active_session = None

    async def run(self, args):
        """运行CLI"""
        # 初始化默认设备产品类别
        await self.category_manager.initialize_default_categories()

        if args.command == "connect":
            await self.handle_connect(args)
        elif args.command == "list":
            await self.handle_list_configs()
        elif args.command == "add":
            await self.handle_add_config(args)
        elif args.command == "delete":
            await self.handle_delete_config(args)
        elif args.command == "session":
            await self.handle_session_command(args)
        elif args.command == "shell":
            await self.handle_shell_mode()
        else:
            print("未知命令，请使用 --help 查看帮助")

    async def handle_connect(self, args):
        """处理连接命令"""
        print(f"正在连接到 {args.host}:{args.port}...")

        # 尝试获取已保存的配置
        if args.name:
            config = await self.connection_manager.get_config_by_name(args.name)
            if config:
                print(f"使用保存的配置: {config.name}")
            else:
                print(f"未找到名为 '{args.name}' 的配置")
                return
        else:
            # 创建临时配置
            auth_type = AuthType.KEY if args.auth_type == "key" else AuthType.PASSWORD
            protocol = ConnectionProtocol.SSH if args.protocol == "ssh" else ConnectionProtocol.TELNET

            config = RemoteConnectionConfig(
                id=0,
                name=f"temp_{args.host}_{args.port}",
                host=args.host,
                port=args.port,
                auth_type=auth_type,
                username=args.username or "root",
                password=args.password,
                protocol=protocol
            )

        try:
            session = await self.connection_manager.connect(config)
            self.active_session = session
            print(f"✅ 连接成功! 会话ID: {session.id}")
            print(f"   主机: {session.host}:{session.port}")
            print(f"   协议: {session.protocol.value}")
            print(f"   用户: {session.username}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")

    async def handle_list_configs(self):
        """处理列出配置命令"""
        configs = await self.connection_manager.list_saved_configs()

        if not configs:
            print("没有保存的连接配置")
            return

        print(f"找到 {len(configs)} 个连接配置:")
        print("-" * 60)
        for config in configs:
            print(f"名称: {config.name}")
            print(f"主机: {config.host}:{config.port}")
            print(f"协议: {config.protocol.value if config.protocol else 'unknown'}")
            print(f"用户: {config.username}")
            print(f"认证: {config.auth_type.value}")
            if config.last_connected:
                print(f"最后连接: {config.last_connected}")
            print("-" * 60)

    async def handle_add_config(self, args):
        """处理添加配置命令"""
        auth_type = AuthType.KEY if args.auth_type == "key" else AuthType.PASSWORD
        protocol = ConnectionProtocol.SSH if args.protocol == "ssh" else ConnectionProtocol.TELNET

        config = RemoteConnectionConfig(
            id=0,  # 数据库会自动分配ID
            name=args.name,
            host=args.host,
            port=args.port,
            auth_type=auth_type,
            username=args.username,
            password=args.password,
            key_path=args.key_path,
            protocol=protocol
        )

        try:
            await self.connection_manager.save_config(config)
            print(f"✅ 配置 '{config.name}' 已保存")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")

    async def handle_delete_config(self, args):
        """处理删除配置命令"""
        config = await self.connection_manager.get_config_by_name(args.name)
        if not config:
            print(f"❌ 未找到名为 '{args.name}' 的配置")
            return

        try:
            await self.connection_manager.delete_config(config.id)
            print(f"✅ 配置 '{config.name}' 已删除")
        except Exception as e:
            print(f"❌ 删除配置失败: {e}")

    async def handle_session_command(self, args):
        """处理会话相关命令"""
        if args.session_action == "list":
            sessions = await self.session_manager.get_active_sessions()
            if sessions:
                print("活动会话:")
                for session in sessions:
                    print(f"  ID: {session.id}")
                    print(f"  主机: {session.host}:{session.port}")
                    print(f"  状态: {session.status.value}")
                    print(f"  命令数: {session.commands_count}")
                    print("-" * 30)
            else:
                print("当前没有活动会话")

        elif args.session_action == "history":
            if self.active_session:
                history = await self.session_manager.get_session_history(self.active_session.id, limit=20)
                print(f"会话 {self.active_session.id} 的历史命令:")
                for i, cmd in enumerate(history):
                    print(f"  {i+1}. {cmd.command} [退出码: {cmd.exit_code}]")
            else:
                print("当前没有活动会话")

    async def handle_shell_mode(self):
        """处理交互式shell模式"""
        session = self.connection_manager.get_active_session()
        if not session:
            print("❌ 没有活动的连接会话，请先使用 connect 命令连接")
            return

        print(f"进入交互式模式 - {session.host}:{session.port}")
        print("输入 'exit' 或 'quit' 退出会话")
        print("使用方向键 ↑/↓ 可浏览历史命令")
        print("-" * 50)

        # 创建交互式命令输入处理器
        command_input = InteractiveCommandInput()
        command_input.setup_readline()

        try:
            while True:
                try:
                    # 显示提示符并获取用户输入
                    prompt = f"[{session.username}@{session.host}:{session.port}]$ "
                    command = command_input.get_user_input(prompt)

                    if command.lower() in ['exit', 'quit', 'logout']:
                        print("断开连接...")
                        # 保存命令历史
                        command_input.history_manager.save_history()
                        await self.connection_manager.disconnect()
                        break

                    if command.strip() == "":
                        continue

                    # 执行命令
                    import time
                    start_time = time.time()
                    exit_code, output = await self.connection_manager.execute_command(command)
                    duration = time.time() - start_time

                    print(output)
                    print(f"[退出码: {exit_code}, 耗时: {duration:.2f}s]")

                    # 添加到历史记录
                    await self.session_manager.add_command_to_session(
                        session_id=session.id,
                        command=command,
                        mode=self.connection_manager.get_active_session().current_mode,
                        output=output,
                        exit_code=exit_code,
                        duration=duration
                    )

                except KeyboardInterrupt:
                    print("\n使用 'exit' 命令退出会话")
                    continue
                except EOFError:
                    print("\n断开连接...")
                    # 保存命令历史
                    command_input.history_manager.save_history()
                    await self.connection_manager.disconnect()
                    break
        except Exception as e:
            print(f"会话错误: {e}")
            # 保存命令历史
            command_input.history_manager.save_history()
            await self.connection_manager.disconnect()


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(description='SmartTerm - 智能终端增强工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 连接命令
    connect_parser = subparsers.add_parser('connect', help='连接到远程服务器')
    connect_parser.add_argument('--name', '-n', help='连接配置名称')
    connect_parser.add_argument('--host', '--hostname', help='主机地址')
    connect_parser.add_argument('--port', '-p', type=int, default=22, help='端口号')
    connect_parser.add_argument('--username', '-u', help='用户名')
    connect_parser.add_argument('--password', '-P', help='密码')
    connect_parser.add_argument('--auth-type', '-a', choices=['password', 'key'], default='password', help='认证类型')
    connect_parser.add_argument('--protocol', '-t', choices=['ssh', 'telnet'], default='ssh', help='协议类型')

    # 列出配置命令
    list_parser = subparsers.add_parser('list', help='列出所有连接配置')

    # 添加配置命令
    add_parser = subparsers.add_parser('add', help='添加连接配置')
    add_parser.add_argument('--name', '-n', required=True, help='配置名称')
    add_parser.add_argument('--host', '--hostname', required=True, help='主机地址')
    add_parser.add_argument('--port', '-p', type=int, default=22, help='端口号')
    add_parser.add_argument('--username', '-u', required=True, help='用户名')
    add_parser.add_argument('--password', '-P', help='密码')
    add_parser.add_argument('--key-path', '-k', help='密钥路径')
    add_parser.add_argument('--auth-type', '-a', choices=['password', 'key'], default='password', help='认证类型')
    add_parser.add_argument('--protocol', '-t', choices=['ssh', 'telnet'], default='ssh', help='协议类型')

    # 删除配置命令
    delete_parser = subparsers.add_parser('delete', help='删除连接配置')
    delete_parser.add_argument('--name', '-n', required=True, help='配置名称')

    # 会话命令
    session_parser = subparsers.add_parser('session', help='会话管理')
    session_subparsers = session_parser.add_subparsers(dest='session_action', help='会话子命令')
    session_subparsers.add_parser('list', help='列出活动会话')
    session_subparsers.add_parser('history', help='显示会话历史')

    # Shell模式
    shell_parser = subparsers.add_parser('shell', help='进入交互式shell模式')

    return parser


async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = SmartTermCLI()
    await cli.run(args)


if __name__ == "__main__":
    asyncio.run(main())