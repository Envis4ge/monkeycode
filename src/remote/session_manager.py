"""
会话管理器
"""

import asyncio
import logging
from typing import Optional, List
from datetime import datetime

from ..models.remote import ConnectionSession, SessionCommand, SessionStatus, ExecutionMode


logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""

    def __init__(self):
        self._sessions: dict[str, ConnectionSession] = {}
        self._session_commands: dict[str, List[SessionCommand]] = {}
        self._command_counter = 0

    async def create_session(self, connection, config_id: int) -> ConnectionSession:
        """创建新会话

        Args:
            connection: 连接对象
            config_id: 连接配置ID

        Returns:
            会话对象
        """
        session = ConnectionSession(
            id=self._generate_session_id(),
            config_id=config_id,
            host=connection.host,
            port=connection.port,
            protocol=connection.protocol,
            username=connection.username
        )

        session.status = SessionStatus.CONNECTED
        self._sessions[session.id] = session
        self._session_commands[session.id] = []

        logger.info(f"Created session {session.id}")
        return session

    async def get_session(self, session_id: str) -> Optional[ConnectionSession]:
        """获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象，如果不存在则返回None
        """
        return self._sessions.get(session_id)

    async def close_session(self, session_id: str) -> None:
        """关闭会话

        Args:
            session_id: 会话ID
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return

        session.status = SessionStatus.DISCONNECTED
        session.ended_at = datetime.now()

        logger.info(f"Closed session {session_id}")

    async def add_command_to_session(
        self,
        session_id: str,
        command: str,
        mode: ExecutionMode,
        output: Optional[str] = None,
        exit_code: Optional[int] = None
    ) -> None:
        """添加命令到会话历史

        Args:
            session_id: 会话ID
            command: 命令字符串
            mode: 执行模式
            output: 输出结果
            exit_code: 退出码
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return

        session_cmd = SessionCommand(
            id=self._command_counter,
            session_id=session_id,
            command=command,
            mode=mode,
            output=output,
            exit_code=exit_code
        )
        self._command_counter += 1

        self._session_commands[session_id].append(session_cmd)
        session.commands_count += 1

        logger.debug(f"Added command to session {session_id}: {command}")

    async def get_session_history(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[SessionCommand]:
        """获取会话历史

        Args:
            session_id: 会话ID
            limit: 返回数量限制

        Returns:
            会话命令列表
        """
        commands = self._session_commands.get(session_id, [])
        return commands[-limit:] if limit > 0 else commands

    async def get_active_sessions(self) -> List[ConnectionSession]:
        """获取所有活动会话"""
        return [
            session for session in self._sessions.values()
            if session.is_active
        ]

    async def cleanup_inactive_sessions(self, timeout_seconds: int = 3600) -> None:
        """清理非活动会话

        Args:
            timeout_seconds: 超时时间（秒）
        """
        now = datetime.now()
        for session_id, session in list(self._sessions.items()):
            if not session.is_active and session.ended_at:
                elapsed = (now - session.ended_at).total_seconds()
                if elapsed > timeout_seconds:
                    logger.info(f"Cleaning up inactive session {session_id}")
                    del self._sessions[session_id]
                    del self._session_commands[session_id]

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        import uuid
        return f"session_{uuid.uuid4().hex[:16]}"
