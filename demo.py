#!/usr/bin/env python3
"""
SmartTerm 演示脚本
展示远程连接功能的主要特性
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.main import SmartTermCLI
from src.models.remote import RemoteConnectionConfig, AuthType, ConnectionProtocol


def demo_usage():
    """演示SmartTerm的主要功能"""
    print("🔧 SmartTerm - 智能终端增强工具演示")
    print("=" * 50)

    print("\n1. 🚀 主要功能:")
    print("   • SSH/Telnet 远程连接")
    print("   • 连接配置持久化")
    print("   • 交互式Shell模式")
    print("   • 命令历史记录与补全")
    print("   • 设备产品类别管理")
    print("   • 安全检查与加密")

    print("\n2. 📋 命令示例:")
    print("   # 连接到远程服务器")
    print("   python -m src.main connect --host example.com --username user --password pass")
    print("")
    print("   # 保存连接配置")
    print("   python -m src.main add --name 'my-server' --host example.com --username user")
    print("")
    print("   # 列出已保存的配置")
    print("   python -m src.main list")
    print("")
    print("   # 进入交互式Shell")
    print("   python -m src.main shell")

    print("\n3. ⚡ 安全特性:")
    print("   • 自动检测不安全的Telnet连接")
    print("   • 密码加密存储")
    print("   • 弱密码检测")
    print("   • 主机密钥验证")

    print("\n4. 🛠️ 扩展能力:")
    print("   • 支持命令历史记录（方向键导航）")
    print("   • Tab键命令补全")
    print("   • 会话管理")
    print("   • 设备分类管理")

    print("\n💡 提示: 使用 --help 参数查看详细用法")
    print("   python -m src.main --help")


if __name__ == "__main__":
    demo_usage()