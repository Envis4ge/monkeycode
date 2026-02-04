#!/usr/bin/env python3
"""
测试连接配置数据库功能
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.remote.db import RemoteConfigDatabase
from src.models.remote import RemoteConnectionConfig, AuthType, ConnectionProtocol


async def test_database():
    """测试数据库功能"""

    print("=" * 60)
    print("测试连接配置数据库功能")
    print("=" * 60)

    # 创建数据库实例
    db = RemoteConfigDatabase()

    print("\n1. 创建测试配置")

    # 创建测试配置
    test_config = RemoteConnectionConfig(
        id=0,  # 会由数据库自动生成
        name="Test Server",
        host="192.168.1.100",
        port=22,
        auth_type=AuthType.PASSWORD,
        username="testuser",
        password="testpass",
        key_path=None,
        product_category_id=1
    )

    print(f"   配置: {test_config.name}")
    print(f"   主机: {test_config.host}:{test_config.port}")
    print(f"   用户: {test_config.username}")

    print("\n2. 保存配置到数据库")
    try:
        config_id = await db.save_config(test_config)
        print(f"   成功保存，ID: {config_id}")
        test_config.id = config_id
    except Exception as e:
        print(f"   保存失败: {e}")
        return False

    print("\n3. 根据ID获取配置")
    try:
        retrieved_config = await db.get_config(config_id)
        if retrieved_config:
            print(f"   成功获取配置: {retrieved_config.name}")
            print(f"   主机: {retrieved_config.host}:{retrieved_config.port}")
            print(f"   用户: {retrieved_config.username}")
        else:
            print("   未找到配置")
            return False
    except Exception as e:
        print(f"   获取失败: {e}")
        return False

    print("\n4. 根据名称获取配置")
    try:
        retrieved_by_name = await db.get_config_by_name("Test Server")
        if retrieved_by_name:
            print(f"   成功获取配置: {retrieved_by_name.name}")
        else:
            print("   未找到配置")
            return False
    except Exception as e:
        print(f"   获取失败: {e}")
        return False

    print("\n5. 更新配置")
    try:
        test_config.username = "updated_user"
        await db.update_config(test_config)
        print(f"   成功更新配置")

        # 验证更新
        updated_config = await db.get_config(config_id)
        print(f"   更新后用户名: {updated_config.username}")
    except Exception as e:
        print(f"   更新失败: {e}")
        return False

    print("\n6. 列出所有配置")
    try:
        all_configs = await db.list_configs()
        print(f"   找到 {len(all_configs)} 个配置:")
        for cfg in all_configs:
            print(f"     - {cfg.name} ({cfg.host}:{cfg.port})")
    except Exception as e:
        print(f"   列出失败: {e}")
        return False

    print("\n7. 更新最后连接时间")
    try:
        await db.update_last_connected(config_id)
        print("   成功更新最后连接时间")
    except Exception as e:
        print(f"   更新失败: {e}")
        return False

    print("\n8. 删除测试配置")
    try:
        success = await db.delete_config(config_id)
        if success:
            print("   成功删除配置")
        else:
            print("   删除失败")
            return False
    except Exception as e:
        print(f"   删除失败: {e}")
        return False

    print("\n9. 验证配置已删除")
    try:
        deleted_config = await db.get_config(config_id)
        if not deleted_config:
            print("   配置已成功删除")
        else:
            print("   配置仍然存在")
            return False
    except Exception as e:
        print(f"   验证失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = asyncio.run(test_database())
    if success:
        print("\n数据库功能测试成功！")
        sys.exit(0)
    else:
        print("\n数据库功能测试失败！")
        sys.exit(1)