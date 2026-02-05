"""
远程连接功能集成测试
"""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.remote import ConnectionManager, SecurityManager, CategoryManager
from src.models.remote import RemoteConnectionConfig, ConnectionProtocol, ExecutionMode


class TestConnectionManager:
    """测试连接管理器"""

    @pytest.fixture
    def connection_manager(self):
        """创建连接管理器实例"""
        return ConnectionManager()

    @pytest.mark.asyncio
    async def test_connect_telnet(self, connection_manager):
        """测试 Telnet 连接"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Telnet",
            host="127.0.0.1",
            port=2323,
            protocol=ConnectionProtocol.TELNET,
            username="test"
        )

        session = await connection_manager.connect(config)
        assert session is not None
        assert session.status.value == "connected"
        assert session.is_active is True

        await connection_manager.disconnect()
        assert connection_manager.get_active_session() is None

    @pytest.mark.asyncio
    async def test_execute_commands(self, connection_manager):
        """测试命令执行"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="127.0.0.1",
            port=2323,
            protocol=ConnectionProtocol.TELNET,
            username="test"
        )

        await connection_manager.connect(config)

        exit_code, output = await connection_manager.execute_command("whoami", ExecutionMode.INTERACTIVE)
        assert exit_code == 0
        assert "root" in output

        exit_code, output = await connection_manager.execute_command("pwd", ExecutionMode.INTERACTIVE)
        assert exit_code == 0
        assert "/workspace" in output

        await connection_manager.disconnect()

    @pytest.mark.asyncio
    async def test_session_mode_switch(self, connection_manager):
        """测试会话模式切换"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="127.0.0.1",
            port=2323,
            protocol=ConnectionProtocol.TELNET,
            username="test"
        )

        await connection_manager.connect(config)

        await connection_manager.switch_to_interactive_mode()
        session = connection_manager.get_active_session()
        assert session.current_mode == ExecutionMode.INTERACTIVE

        await connection_manager.switch_to_ai_mode()
        session = connection_manager.get_active_session()
        assert session.current_mode == ExecutionMode.AI

        await connection_manager.disconnect()

    @pytest.mark.asyncio
    async def test_multiple_connections_rejected(self, connection_manager):
        """测试拒绝多个连接"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="127.0.0.1",
            port=2323,
            protocol=ConnectionProtocol.TELNET,
            username="test"
        )

        await connection_manager.connect(config)

        with pytest.raises(ConnectionError):
            await connection_manager.connect(config)

        await connection_manager.disconnect()


class TestCategoryManager:
    """测试类别管理器"""

    @pytest.fixture
    def category_manager(self):
        """创建类别管理器实例"""
        return CategoryManager()

    @pytest.mark.asyncio
    async def test_create_category(self, category_manager):
        """测试创建类别"""
        category_id = await category_manager.create_category("测试类别", "测试用类别")
        assert category_id == 0

        categories = await category_manager.get_all_categories()
        assert len(categories) == 1
        assert categories[0].name == "测试类别"

    @pytest.mark.asyncio
    async def test_initialize_default_categories(self, category_manager):
        """测试初始化默认类别"""
        await category_manager.initialize_default_categories()

        categories = await category_manager.get_all_categories()

        assert len(categories) == 5

        category_names = [c.name for c in categories]
        assert "网关_海思" in category_names
        assert "网关_中兴微" in category_names
        assert "OLT_zxic" in category_names
        assert "Olt_烽火" in category_names
        assert "未分类" in category_names

    @pytest.mark.asyncio
    async def test_get_category_statistics(self, category_manager):
        """测试获取类别统计"""
        await category_manager.initialize_default_categories()
        categories = await category_manager.get_all_categories()

        for category in categories:
            stats = await category_manager.get_category_statistics(category.id)
            assert stats.category_id == category.id
            assert stats.category_name == category.name

    @pytest.mark.asyncio
    async def test_get_all_statistics(self, category_manager):
        """测试获取所有统计"""
        await category_manager.initialize_default_categories()

        all_stats = await category_manager.get_all_statistics()

        assert len(all_stats) > 0
        assert all(stats.total_commands >= 0 for stats in all_stats.values())

    @pytest.mark.asyncio
    async def test_delete_category(self, category_manager):
        """测试删除类别"""
        category_id = await category_manager.create_category("待删除", "将被删除的类别")

        await category_manager.delete_category(category_id)

        categories = await category_manager.get_all_categories()
        category_ids = [c.id for c in categories]
        assert category_id not in category_ids

    @pytest.mark.asyncio
    async def test_update_category(self, category_manager):
        """测试更新类别"""
        category_id = await category_manager.create_category("旧名称", "旧描述")

        await category_manager.update_category(category_id, name="新名称", description="新描述")

        category = await category_manager.get_category_by_id(category_id)
        assert category.name == "新名称"
        assert category.description == "新描述"


