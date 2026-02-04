"""
SSH 客户端实现
"""

import asyncio
import logging
import paramiko
import io
from typing import Optional

from ..models.remote import RemoteConnectionConfig


logger = logging.getLogger(__name__)


class SSHClient:
    """SSH 客户端实现"""

    def __init__(self, config: RemoteConnectionConfig, auth_choice: Optional[str] = None):
        self.config = config
        self.auth_choice = auth_choice
        self._connected = False
        self.client = None

    async def connect(self) -> None:
        """建立 SSH 连接"""
        logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH")

        try:
            self.client = paramiko.SSHClient()
            # 自动添加未知主机密钥
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 根据认证类型选择认证方式
            if self.config.auth_type == "key" or (self.auth_choice and self.auth_choice == "key"):
                if self.config.key_path:
                    # 使用密钥文件认证
                    self.client.connect(
                        hostname=self.config.host,
                        port=self.config.port,
                        username=self.config.username,
                        key_filename=self.config.key_path,
                        timeout=10
                    )
                else:
                    # 使用密钥内容认证（如果密码字段包含密钥内容）
                    if self.config.password:
                        # 尝试将密码作为私钥内容解析
                        try:
                            key = paramiko.RSAKey.from_private_key(io.StringIO(self.config.password))
                        except paramiko.PasswordRequiredException:
                            # 如果私钥受密码保护，使用其内容作为密码
                            key = paramiko.RSAKey.from_private_key(io.StringIO(self.config.password), password=self.config.password)

                        self.client.connect(
                            hostname=self.config.host,
                            port=self.config.port,
                            username=self.config.username,
                            pkey=key,
                            timeout=10
                        )
                    else:
                        raise ConnectionError("No SSH key provided for key-based authentication")
            else:
                # 使用密码认证
                self.client.connect(
                    hostname=self.config.host,
                    port=self.config.port,
                    username=self.config.username,
                    password=self.config.password,
                    timeout=10
                )

            self._connected = True
            logger.info(f"SSH connection to {self.config.host}:{self.config.port} established")
        except paramiko.AuthenticationException:
            logger.error("SSH Authentication failed")
            raise ConnectionError("SSH Authentication failed")
        except paramiko.SSHException as e:
            logger.error(f"SSH connection error: {e}")
            raise ConnectionError(f"SSH connection error: {e}")
        except Exception as e:
            logger.error(f"Failed to connect via SSH: {e}")
            raise ConnectionError(f"Failed to connect via SSH: {e}")

    async def execute(self, command: str) -> tuple[int, str]:
        """执行命令并返回结果

        Args:
            command: 要执行的命令

        Returns:
            (exit_code, output)
        """
        if not self._connected or self.client is None:
            raise ConnectionError("Not connected to remote host")

        logger.debug(f"Executing SSH command: {command}")

        try:
            # 执行命令
            stdin, stdout, stderr = self.client.exec_command(command)

            # 获取输出
            output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')

            # 获取退出码
            exit_code = stdout.channel.recv_exit_status()

            # 合并标准输出和错误输出
            if error_output:
                output += error_output

            return exit_code, output
        except Exception as e:
            logger.error(f"Error executing command via SSH: {e}")
            raise ConnectionError(f"Error executing command: {e}")

    async def disconnect(self) -> None:
        """断开连接"""
        logger.info(f"Disconnecting SSH from {self.config.host}:{self.config.port}")

        if self.client:
            try:
                self.client.close()
                self._connected = False
                logger.info(f"SSH disconnected from {self.config.host}:{self.config.port}")
            except Exception as e:
                logger.error(f"Error during SSH disconnect: {e}")
                raise ConnectionError(f"Error during disconnect: {e}")
        else:
            logger.warning("SSH client was not initialized")

    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
