"""
远程连接数据模型测试
"""

from datetime import datetime

from src.models.remote import (
    AuthType,
    SessionStatus,
    ExecutionMode,
    ConnectionProtocol,
    DeviceProductCategory,
    RemoteConnectionConfig,
    ConnectionSession,
    CategorizedCommandRecord,
    SessionCommand,
    CategoryStatistics,
    SecurityIssue
)


class TestAuthType:
    """测试 AuthType 枚举"""

    def test_password_auth_type(self):
        """测试密码认证类型"""
        assert AuthType.PASSWORD.value == "password"

    def test_key_auth_type(self):
        """测试密钥认证类型"""
        assert AuthType.KEY.value == "key"


class TestSessionStatus:
    """测试 SessionStatus 枚举"""

    def test_all_session_statuses(self):
        """测试所有会话状态"""
        assert SessionStatus.CONNECTING.value == "connecting"
        assert SessionStatus.CONNECTED.value == "connected"
        assert SessionStatus.DISCONNECTING.value == "disconnecting"
        assert SessionStatus.DISCONNECTED.value == "disconnected"
        assert SessionStatus.ERROR.value == "error"


class TestExecutionMode:
    """测试 ExecutionMode 枚举"""

    def test_interactive_mode(self):
        """测试交互模式"""
        assert ExecutionMode.INTERACTIVE.value == "interactive"

    def test_ai_mode(self):
        """测试 AI 模式"""
        assert ExecutionMode.AI.value == "ai"


class TestConnectionProtocol:
    """测试 ConnectionProtocol 枚举"""

    def test_ssh_protocol(self):
        """测试 SSH 协议"""
        assert ConnectionProtocol.SSH.value == "ssh"

    def test_telnet_protocol(self):
        """测试 Telnet 协议"""
        assert ConnectionProtocol.TELNET.value == "telnet"


class TestDeviceProductCategory:
    """测试 DeviceProductCategory 数据类"""

    def test_create_category(self):
        """测试创建类别"""
        category = DeviceProductCategory(
            id=1,
            name="网关_海思",
            description="海思芯片的网关设备"
        )

        assert category.id == 1
        assert category.name == "网关_海思"
        assert category.description == "海思芯片的网关设备"
        assert category.commands_count == 0
        assert category.connection_count == 0
        assert isinstance(category.created_at, datetime)

    def test_create_category_with_defaults(self):
        """测试使用默认值创建类别"""
        category = DeviceProductCategory(
            id=1,
            name="OLT_zxic"
        )

        assert category.id == 1
        assert category.name == "OLT_zxic"
        assert category.description is None
        assert category.commands_count == 0


class TestRemoteConnectionConfig:
    """测试 RemoteConnectionConfig 数据类"""

    def test_create_ssh_config(self):
        """测试创建 SSH 连接配置"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="192.168.1.1",
            port=22,
            username="root",
            password="password123"
        )

        assert config.id == 1
        assert config.name == "Test Server"
        assert config.host == "192.168.1.1"
        assert config.port == 22
        assert config.username == "root"
        assert config.password == "password123"
        assert config.protocol == ConnectionProtocol.SSH

    def test_create_telnet_config(self):
        """测试创建 Telnet 连接配置（端口 23）"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Telnet Server",
            host="192.168.1.1",
            port=23,
            username="admin"
        )

        assert config.id == 1
        assert config.host == "192.168.1.1"
        assert config.port == 23
        assert config.protocol == ConnectionProtocol.TELNET

    def test_protocol_inference(self):
        """测试协议自动推断"""
        # 端口 22 应为 SSH
        config_ssh = RemoteConnectionConfig(
            id=1,
            name="SSH Server",
            host="192.168.1.1",
            port=22
        )
        assert config_ssh.protocol == ConnectionProtocol.SSH

        # 端口 23 应为 Telnet
        config_telnet = RemoteConnectionConfig(
            id=2,
            name="Telnet Server",
            host="192.168.1.1",
            port=23
        )
        assert config_telnet.protocol == ConnectionProtocol.TELNET

        # 其他端口应为 SSH
        config_other = RemoteConnectionConfig(
            id=3,
            name="Other Port",
            host="192.168.1.1",
            port=2222
        )
        assert config_other.protocol == ConnectionProtocol.SSH

    def test_explicit_protocol(self):
        """测试显式指定协议"""
        config = RemoteConnectionConfig(
            id=1,
            name="Test Server",
            host="192.168.1.1",
            port=2222,
            protocol=ConnectionProtocol.SSH
        )

        assert config.protocol == ConnectionProtocol.SSH


