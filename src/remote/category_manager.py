"""
设备产品类别管理器
"""

import asyncio
import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..models.remote import (
    DeviceProductCategory,
    CategoryStatistics,
    CategorizedCommandRecord
)


logger = logging.getLogger(__name__)


class CategoryManager:
    """设备产品类别管理器"""

    def __init__(self):
        self._categories: dict[int, DeviceProductCategory] = {}
        self._category_counter = 0

    async def get_all_categories(self) -> List[DeviceProductCategory]:
        """获取所有类别

        Returns:
            类别列表
        """
        return list(self._categories.values())

    async def get_category_by_id(self, category_id: int) -> Optional[DeviceProductCategory]:
        """根据ID获取类别

        Args:
            category_id: 类别ID

        Returns:
            类别对象，如果不存在则返回None
        """
        return self._categories.get(category_id)

    async def create_category(
        self,
        name: str,
        description: Optional[str] = None
    ) -> int:
        """创建新类别

        Args:
            name: 类别名称
            description: 类别描述

        Returns:
            新创建的类别ID
        """
        category = DeviceProductCategory(
            id=self._category_counter,
            name=name,
            description=description
        )
        self._category_counter += 1
        self._categories[category.id] = category

        logger.info(f"Created category: {name} (ID: {category.id})")
        return category.id

    async def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """更新类别

        Args:
            category_id: 类别ID
            name: 新类别名称
            description: 新类别描述
        """
        category = self._categories.get(category_id)
        if not category:
            raise ValueError(f"Category {category_id} not found")

        if name:
            category.name = name
        if description:
            category.description = description

        logger.info(f"Updated category: {category_id}")

    async def delete_category(self, category_id: int) -> None:
        """删除类别

        Args:
            category_id: 类别ID
        """
        category = self._categories.pop(category_id, None)
        if not category:
            raise ValueError(f"Category {category_id} not found")

        logger.info(f"Deleted category: {category_id}")

    async def classify_command(
        self,
        command: str,
        connection_id: int,
        category_id: Optional[int] = None
    ) -> int:
        """根据连接配置自动标记命令的设备产品类别

        Args:
            command: 命令字符串
            connection_id: 连接配置ID
            category_id: 指定的类别ID（如果有）

        Returns:
            设备产品类别ID
        """
        if category_id is not None:
            return category_id

        # TODO: 根据连接配置关联的设备产品类型自动标记
        # 占位符实现
        logger.debug(f"Classifying command from connection {connection_id}")

        # 返回"未分类"类别（如果没有指定）
        return await self._get_or_create_uncategorized()

    async def get_category_statistics(self, category_id: int) -> CategoryStatistics:
        """获取设备产品类别的统计信息

        Args:
            category_id: 类别ID

        Returns:
            统计信息
        """
        category = self._categories.get(category_id)
        if not category:
            raise ValueError(f"Category {category_id} not found")

        return CategoryStatistics(
            category_id=category.id,
            category_name=category.name,
            total_commands=category.commands_count,
            connection_count=category.connection_count
        )

    async def get_all_statistics(self) -> Dict[int, CategoryStatistics]:
        """获取所有设备产品类别的统计信息

        Returns:
            类别ID到统计信息的映射
        """
        stats = {}
        for category_id, category in self._categories.items():
            stats[category_id] = CategoryStatistics(
                category_id=category.id,
                category_name=category.name,
                total_commands=category.commands_count,
                connection_count=category.connection_count
            )
        return stats

    async def search_commands(
        self,
        query: str,
        category_id: Optional[int] = None
    ) -> List[CategorizedCommandRecord]:
        """搜索命令

        Args:
            query: 搜索关键词
            category_id: 设备产品类别ID（可选，指定则在该类别范围内搜索）

        Returns:
            匹配的命令记录列表
        """
        # TODO: 从数据库搜索命令
        # 占位符实现
        logger.debug(f"Searching commands: {query}, category: {category_id}")
        return []

    async def get_connections_by_category(
        self,
        category_id: int
    ) -> List:
        """获取属于指定设备产品类别的所有连接配置

        Args:
            category_id: 设备产品类别ID

        Returns:
            连接配置列表
        """
        # TODO: 从数据库加载连接配置
        # 占位符实现
        logger.debug(f"Getting connections for category: {category_id}")
        return []

    async def export_commands(
        self,
        category_id: Optional[int] = None,
        format: str = "json"
    ) -> str:
        """导出命令历史

        Args:
            category_id: 类别ID（可选，不指定则导出所有）
            format: 导出格式（json、csv）

        Returns:
            导出的数据字符串
        """
        # TODO: 从数据库导出命令
        # 占位符实现
        logger.debug(f"Exporting commands: category={category_id}, format={format}")

        if format.lower() == "json":
            import json
            return json.dumps([], indent=2)
        elif format.lower() == "csv":
            return ""
        else:
            return ""

    async def _get_or_create_uncategorized(self) -> int:
        """获取或创建"未分类"类别"""
        for category in self._categories.values():
            if category.name == "未分类":
                return category.id

        return await self.create_category("未分类", "未分类的命令")

    async def initialize_default_categories(self) -> None:
        """初始化默认设备产品类别"""
        # 检查是否已经有类别，避免重复初始化
        if len(self._categories) > 0:
            return

        default_categories = [
            ("网关_海思", "海思芯片的网关设备"),
            ("网关_中兴微", "中兴微芯片的网关设备"),
            ("OLT_zxic", "zxic 光线路终端"),
            ("Olt_烽火", "烽火光线路终端"),
            ("未分类", "未分类的命令")
        ]

        for name, desc in default_categories:
            await self.create_category(name, desc)

        logger.info("Initialized default categories")
