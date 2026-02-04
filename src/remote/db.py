"""
远程连接配置数据库模块
"""

import sqlite3
import json
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from ..models.remote import RemoteConnectionConfig, AuthType, ConnectionProtocol


logger = logging.getLogger(__name__)


class RemoteConfigDatabase:
    """远程连接配置数据库"""

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
            db_path = str(db_dir / "remote_configs.db")

        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建连接配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connection_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    host TEXT NOT NULL,
                    port INTEGER DEFAULT 22,
                    auth_type TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT,
                    key_path TEXT,
                    product_category_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_connected TIMESTAMP,
                    protocol TEXT,
                    encrypted INTEGER DEFAULT 0
                )
            ''')

            # 创建触发器，自动更新updated_at字段
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_configs_updated_at
                AFTER UPDATE ON connection_configs
                FOR EACH ROW
                BEGIN
                    UPDATE connection_configs SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
            ''')

            conn.commit()

        logger.info(f"Database initialized at {self.db_path}")

    async def save_config(self, config: RemoteConnectionConfig) -> int:
        """保存连接配置

        Args:
            config: 连接配置对象

        Returns:
            配置ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 将枚举转换为字符串
            auth_type_str = config.auth_type.value if isinstance(config.auth_type, AuthType) else config.auth_type
            protocol_str = config.protocol.value if config.protocol and isinstance(config.protocol, ConnectionProtocol) else config.protocol

            try:
                cursor.execute('''
                    INSERT INTO connection_configs
                    (name, host, port, auth_type, username, password, key_path, product_category_id, protocol)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    config.name, config.host, config.port, auth_type_str,
                    config.username, config.password, config.key_path,
                    config.product_category_id, protocol_str
                ))

                config_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Saved connection config: {config.name} (ID: {config_id})")
                return config_id
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to save config {config.name}: {e}")
                raise ValueError(f"Configuration with name '{config.name}' already exists")

    async def update_config(self, config: RemoteConnectionConfig) -> None:
        """更新连接配置

        Args:
            config: 连接配置对象
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 将枚举转换为字符串
            auth_type_str = config.auth_type.value if isinstance(config.auth_type, AuthType) else config.auth_type
            protocol_str = config.protocol.value if config.protocol and isinstance(config.protocol, ConnectionProtocol) else config.protocol

            cursor.execute('''
                UPDATE connection_configs
                SET host=?, port=?, auth_type=?, username=?, password=?,
                    key_path=?, product_category_id=?, protocol=?
                WHERE id=?
            ''', (
                config.host, config.port, auth_type_str, config.username,
                config.password, config.key_path, config.product_category_id,
                protocol_str, config.id
            ))

            if cursor.rowcount == 0:
                raise ValueError(f"Configuration with ID {config.id} not found")

            conn.commit()
            logger.info(f"Updated connection config: {config.name} (ID: {config.id})")

    async def get_config(self, config_id: int) -> Optional[RemoteConnectionConfig]:
        """根据ID获取连接配置

        Args:
            config_id: 配置ID

        Returns:
            连接配置对象，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, host, port, auth_type, username, password,
                       key_path, product_category_id, created_at, updated_at,
                       last_connected, protocol
                FROM connection_configs
                WHERE id=?
            ''', (config_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_config(row)
            return None

    async def get_config_by_name(self, name: str) -> Optional[RemoteConnectionConfig]:
        """根据名称获取连接配置

        Args:
            name: 配置名称

        Returns:
            连接配置对象，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, host, port, auth_type, username, password,
                       key_path, product_category_id, created_at, updated_at,
                       last_connected, protocol
                FROM connection_configs
                WHERE name=?
            ''', (name,))

            row = cursor.fetchone()
            if row:
                return self._row_to_config(row)
            return None

    async def list_configs(self) -> List[RemoteConnectionConfig]:
        """列出所有连接配置

        Returns:
            连接配置列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, host, port, auth_type, username, password,
                       key_path, product_category_id, created_at, updated_at,
                       last_connected, protocol
                FROM connection_configs
                ORDER BY name
            ''')

            configs = []
            for row in cursor.fetchall():
                configs.append(self._row_to_config(row))
            return configs

    async def delete_config(self, config_id: int) -> bool:
        """删除连接配置

        Args:
            config_id: 配置ID

        Returns:
            是否删除成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM connection_configs WHERE id=?', (config_id,))
            conn.commit()

            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted connection config: {config_id}")
            else:
                logger.warning(f"Attempted to delete non-existent config: {config_id}")

            return deleted

    async def update_last_connected(self, config_id: int) -> None:
        """更新最后连接时间

        Args:
            config_id: 配置ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE connection_configs
                SET last_connected=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (config_id,))
            conn.commit()

    def _row_to_config(self, row) -> RemoteConnectionConfig:
        """将数据库行转换为配置对象

        Args:
            row: 数据库行数据

        Returns:
            远程连接配置对象
        """
        (config_id, name, host, port, auth_type, username, password,
         key_path, product_category_id, created_at, updated_at,
         last_connected, protocol) = row

        # 转换字符串为枚举
        auth_type_enum = AuthType(auth_type) if auth_type else AuthType.PASSWORD
        protocol_enum = ConnectionProtocol(protocol) if protocol else None

        # 转换时间字符串为datetime对象
        created_at_dt = datetime.fromisoformat(created_at) if created_at else datetime.now()
        updated_at_dt = datetime.fromisoformat(updated_at) if updated_at else created_at_dt
        last_connected_dt = datetime.fromisoformat(last_connected) if last_connected else None

        config = RemoteConnectionConfig(
            id=config_id,
            name=name,
            host=host,
            port=port,
            auth_type=auth_type_enum,
            username=username,
            password=password,
            key_path=key_path,
            product_category_id=product_category_id,
            created_at=created_at_dt,
            updated_at=updated_at_dt,
            last_connected=last_connected_dt,
            protocol=protocol_enum
        )

        return config