class TestConnectionSession:
    """测试 ConnectionSession 数据类"""

    def test_create_session(self):
        """测试创建会话"""
        session = ConnectionSession(
            id="session_123",
            config_id=1,
            host="192.168.1.1",
            port=22,
            protocol=ConnectionProtocol.SSH,
            username="root"
        )

        assert session.id == "session_123"
        assert session.config_id == 1
        assert session.host == "192.168.1.1"
        assert session.port == 22
        assert session.protocol == ConnectionProtocol.SSH
        assert session.username == "root"
        assert isinstance(session.started_at, datetime)
        assert session.ended_at is None
        assert session.current_mode == ExecutionMode.INTERACTIVE
        assert session.commands_count == 0

    def test_session_is_active(self):
        """测试会话活动状态"""
        session = ConnectionSession(
            id="session_123",
            config_id=1,
            host="192.168.1.1",
            port=22,
            protocol=ConnectionProtocol.SSH,
            username="root",
            status=SessionStatus.CONNECTED
        )

        assert session.is_active is True

        session.status = SessionStatus.DISCONNECTED
        assert session.is_active is False


class TestCategorizedCommandRecord:
    """测试 CategorizedCommandRecord 数据类"""

    def test_create_command_record(self):
        """测试创建命令记录"""
        record = CategorizedCommandRecord(
            id=1,
            command="ls -la",
            category_id=1,
            category_name="文件管理",
            is_remote=True,
            remote_host="192.168.1.1",
            execution_mode=ExecutionMode.INTERACTIVE
        )

        assert record.id == 1
        assert record.command == "ls -la"
        assert record.category_id == 1
        assert record.category_name == "文件管理"
        assert record.is_remote is True
        assert record.remote_host == "192.168.1.1"
        assert record.execution_mode == ExecutionMode.INTERACTIVE
        assert isinstance(record.timestamp, datetime)

    def test_command_record_defaults(self):
        """测试命令记录默认值"""
        record = CategorizedCommandRecord(
            id=1,
            command="pwd"
        )

        assert record.id == 1
        assert record.command == "pwd"
        assert record.category_id is None
        assert record.category_name is None
        assert record.exit_code is None
        assert record.duration == 0.0
        assert record.is_remote is False
        assert record.remote_host is None


class TestSessionCommand:
    """测试 SessionCommand 数据类"""

    def test_create_session_command(self):
        """测试创建会话命令"""
        cmd = SessionCommand(
            id=1,
            session_id="session_123",
            command="whoami",
            mode=ExecutionMode.INTERACTIVE,
            output="root",
            exit_code=0
        )

        assert cmd.id == 1
        assert cmd.session_id == "session_123"
        assert cmd.command == "whoami"
        assert cmd.mode == ExecutionMode.INTERACTIVE
        assert cmd.output == "root"
        assert cmd.exit_code == 0
        assert isinstance(cmd.timestamp, datetime)


class TestCategoryStatistics:
    """测试 CategoryStatistics 数据类"""

    def test_create_statistics(self):
        """测试创建统计信息"""
        stats = CategoryStatistics(
            category_id=1,
            category_name="网关_海思",
            total_commands=100,
            success_rate=0.95,
            avg_duration=0.5
        )

        assert stats.category_id == 1
        assert stats.category_name == "网关_海思"
        assert stats.total_commands == 100
        assert stats.success_rate == 0.95
        assert stats.avg_duration == 0.5


class TestSecurityIssue:
    """测试 SecurityIssue 数据类"""

    def test_create_security_issue(self):
        """测试创建安全问题"""
        issue = SecurityIssue(
            type="telnet_insecure",
            severity="high",
            message="Telnet 协议使用明文传输，不安全",
            suggestion="建议使用 SSH 协议进行加密连接"
        )

        assert issue.type == "telnet_insecure"
        assert issue.severity == "high"
        assert issue.message == "Telnet 协议使用明文传输，不安全"
        assert issue.suggestion == "建议使用 SSH 协议进行加密连接"
