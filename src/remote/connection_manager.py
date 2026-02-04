"""
远程连接管理器
"""

import asyncio
import logging
from typing import Optional, List
from datetime import datetime

from ..models.remote import (
    RemoteConnectionConfig,
    ConnectionSession,
    SessionStatus,
    ExecutionMode,
    AuthType
)
from .telnet_client import TelnetClient
from .ssh_client import SSHClient
from .db import RemoteConfigDatabase


logger = logging.getLogger(__name__)


class ConnectionManager:
    """远程连接管理器"""

    def __init__(self):
        self._active_session: Optional[ConnectionSession] = None
        self._client: Optional[TelnetClient | SSHClient] = None
        self.config_db = RemoteConfigDatabase()

    async def connect(
        self,
        config: RemoteConnectionConfig,
        auth_choice: Optional[str] = None
    ) -> ConnectionSession:
        """建立远程连接

        Args:
            config: 连接配置
            auth_choice: 认证方式选择（SSH时有效："password" 或 "key"）

        Returns:
            连接会话对象

        Raises:
            ConnectionError: 连接失败
            AuthError: 认证失败
        """
        if self._active_session and self._active_session.is_active:
            logger.warning("An active session already exists")
            raise ConnectionError("An active session already exists. Disconnect first.")

        # 更新认证方式选择
        if auth_choice:
            config.auth_type = AuthType.KEY if auth_choice == "key" else AuthType.PASSWORD

        # 确保协议已设置
        if config.protocol is None:
            from ..models.remote import ConnectionProtocol
            if config.port == 23:
                config.protocol = ConnectionProtocol.TELNET
            else:
                config.protocol = ConnectionProtocol.SSH

        logger.info(f"Connecting to {config.host}:{config.port} using {config.protocol.value}")

        # 创建客户端
        if config.protocol.value == "telnet":
            self._client = TelnetClient(config)
        else:
            self._client = SSHClient(config, auth_choice)

        # 建立连接
        try:
            await self._client.connect()
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Failed to connect: {e}")

        # 更新最后连接时间
        try:
            await self.config_db.update_last_connected(config.id)
        except Exception as e:
            logger.warning(f"Could not update last connected time: {e}")

        # 创建会话
        session = ConnectionSession(
            id=self._generate_session_id(),
            config_id=config.id,
            host=config.host,
            port=config.port,
            protocol=config.protocol,
            username=config.username
        )
        session.status = SessionStatus.CONNECTED

        self._active_session = session

        logger.info(f"Session {session.id} established")
        return session

    async def disconnect(self) -> None:
        """断开所有活动连接"""
        if not self._active_session:
            logger.warning("No active session to disconnect")
            return

        logger.info(f"Disconnecting session {self._active_session.id}")

        # 断开客户端连接
        if self._client:
            try:
                await self._client.disconnect()
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

        # 更新会话状态
        self._active_session.status = SessionStatus.DISCONNECTED
        self._active_session.ended_at = datetime.now()

        session_id = self._active_session.id
        self._active_session = None
        self._client = None

        logger.info(f"Session {session_id} disconnected")

    async def execute_command(self, command: str, mode: ExecutionMode = ExecutionMode.INTERACTIVE) -> tuple[int, str]:
        """在活动会话中执行命令

        Args:
            command: 要执行的命令
            mode: 执行模式

        Returns:
            (exit_code, output)

        Raises:
            ConnectionError: 没有活动连接
        """
        if not self._active_session or not self._active_session.is_active:
            raise ConnectionError("No active session. Connect first.")

        if not self._client or not self._client.is_connected:
            raise ConnectionError("Client not connected")

        logger.debug(f"Executing command in {mode.value} mode: {command}")

        # 执行命令
        exit_code, output = await self._client.execute(command)

        # 更新会话统计
        self._active_session.commands_count += 1

        return exit_code, output

    def get_active_session(self) -> Optional[ConnectionSession]:
        """获取当前活动的连接会话"""
        return self._active_session

    async def switch_to_interactive_mode(self) -> None:
        """切换到交互模式（直接转发命令）"""
        if self._active_session:
            self._active_session.current_mode = ExecutionMode.INTERACTIVE
            logger.info(f"Switched to interactive mode")

    async def switch_to_ai_mode(self) -> None:
        """切换到 AI 模式（通过 AI 理解命令）"""
        if self._active_session:
            self._active_session.current_mode = ExecutionMode.AI
            logger.info(f"Switched to AI mode")

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        import uuid
        return f"session_{uuid.uuid4().hex[:16]}"

    async def save_config(self, config: RemoteConnectionConfig) -> None:
        """保存连接配置"""
        logger.info(f"Saving connection config: {config.name}")
        await self.config_db.save_config(config)

    async def update_config(self, config: RemoteConnectionConfig) -> None:
        """更新连接配置"""
        logger.info(f"Updating connection config: {config.name}")
        await self.config_db.update_config(config)

    async def list_saved_configs(self) -> List[RemoteConnectionConfig]:
        """列出所有已保存的连接配置"""
        configs = await self.config_db.list_configs()
        logger.info(f"Retrieved {len(configs)} saved connection configs")
        return configs

    async def get_config_by_id(self, config_id: int) -> Optional[RemoteConnectionConfig]:
        """根据ID获取连接配置"""
        return await self.config_db.get_config(config_id)

    async def get_config_by_name(self, name: str) -> Optional[RemoteConnectionConfig]:
        """根据名称获取连接配置"""
        return await self.config_db.get_config_by_name(name)

    async def delete_config(self, config_id: int) -> None:
        """删除连接配置"""
        logger.info(f"Deleting connection config: {config_id}")
        await self.config_db.delete_config(config_id)