class TestSecurityManager:
    """测试安全管理器"""

    @pytest.fixture
    def security_manager(self):
        """创建安全管理器实例"""
        return SecurityManager()

    @pytest.mark.asyncio
    async def test_encrypt_password(self, security_manager):
        """测试密码加密"""
        password = "test_password_123"
        encrypted = await security_manager.encrypt_password(password)

        assert encrypted is not None
        assert encrypted != password
        assert isinstance(encrypted, str)

    @pytest.mark.asyncio
    async def test_decrypt_password(self, security_manager):
        """测试密码解密"""
        password = "test_password_123"
        encrypted = await security_manager.encrypt_password(password)
        decrypted = await security_manager.decrypt_password(encrypted)

        assert decrypted == password

    @pytest.mark.asyncio
    async def test_ssh_host_key_first_connection(self, security_manager):
        """测试首次连接记录密钥"""
        host = "192.168.1.1"
        port = 22
        key = "ssh-rsa AAAAB3NzaC1yc2E..."

        result = await security_manager.verify_ssh_host_key(host, port, key)

        assert result is True

    @pytest.mark.asyncio
    async def test_ssh_host_key_matches(self, security_manager):
        """测试已知主机密钥匹配"""
        host = "192.168.1.1"
        port = 22
        key = "ssh-rsa AAAAB3NzaC1yc2E..."

        await security_manager.verify_ssh_host_key(host, port, key)

        result = await security_manager.verify_ssh_host_key(host, port, key)

        assert result is True

    @pytest.mark.asyncio
    async def test_ssh_host_key_mismatch(self, security_manager):
        """测试已知主机密钥不匹配"""
        host = "192.168.1.1"
        port = 22
        key1 = "ssh-rsa AAAAB3NzaC1yc2E..."
        key2 = "ssh-rsa BBBB3NzaC1yc2F..."

        await security_manager.verify_ssh_host_key(host, port, key1)

        result = await security_manager.verify_ssh_host_key(host, port, key2)

        assert result is False

    @pytest.mark.asyncio
    async def test_detect_telnet_insecure(self, security_manager):
        """测试 Telnet 不安全检测"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Telnet Server",
            host="192.168.1.1",
            port=23,
            protocol=ConnectionProtocol.TELNET
        )

        issues = await security_manager.detect_security_issues(config)

        telnet_issues = [i for i in issues if i.type == "telnet_insecure"]
        assert len(telnet_issues) > 0

    @pytest.mark.asyncio
    async def test_detect_weak_password(self, security_manager):
        """测试弱密码检测"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="192.168.1.1",
            port=22,
            password="123"
        )

        issues = await security_manager.detect_security_issues(config)

        weak_password_issues = [i for i in issues if i.type == "weak_password"]
        assert len(weak_password_issues) > 0

    @pytest.mark.asyncio
    async def test_strong_password(self, security_manager):
        """测试强密码"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="192.168.1.1",
            port=22,
            password="StrongPassword123!"
        )

        issues = await security_manager.detect_security_issues(config)

        weak_password_issues = [i for i in issues if i.type == "weak_password"]
        assert len(weak_password_issues) == 0
