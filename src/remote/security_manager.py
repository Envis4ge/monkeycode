"""
安全管理器
"""

import asyncio
import logging
from typing import List, Optional
from cryptography.fernet import Fernet
import base64

from ..models.remote import RemoteConnectionConfig, SecurityIssue


logger = logging.getLogger(__name__)


class SecurityManager:
    """安全管理器"""

    def __init__(self, encryption_key: Optional[bytes] = None):
        if encryption_key is None:
            encryption_key = self._generate_key()

        self.cipher = Fernet(encryption_key)
        self._known_hosts: dict[str, str] = {}

    def _generate_key(self) -> bytes:
        """生成加密密钥"""
        return Fernet.generate_key()

    async def encrypt_password(self, password: str) -> str:
        """加密密码

        Args:
            password: 明文密码

        Returns:
            加密后的密码
        """
        encrypted = self.cipher.encrypt(password.encode())
        return base64.b64encode(encrypted).decode()

    async def decrypt_password(self, encrypted: str) -> str:
        """解密密码

        Args:
            encrypted: 加密的密码

        Returns:
            明文密码

        Raises:
            DecryptionError: 解密失败
        """
        try:
            decoded = base64.b64decode(encrypted.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt password: {e}")
            raise DecryptionError(f"Failed to decrypt password: {e}")

    async def verify_ssh_host_key(self, host: str, port: int, key: str) -> bool:
        """验证 SSH 主机密钥

        Args:
            host: 主机地址
            port: 端口
            key: 主机密钥

        Returns:
            是否验证通过
        """
        known_key = self._known_hosts.get(f"{host}:{port}")

        if known_key is None:
            # 首次连接，记录密钥
            self._known_hosts[f"{host}:{port}"] = key
            logger.info(f"First connection to {host}:{port}, key recorded")
            return True

        if known_key == key:
            logger.debug(f"SSH host key verified for {host}:{port}")
            return True
        else:
            logger.warning(f"SSH host key mismatch for {host}:{port}")
            return False

    async def check_known_hosts(self, host: str, port: int) -> Optional[str]:
        """检查已知主机

        Args:
            host: 主机地址
            port: 端口

        Returns:
            已知的主机密钥，如果不存在则返回None
        """
        return self._known_hosts.get(f"{host}:{port}")

    async def detect_security_issues(self, config: RemoteConnectionConfig) -> List[SecurityIssue]:
        """检测安全问题

        Args:
            config: 连接配置

        Returns:
            安全问题列表
        """
        issues = []

        # 检测 Telnet 的安全问题
        if config.port == 23 or (config.protocol and config.protocol.value == "telnet"):
            issues.append(SecurityIssue(
                type="telnet_insecure",
                severity="high",
                message="Telnet 协议使用明文传输，不安全",
                suggestion="建议使用 SSH 协议进行加密连接"
            ))

        # 检测密码存储
        if config.password and not self._is_encrypted(config.password):
            issues.append(SecurityIssue(
                type="password_plaintext",
                severity="high",
                message="密码以明文形式存储",
                suggestion="请使用加密存储密码"
            ))

        # 检测弱密码
        if config.password and len(config.password) < 8:
            issues.append(SecurityIssue(
                type="weak_password",
                severity="medium",
                message="密码长度不足 8 位",
                suggestion="建议使用至少 8 位的强密码，最好包含大小写字母、数字和特殊字符"
            ))

        # 检测默认或常见用户名
        common_usernames = ['admin', 'root', 'user', 'guest', 'test']
        if config.username.lower() in common_usernames:
            issues.append(SecurityIssue(
                type="common_username",
                severity="low",
                message=f"使用常见用户名 '{config.username}' 可能增加安全风险",
                suggestion="考虑使用非标准用户名"
            ))

        # 检测常用端口
        common_ports = [22, 23, 80, 443, 3389]
        if config.port in common_ports and config.protocol and config.protocol.value != "ssh":
            issues.append(SecurityIssue(
                type="common_port_unprotected",
                severity="medium",
                message=f"通过非安全协议访问常用端口 {config.port}",
                suggestion="对于敏感服务，建议使用安全协议(如SSH)进行访问"
            ))

        # 检测主机地址
        if config.host in ['localhost', '127.0.0.1', '::1']:
            issues.append(SecurityIssue(
                type="localhost_connection",
                severity="info",
                message="连接到本地主机",
                suggestion="确认此操作是否必要"
            ))

        # 检测认证方式
        if config.auth_type and config.auth_type.value == "password":
            issues.append(SecurityIssue(
                type="password_auth",
                severity="medium",
                message="使用密码认证方式",
                suggestion="建议使用密钥认证方式以提高安全性"
            ))

        return issues

    def _is_encrypted(self, password: str) -> bool:
        """检查密码是否已加密"""
        try:
            decoded = base64.b64decode(password.encode())
            self.cipher.decrypt(decoded)
            return True
        except:
            return False


class DecryptionError(Exception):
    """解密错误"""
    pass
