"""远程连接数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class AuthType(Enum):
    """认证类型枚举"""
    PASSWORD = "password"
    KEY = "key"


class SessionStatus(Enum):
    """会话状态枚举"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ExecutionMode(Enum):
    """执行模式枚举"""
    INTERACTIVE = "interactive"
    AI = "ai"


class ConnectionProtocol(Enum):
    """连接协议枚举"""
    SSH = "ssh"
    TELNET = "telnet"


@dataclass
class DeviceProductCategory:
    """设备产品类别"""
    id: int
    name: str
    description: Optional[str] = None
    commands_count: int = 0
    connection_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RemoteConnectionConfig:
    """远程连接配置"""
    id: int
    name: str
    host: str
    port: int = 22
    auth_type: AuthType = AuthType.PASSWORD
    username: str = "root"
    password: Optional[str] = None
    key_path: Optional[str] = None
    product_category_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_connected: Optional[datetime] = None
    protocol: Optional[ConnectionProtocol] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.protocol is None:
            if self.port == 23:
                self.protocol = ConnectionProtocol.TELNET
            else:
                self.protocol = ConnectionProtocol.SSH


@dataclass
class ConnectionSession:
    """连接会话"""
    id: str
    config_id: int
    host: str
    port: int
    protocol: ConnectionProtocol
    username: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.CONNECTING
    current_mode: ExecutionMode = ExecutionMode.INTERACTIVE
    current_path: str = "~"
    commands_count: int = 0

    @property
    def is_active(self) -> bool:
        """检查会话是否活动"""
        return self.status == SessionStatus.CONNECTED


@dataclass
class CategorizedCommandRecord:
    """带类别的命令记录"""
    id: int
    command: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    exit_code: Optional[int] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_remote: bool = False
    remote_host: Optional[str] = None
    remote_port: Optional[int] = None
    execution_mode: ExecutionMode = ExecutionMode.INTERACTIVE


@dataclass
class SessionCommand:
    """会话中的命令"""
    id: int
    session_id: str
    command: str
    timestamp: datetime = field(default_factory=datetime.now)
    mode: ExecutionMode = ExecutionMode.INTERACTIVE
    output: Optional[str] = None
    exit_code: Optional[int] = None
    duration: float = 0.0


@dataclass
class CategoryStatistics:
    """类别统计信息"""
    category_id: int
    category_name: str
    total_commands: int = 0
    success_rate: float = 0.0
    avg_duration: float = 0.0
    last_used: Optional[datetime] = None
    usage_frequency: float = 0.0
    connection_count: int = 0


@dataclass
class SecurityIssue:
    """安全问题"""
    type: str
    severity: str
    message: str
    suggestion: str
