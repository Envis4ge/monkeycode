#!/usr/bin/env python3
"""
SmartTerm Web UI 演示
展示整合后的Web界面功能
"""

import asyncio
import json
from src.ai.command_converter import convert_natural_language_to_command
from src.models.remote import DeviceProductCategory

async def demo_web_ui_features():
    """演示Web UI的主要功能"""
    print("🌐 SmartTerm Web UI - 功能演示")
    print("=" * 60)

    print("\n🎯 Web界面主要功能:")
    print("   1. 终端仿真器 (xterm.js)")
    print("   2. AI命令助手")
    print("   3. 连接管理器")
    print("   4. 会话管理器")
    print("   5. 设置面板")

    print("\n🔍 后端API功能演示:")
    print("   GET  /api/configs     - 获取连接配置")
    print("   POST /api/configs     - 添加连接配置")
    print("   POST /api/connect     - 连接远程主机")
    print("   POST /api/disconnect  - 断开连接")
    print("   POST /api/command     - 执行命令")
    print("   WS   /ws/terminal     - WebSocket终端")

    print("\n🧠 AI命令转换演示:")
    ai_requests = [
        "我想查看当前目录的文件",
        "显示系统内存使用情况",
        "如何查看网络连接状态"
    ]

    for req in ai_requests:
        result = await convert_natural_language_to_command(req)
        if result:
            print(f"   '{req}' -> '{result.command}' (置信度: {result.confidence:.2f})")

    print("\n🛠️ 设备特定命令演示 (OLT设备):")
    olt_category = DeviceProductCategory(
        id=3,
        name="OLT_zxic",
        description="zxic 光线路终端"
    )

    olt_requests = ["查看ONU信息", "重启ONU设备"]
    for req in olt_requests:
        result = await convert_natural_language_to_command(req, olt_category)
        if result:
            print(f"   '{req}' -> '{result.command}' (置信度: {result.confidence:.2f})")

    print("\n📁 连接配置管理演示:")
    print("   - 添加连接配置 (HTTP POST)")
    print("   - 编辑连接配置 (HTTP PUT)")
    print("   - 删除连接配置 (HTTP DELETE)")
    print("   - 列出所有配置 (HTTP GET)")

    print("\n🔗 连接功能演示:")
    print("   - SSH连接 (端口22)")
    print("   - Telnet连接 (端口23)")
    print("   - 密码认证和密钥认证")
    print("   - WebSocket实时终端交互")

    print("\n⚡ 实时终端功能:")
    print("   - 基于WebSocket的双向通信")
    print("   - 实时命令执行和输出")
    print("   - 终端仿真 (xterm.js)")
    print("   - 交互式会话管理")

    print("\n" + "=" * 60)
    print("✅ SmartTerm Web UI 准备就绪!")
    print("   后端服务: uvicorn web_app:app --host 0.0.0.0 --port 8000")
    print("   前端界面: cd frontend && npm start")
    print("   访问地址: http://localhost:3000")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo_web_ui_features())