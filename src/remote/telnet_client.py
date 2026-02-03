"""
Telnet 客户端实现
"""

import asyncio
import logging
from typing import Optional

from ..models.remote import RemoteConnectionConfig, ConnectionSession, SessionStatus, ExecutionMode


logger = logging.getLogger(__name__)


class TelnetClient:
    """Telnet 客户端"""

    def __init__(self, config: RemoteConnectionConfig):
        self.config = config
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._connected = False

    async def connect(self) -> None:
        """建立 Telnet 连接"""
        logger.info(f"Connecting to {self.config.host}:{self.config.port} via Telnet")

        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.config.host, self.config.port),
                timeout=10.0
            )
            self._connected = True

            # 读取欢迎消息
            await asyncio.wait_for(self._read_welcome(), timeout=5.0)

            logger.info(f"Connected to {self.config.host}:{self.config.port}")
        except asyncio.TimeoutError:
            raise ConnectionError(f"Connection to {self.config.host}:{self.config.port} timed out")
        except Exception as e:
            logger.error(f"Failed to connect to {self.config.host}:{self.config.port}: {e}")
            raise ConnectionError(f"Failed to connect: {e}")

    async def _read_welcome(self) -> str:
        """读取欢迎消息"""
        welcome = await asyncio.wait_for(self.reader.read(1024), timeout=5.0)
        return welcome.decode(errors='ignore')

    async def execute(self, command: str) -> tuple[int, str]:
        """执行命令并返回结果

        Args:
            command: 要执行的命令

        Returns:
            (exit_code, output)
        """
        if not self._connected:
            raise ConnectionError("Not connected to remote host")

        logger.debug(f"Executing command: {command}")

        # 发送命令
        self.writer.write(command.encode() + b'\n')
        await self.writer.drain()

        # 读取响应
        try:
            output = await asyncio.wait_for(self.reader.read(8192), timeout=10.0)
            output_str = output.decode(errors='ignore')
            return 0, output_str
        except asyncio.TimeoutError:
            logger.warning(f"Command timeout: {command}")
            return 1, ""
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return 1, str(e)

    async def disconnect(self) -> None:
        """断开连接"""
        logger.info(f"Disconnecting from {self.config.host}:{self.config.port}")

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

        self._connected = False
        self.reader = None
        self.writer = None

        logger.info(f"Disconnected from {self.config.host}:{self.config.port}")

    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
