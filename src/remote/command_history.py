"""
命令历史记录功能模块
提供在交互式Shell中使用方向键浏览历史命令的功能
"""

import asyncio
import os
from typing import List, Optional
from pathlib import Path

# 尝试导入 readline 模块（Windows 可能需要 pyreadline3）
try:
    import readline
except ImportError:
    try:
        import gnureadline as readline
    except ImportError:
        readline = None


class CommandHistory:
    """命令历史记录管理器"""

    # 内存中的历史记录（当 readline 不可用时使用）
    _in_memory_history: List[str] = []

    def __init__(self, max_entries: int = 1000, history_file: str = None):
        """
        初始化命令历史记录

        Args:
            max_entries: 最大历史记录条数
            history_file: 历史记录文件路径
        """
        self.max_entries = max_entries
        if history_file is None:
            # 默认历史记录文件路径
            home_dir = Path.home()
            history_dir = home_dir / ".smart_term"
            history_dir.mkdir(exist_ok=True)
            self.history_file = str(history_dir / "command_history.txt")
        else:
            self.history_file = history_file

        self._load_history_from_file()

    def _load_history_from_file(self):
        """从文件加载历史记录"""
        if readline is not None:
            try:
                if os.path.exists(self.history_file):
                    readline.read_history_file(self.history_file)
                    # 限制历史记录条数
                    readline.set_history_length(self.max_entries)
            except Exception as e:
                print(f"Warning: Could not load command history from {self.history_file}: {e}")
        else:
            # 使用简单的历史记录
            try:
                if os.path.exists(self.history_file):
                    with open(self.history_file, 'r') as f:
                        CommandHistory._in_memory_history = f.read().splitlines()
                        # 限制历史记录条数
                        CommandHistory._in_memory_history = CommandHistory._in_memory_history[-self.max_entries:]
            except Exception as e:
                print(f"Warning: Could not load command history from {self.history_file}: {e}")

    def save_history(self):
        """保存历史记录到文件"""
        if readline is not None:
            try:
                readline.write_history_file(self.history_file)
            except Exception as e:
                print(f"Warning: Could not save command history to {self.history_file}: {e}")
        else:
            # 保存内存中的历史记录
            try:
                with open(self.history_file, 'w') as f:
                    f.write('\n'.join(CommandHistory._in_memory_history))
            except Exception as e:
                print(f"Warning: Could not save command history to {self.history_file}: {e}")

    def add_command(self, command: str):
        """添加命令到历史记录"""
        if command.strip():  # 只添加非空命令
            if readline is not None:
                readline.add_history(command)
            else:
                CommandHistory._in_memory_history.append(command)
                # 限制历史记录条数
                if len(CommandHistory._in_memory_history) > self.max_entries:
                    CommandHistory._in_memory_history = CommandHistory._in_memory_history[-self.max_entries:]

    def get_history(self, limit: int = None) -> List[str]:
        """获取历史命令列表

        Args:
            limit: 限制返回的数量

        Returns:
            命令列表，最新的命令在最后
        """
        if readline is not None:
            history_size = readline.get_current_history_length()
            start_index = max(0, history_size - (limit or history_size))

            history = []
            for i in range(start_index, history_size):
                cmd = readline.get_history_item(i + 1)  # readline索引从1开始
                if cmd:
                    history.append(cmd)

            return history
        else:
            # 返回内存中的历史记录
            if limit:
                return CommandHistory._in_memory_history[-limit:]
            return CommandHistory._in_memory_history[:]

    def clear_history(self):
        """清空历史记录"""
        if readline is not None:
            readline.clear_history()
        else:
            CommandHistory._in_memory_history = []
        self.save_history()


class CommandCompleter:
    """命令补全器"""

    def __init__(self, commands=None):
        """
        初始化命令补全器

        Args:
            commands: 预定义的命令列表
        """
        self.commands = set(commands or [
            'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'ps', 'kill', 'top',
            'df', 'du', 'free', 'whoami', 'date', 'echo', 'mkdir', 'rm',
            'cp', 'mv', 'touch', 'chmod', 'chown', 'tar', 'gzip', 'unzip',
            'wget', 'curl', 'scp', 'ssh', 'ping', 'netstat', 'ifconfig',
            'route', 'nslookup', 'dig', 'traceroute', 'history', 'exit',
            'quit', 'help', 'clear'
        ])

    def add_command(self, command: str):
        """添加命令到补全列表"""
        self.commands.add(command.split()[0])  # 只取命令名，忽略参数

    def complete(self, text, state):
        """
        补全函数，供readline使用

        Args:
            text: 当前输入的文本
            state: 补全状态索引

        Returns:
            匹配的命令，如果没有更多匹配项则返回None
        """
        results = [cmd for cmd in self.commands if cmd.startswith(text)] + [None]
        return results[state]


class InteractiveCommandInput:
    """交互式命令输入处理器"""

    def __init__(self, history_manager: CommandHistory = None, completer: CommandCompleter = None, prompt: str = "$ "):
        """
        初始化交互式命令输入

        Args:
            history_manager: 命令历史记录管理器
            completer: 命令补全器
            prompt: 提示符
        """
        self.history_manager = history_manager or CommandHistory()
        self.completer = completer or CommandCompleter()
        self.prompt = prompt

    def setup_readline(self):
        """设置readline，启用命令补全和历史记录功能"""
        if readline is not None:
            try:
                # 设置补全函数
                readline.set_completer(self.completer.complete)

                # 启用Tab补全
                readline.parse_and_bind("tab: complete")

                # 设置历史记录最大数量
                readline.set_history_length(self.history_manager.max_entries)
            except Exception:
                # 在某些系统上rlcompleter不可用
                pass

    def get_user_input(self, prompt: str = None) -> str:
        """
        获取用户输入的命令

        Args:
            prompt: 自定义提示符

        Returns:
            用户输入的命令字符串
        """
        prompt = prompt or self.prompt

        try:
            # 读取用户输入，自动支持方向键浏览历史命令和Tab补全（如果有 readline）
            command = input(prompt)
            if command.strip() and self.history_manager:
                self.history_manager.add_command(command)
            return command
        except KeyboardInterrupt:
            # 用户按下Ctrl+C
            print("^C")
            return ""
        except EOFError:
            # 用户按下Ctrl+D
            return "exit"

    def get_command_history(self, limit: int = None) -> List[str]:
        """获取历史命令列表"""
        return self.history_manager.get_history(limit)
