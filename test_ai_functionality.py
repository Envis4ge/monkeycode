#!/usr/bin/env python3
"""
测试AI命令转换功能
"""

import asyncio
from src.ai.command_converter import convert_natural_language_to_command, ParsedCommand
from src.models.remote import DeviceProductCategory


async def test_ai_conversion():
    """测试AI命令转换功能"""
    print("🔍 测试AI命令转换功能")
    print("=" * 50)

    # 测试通用命令
    test_cases = [
        "我想查看当前目录的文件",
        "帮我列出所有进程",
        "显示系统内存使用情况",
        "显示磁盘空间使用情况",
        "查看系统时间",
        "我想创建一个新目录",
        "如何查看网络连接状态"
    ]

    print("🧪 测试通用命令转换:")
    for case in test_cases:
        result = await convert_natural_language_to_command(case)
        if result:
            print(f"  输入: {case}")
            print(f"  输出: {result.command}")
            print(f"  说明: {result.explanation}")
            print(f"  置信度: {result.confidence:.2f}")
            print()

    # 测试特定设备类别命令
    print("🧪 测试特定设备类别命令转换:")

    # 海思网关
    hisilicon_cat = DeviceProductCategory(id=1, name="网关_海思", description="海思芯片的网关设备")
    hisilicon_result = await convert_natural_language_to_command("重启海思网关", hisilicon_cat)
    if hisilicon_result:
        print(f"  海思网关 - 输入: 重启海思网关")
        print(f"  输出: {hisilicon_result.command}")
        print(f"  说明: {hisilicon_result.explanation}")
        print(f"  置信度: {hisilicon_result.confidence:.2f}")
        print()

    # 中兴微网关
    zxmicro_cat = DeviceProductCategory(id=2, name="网关_中兴微", description="中兴微芯片的网关设备")
    zxmicro_result = await convert_natural_language_to_command("查看内存使用率", zxmicro_cat)
    if zxmicro_result:
        print(f"  中兴微网关 - 输入: 查看内存使用率")
        print(f"  输出: {zxmicro_result.command}")
        print(f"  说明: {zxmicro_result.explanation}")
        print(f"  置信度: {zxmicro_result.confidence:.2f}")
        print()

    # OLT设备
    olt_cat = DeviceProductCategory(id=3, name="OLT_zxic", description="zxic 光线路终端")
    olt_result = await convert_natural_language_to_command("查看ONU信息", olt_cat)
    if olt_result:
        print(f"  OLT设备 - 输入: 查看ONU信息")
        print(f"  输出: {olt_result.command}")
        print(f"  说明: {olt_result.explanation}")
        print(f"  置信度: {olt_result.confidence:.2f}")
        print()

    print("✅ AI命令转换功能测试完成!")


if __name__ == "__main__":
    asyncio.run(test_ai_conversion())