"""
SSH 客户端实现
"""

import asyncio
import logging
from typing import Optional

from ..models.remote import RemoteConnectionConfig


logger = logging.getLogger(__name__)


class SSHClient:
    """SSH 客户端（占位符实现，实际需要使用 paramiko）"""

    def __init__(self, config: RemoteConnectionConfig, auth_choice: Optional[str] = None):
        self.config = config
        self.auth_choice = auth_choice
        self._connected = False

    async def connect(self) -> None:
        """建立 SSH 连接"""
        logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH")

        # TODO: 使用 paramiko 实现 SSH 连接
        # 占位符实现
        await asyncio.sleep(0.1)
        self._connected = True
        logger.info(f"SSH connection to {self.config.host}:{self.config.port} established (mock)")

    async def execute(self, command: str) -> tuple[int, str]:
        """执行命令并返回结果

        Args:
            command: 要执行的命令

        Returns:
            (exit_code, output)
        """
        if not self._connected:
            raise ConnectionError("Not connected to remote host")

        logger.debug(f"Executing SSH command: {command}")

        # TODO: 使用 paramiko 执行命令
        # 占位符实现
        await asyncio.sleep(0.05)
        return 0, f"Mock output for: {command}"

    async def disconnect(self) -> None:
        """断开连接"""
        logger.info(f"Disconnecting SSH from {self.config.host}:{self.config.port}")

        # TODO: 使用 paramiko 关闭连接
        # 占位符实现
        self._connected = False
        logger.info(f"SSH disconnected from {self.config.host}:{self.config.port}")

    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
