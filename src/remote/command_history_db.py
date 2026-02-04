"""
命令历史记录数据库模块
"""

import sqlite3
import json
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from ..models.remote import SessionCommand, ExecutionMode


logger = logging.getLogger(__name__)


class CommandHistoryDatabase:
    """命令历史记录数据库"""

    def __init__(self, db_path: str = None):
        """初始化数据库
        Args:
            db_path: 数据库文件路径，如果不提供则使用默认路径
        """
        if db_path is None:
            # 创建默认数据库路径
            home_dir = Path.home()
            db_dir = home_dir / ".smart_term"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "command_history.db")

        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建命令历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    command TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mode TEXT NOT NULL,
                    output TEXT,
                    exit_code INTEGER,
                    duration REAL DEFAULT 0.0,
                    remote_host TEXT,
                    remote_port INTEGER,
                    category_id INTEGER
                )
            ''')

            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON command_history(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON command_history(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_remote_host ON command_history(remote_host)')

            conn.commit()

        logger.info(f"Command history database initialized at {self.db_path}")

    async def add_command(self, command_record: SessionCommand, remote_host: str = None, remote_port: int = None) -> int:
        """添加命令记录

        Args:
            command_record: 命令记录对象
            remote_host: 远程主机（可选）
            remote_port: 远程端口（可选）

        Returns:
            记录ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 将枚举转换为字符串
            mode_str = command_record.mode.value if isinstance(command_record.mode, ExecutionMode) else command_record.mode

            cursor.execute('''
                INSERT INTO command_history
                (session_id, command, timestamp, mode, output, exit_code, duration, remote_host, remote_port)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                command_record.session_id, command_record.command, command_record.timestamp.isoformat(),
                mode_str, command_record.output, command_record.exit_code, command_record.duration,
                remote_host, remote_port
            ))

            record_id = cursor.lastrowid
            conn.commit()

            logger.debug(f"Added command to history: {command_record.command} (ID: {record_id})")
            return record_id

    async def get_command(self, record_id: int) -> Optional[SessionCommand]:
        """根据ID获取命令记录

        Args:
            record_id: 记录ID

        Returns:
            命令记录对象，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, session_id, command, timestamp, mode, output, exit_code, duration
                FROM command_history
                WHERE id=?
            ''', (record_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_command(row)
            return None

    async def get_recent_commands(self, limit: int = 50, remote_host: str = None) -> List[SessionCommand]:
        """获取最近的命令记录

        Args:
            limit: 返回数量限制
            remote_host: 远程主机（可选），如果指定则只返回该主机的命令

        Returns:
            命令记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if remote_host:
                cursor.execute('''
                    SELECT id, session_id, command, timestamp, mode, output, exit_code, duration
                    FROM command_history
                    WHERE remote_host=?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (remote_host, limit))
            else:
                cursor.execute('''
                    SELECT id, session_id, command, timestamp, mode, output, exit_code, duration
                    FROM command_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

            commands = []
            for row in cursor.fetchall():
                commands.append(self._row_to_command(row))
            return commands

    async def search_commands(self, query: str, limit: int = 50) -> List[SessionCommand]:
        """搜索命令记录

        Args:
            query: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的命令记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 在命令和输出中搜索
            search_pattern = f"%{query}%"
            cursor.execute('''
                SELECT id, session_id, command, timestamp, mode, output, exit_code, duration
                FROM command_history
                WHERE command LIKE ? OR output LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, limit))

            commands = []
            for row in cursor.fetchall():
                commands.append(self._row_to_command(row))
            return commands

    async def get_commands_by_session(self, session_id: str, limit: int = 100) -> List[SessionCommand]:
        """根据会话ID获取命令记录

        Args:
            session_id: 会话ID
            limit: 返回数量限制

        Returns:
            命令记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, session_id, command, timestamp, mode, output, exit_code, duration
                FROM command_history
                WHERE session_id=?
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (session_id, limit))

            commands = []
            for row in cursor.fetchall():
                commands.append(self._row_to_command(row))
            return commands

    async def delete_old_commands(self, days: int = 30) -> int:
        """删除指定天数前的旧命令记录

        Args:
            days: 保留的天数

        Returns:
            删除的记录数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute('''
                DELETE FROM command_history
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))

            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Deleted {deleted_count} old command records")
            return deleted_count

    def _row_to_command(self, row) -> SessionCommand:
        """将数据库行转换为命令对象

        Args:
            row: 数据库行数据

        Returns:
            SessionCommand对象
        """
        record_id, session_id, command, timestamp_str, mode_str, output, exit_code, duration = row

        # 转换时间字符串为datetime对象
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()

        # 转换字符串为枚举
        try:
            from ..models.remote import ExecutionMode
            mode = ExecutionMode(mode_str) if mode_str else ExecutionMode.INTERACTIVE
        except ValueError:
            mode = ExecutionMode.INTERACTIVE

        command_obj = SessionCommand(
            id=record_id,
            session_id=session_id,
            command=command,
            timestamp=timestamp,
            mode=mode,
            output=output,
            exit_code=exit_code,
            duration=duration or 0.0
        )

        return command_obj