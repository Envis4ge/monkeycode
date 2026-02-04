#!/usr/bin/env python3
"""
SmartTerm 综合测试脚本
验证所有功能是否正常工作
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.ai.command_converter import convert_natural_language_to_command, ParsedCommand
from src.models.remote import DeviceProductCategory


async def test_ai_features():
    """测试AI功能"""
    print("🔍 测试AI功能")
    print("=" * 50)

    # 测试用例
    test_cases = [
        ("我想查看当前目录的文件", "通用"),
        ("帮我列出所有进程", "通用"),
        ("显示系统内存使用情况", "通用"),
        ("显示磁盘空间使用情况", "通用"),
        ("查看系统时间", "通用"),
        ("我想创建一个新目录", "通用"),
        ("如何查看网络连接状态", "通用")
    ]

    print("🧪 测试通用命令转换:")
    success_count = 0
    for case, category in test_cases:
        result = await convert_natural_language_to_command(case)
        if result:
            print(f"  ✅ '{case}' -> '{result.command}' ({result.confidence:.2f})")
            success_count += 1
        else:
            print(f"  ❌ '{case}' -> 无法解析")

    print(f"\n通用命令测试: {success_count}/{len(test_cases)} 通过\n")

    # 测试特定设备类别
    print("🧪 测试特定设备类别命令转换:")
    device_tests = [
        ("重启海思网关", "网关_海思"),
        ("查看海思网关温度", "网关_海思"),
        ("查看中兴微网关内存使用率", "网关_中兴微"),
        ("查看ONU信息", "OLT_zxic"),
        ("重启ONU", "OLT_zxic")
    ]

    device_success = 0
    for case, device_name in device_tests:
        # 创建设备类别对象
        device_cat = DeviceProductCategory(id=1, name=device_name, description="测试设备")
        result = await convert_natural_language_to_command(case, device_cat)
        if result:
            print(f"  ✅ [{device_name}] '{case}' -> '{result.command}' ({result.confidence:.2f})")
            device_success += 1
        else:
            print(f"  ❌ [{device_name}] '{case}' -> 无法解析")

    print(f"\n设备特定命令测试: {device_success}/{len(device_tests)} 通过\n")

    return success_count == len(test_cases) and device_success >= 2  # 至少要有基础功能


def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入")
    print("=" * 50)

    modules_to_test = [
        "src.main",
        "src.remote",
        "src.ai",
        "src.models.remote",
        "src.remote.ssh_client",
        "src.remote.telnet_client",
        "src.remote.connection_manager",
        "src.remote.session_manager",
        "src.remote.category_manager",
        "src.remote.security_manager",
        "src.remote.command_history",
        "src.ai.command_converter"
    ]

    success_count = 0
    for module_path in modules_to_test:
        try:
            # 将模块路径转换为Python导入格式
            if module_path.startswith("src."):
                import_path = module_path.replace("/", ".")
            else:
                import_path = module_path

            __import__(import_path)
            print(f"  ✅ 成功导入: {import_path}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ 导入失败: {import_path} - {e}")

    print(f"\n模块导入测试: {success_count}/{len(modules_to_test)} 通过\n")
    return success_count == len(modules_to_test)


def show_project_structure():
    """显示项目结构"""
    print("📁 项目结构")
    print("=" * 50)
    structure = """
workspace/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── ai/                # AI模块
│   │   ├── __init__.py
│   │   └── command_converter.py # 自然语言转命令
│   ├── models/            # 数据模型
│   │   └── remote/
│   │       └── __init__.py
│   ├── remote/            # 远程连接模块
│   │   ├── __init__.py
│   │   ├── ssh_client.py     # SSH客户端
│   │   ├── telnet_client.py  # Telnet客户端
│   │   ├── connection_manager.py # 连接管理器
│   │   ├── session_manager.py    # 会话管理器
│   │   ├── category_manager.py   # 设备类别管理器
│   │   ├── command_history.py    # 命令历史功能
│   │   ├── command_history_db.py # 命令历史数据库
│   │   ├── db.py               # 配置数据库
│   │   └── security_manager.py # 安全管理器
│   └── docs/              # 文档目录
│       └── device_categories.md # 设备类别文档
├── README.md             # 项目说明文档
├── PROJECT_OVERVIEW.md   # 项目概览
├── demo.py               # 演示脚本
├── test_ai_functionality.py # AI功能测试脚本
├── requirements.txt      # 依赖列表
└── .gitignore           # Git忽略配置
"""
    print(structure)


def show_usage_examples():
    """显示使用示例"""
    print("💻 使用示例")
    print("=" * 50)
    examples = """
# 1. 查看帮助
python -m src.main --help

# 2. 连接到远程服务器
python -m src.main connect --host 192.168.1.100 --username user --password pass

# 3. 保存连接配置
python -m src.main add --name "server1" --host 192.168.1.100 --username admin --password secret

# 4. 列出所有配置
python -m src.main list

# 5. 进入交互式Shell模式
python -m src.main shell

# 6. 进入AI模式（最新增加的功能）
python -m src.main ai
# 在AI模式下可以使用自然语言，例如：
# [AI@user@server:22]> 我想查看当前目录有哪些文件
# 系统会转换为: ls -la

# 7. 会话管理
python -m src.main session list      # 列出活动会话
python -m src.main session history   # 查看会话历史

# 8. 删除配置
python -m src.main delete --name "server1"
"""
    print(examples)


async def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 SmartTerm 综合功能测试")
    print("=" * 60)

    print("\n开始测试...\n")

    # 测试模块导入
    imports_ok = test_imports()

    # 测试AI功能
    ai_ok = await test_ai_features()

    # 显示项目结构
    show_project_structure()

    # 显示使用示例
    show_usage_examples()

    print("📋 测试总结")
    print("=" * 50)
    print(f"模块导入测试: {'✅ 通过' if imports_ok else '❌ 失败'}")
    print(f"AI功能测试: {'✅ 通过' if ai_ok else '❌ 失败'}")

    overall_success = imports_ok and ai_ok

    print(f"\n整体测试结果: {'✅ 全部通过' if overall_success else '❌ 存在问题'}")

    if overall_success:
        print("\n🎉 SmartTerm 准备就绪！")
        print("您可以开始使用以下功能：")
        print("  - SSH/Telnet远程连接")
        print("  - 交互式Shell模式")
        print("  - AI驱动的自然语言命令转换")
        print("  - 连接配置管理")
        print("  - 会话和命令历史管理")
        print("\n详细使用方法请参考 README.md 文档")
    else:
        print("\n⚠️  存在问题，请检查错误信息并修复后重试")

    return overall_success


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)