"""
AI命令转换器
将自然语言转换为实际命令
"""

import asyncio
import re
from typing import Optional, Dict, List
from dataclasses import dataclass

from ..models.remote import RemoteConnectionConfig, DeviceProductCategory


@dataclass
class ParsedCommand:
    """解析后的命令结构"""
    command: str  # 实际要执行的命令
    explanation: str  # 对命令的解释
    confidence: float  # 置信度 (0-1)


class AICommandConverter:
    """AI命令转换器，将自然语言转换为实际命令"""

    def __init__(self):
        # 模拟AI转换的规则库 - 实际项目中这应该是真正的AI模型
        self.command_patterns = {
            # 文件操作
            r'(?i).*创建.*目录.*': self._handle_create_directory,
            r'(?i).*列出.*文件.*': self._handle_list_files,
            r'(?i).*删除.*文件.*': self._handle_delete_file,
            r'(?i).*复制.*文件.*': self._handle_copy_file,
            r'(?i).*移动.*文件.*': self._handle_move_file,

            # 系统信息
            r'(?i).*查看.*进程.*': self._handle_list_processes,
            r'(?i).*系统.*内存.*': self._handle_check_memory,
            r'(?i).*磁盘.*空间.*': self._handle_check_disk_space,
            r'(?i).*系统.*信息.*': self._handle_system_info,

            # 网络
            r'(?i).*测试.*连接.*': self._handle_ping_host,
            r'(?i).*网络.*状态.*': self._handle_network_status,

            # 服务
            r'(?i).*重启.*服务.*': self._handle_restart_service,
            r'(?i).*启动.*服务.*': self._handle_start_service,
            r'(?i).*停止.*服务.*': self._handle_stop_service,
            r'(?i).*状态.*服务.*': self._handle_service_status,
        }

    async def convert_natural_language(
        self,
        natural_language: str,
        category: Optional[DeviceProductCategory] = None
    ) -> Optional[ParsedCommand]:
        """
        将自然语言转换为实际命令

        Args:
            natural_language: 自然语言指令
            category: 设备产品类别（可选，用于根据特定设备文档定制命令）

        Returns:
            解析后的命令，如果无法解析则返回None
        """
        # 首先尝试基于设备类别的特定处理
        if category:
            command = await self._convert_based_on_category(natural_language, category)
            if command:
                return command

        # 如果基于类别的转换失败，尝试通用模式匹配
        for pattern, handler in self.command_patterns.items():
            if re.search(pattern, natural_language, re.IGNORECASE):
                return handler(natural_language)

        # 如果都没有匹配，尝试更通用的方法
        return await self._convert_generic(natural_language)

    async def _convert_based_on_category(
        self,
        natural_language: str,
        category: DeviceProductCategory
    ) -> Optional[ParsedCommand]:
        """基于设备产品类别转换命令"""
        category_lower = category.name.lower()

        # 针对不同设备类别进行特定处理
        if "网关_海思" in category_lower:
            return await self._convert_hisilicon_gateway(natural_language)
        elif "网关_中兴微" in category_lower:
            return await self._convert_zxmicro_gateway(natural_language)
        elif "olt_zxic" in category_lower or "olt_烽火" in category_lower:
            return await self._convert_olt_commands(natural_language)

        return None

    async def _convert_hisilicon_gateway(self, natural_language: str) -> Optional[ParsedCommand]:
        """海思网关特定命令转换"""
        if "重启设备" in natural_language:
            return ParsedCommand(
                command="reboot",
                explanation="重启海思网关设备",
                confidence=0.9
            )
        elif "查看温度" in natural_language:
            return ParsedCommand(
                command="cat /sys/class/thermal/thermal_zone*/temp",
                explanation="查看海思网关CPU温度",
                confidence=0.85
            )
        elif "网络诊断" in natural_language:
            return ParsedCommand(
                command="hisystem_diag",
                explanation="执行海思网关网络诊断（需特定工具）",
                confidence=0.7
            )
        return None

    async def _convert_zxmicro_gateway(self, natural_language: str) -> Optional[ParsedCommand]:
        """中兴微网关特定命令转换"""
        if "重启设备" in natural_language:
            return ParsedCommand(
                command="reboot",
                explanation="重启中兴微网关设备",
                confidence=0.9
            )
        elif "查看内存使用率" in natural_language:
            return ParsedCommand(
                command="cat /proc/meminfo | grep -E '(MemTotal|MemFree|MemAvailable)'",
                explanation="查看中兴微网关内存使用情况",
                confidence=0.85
            )
        elif "网络诊断" in natural_language:
            return ParsedCommand(
                command="zxdiag_netstat",
                explanation="执行中兴微网关网络诊断（需特定工具）",
                confidence=0.7
            )
        return None

    async def _convert_olt_commands(self, natural_language: str) -> Optional[ParsedCommand]:
        """OLT设备特定命令转换"""
        if "查看ONU" in natural_language or "查看光猫" in natural_language:
            return ParsedCommand(
                command="display ont info",
                explanation="查看OLT下挂载的ONU信息",
                confidence=0.8
            )
        elif "重启ONU" in natural_language:
            return ParsedCommand(
                command="ont reboot",
                explanation="重启OLT下特定ONU设备",
                confidence=0.75
            )
        elif "配置VLAN" in natural_language:
            return ParsedCommand(
                command="vlan config",
                explanation="配置OLT VLAN信息",
                confidence=0.7
            )
        return None

    async def _convert_generic(self, natural_language: str) -> Optional[ParsedCommand]:
        """通用命令转换"""
        # 尝试提取一些常见的自然语言模式
        if "查看当前目录" in natural_language or "显示当前目录内容" in natural_language or "列出文件" in natural_language or "当前目录的文件" in natural_language:
            return ParsedCommand("ls -la", "列出当前目录的所有文件和详细信息", 0.9)
        elif "查看当前用户" in natural_language:
            return ParsedCommand("whoami", "显示当前登录的用户名", 0.95)
        elif "查看系统时间" in natural_language:
            return ParsedCommand("date", "显示系统当前时间和日期", 0.95)
        elif "查看系统负载" in natural_language or "系统负载" in natural_language:
            return ParsedCommand("uptime", "显示系统运行时间及平均负载", 0.85)
        elif "查看磁盘使用情况" in natural_language or "磁盘空间" in natural_language:
            return ParsedCommand("df -h", "显示磁盘使用情况", 0.9)
        elif "查看内存使用" in natural_language or "系统内存" in natural_language:
            return ParsedCommand("free -m", "显示内存使用情况（MB单位）", 0.85)
        elif "查看进程" in natural_language or "列出进程" in natural_language:
            return ParsedCommand("ps aux", "显示所有运行的进程", 0.8)
        elif "查找文件" in natural_language:
            return ParsedCommand("find . -type f", "在当前目录递归查找所有文件", 0.75)
        elif "网络连接状态" in natural_language or "网络状态" in natural_language:
            return ParsedCommand("netstat -tulpn", "显示TCP/UDP监听端口及对应的进程", 0.8)

        # 如果以上都不匹配，尝试更简单的方式
        return None

    def _handle_create_directory(self, natural_language: str) -> ParsedCommand:
        """处理创建目录请求"""
        # 从自然语言中提取目录名
        dir_match = re.search(r'["\']([^"\']+)["\']', natural_language)
        if dir_match:
            dirname = dir_match.group(1)
            return ParsedCommand(
                f"mkdir -p {dirname}",
                f"创建目录 {dirname}（包括父目录）",
                0.8
            )
        else:
            return ParsedCommand(
                "mkdir new_directory",
                "创建新目录（请替换 new_directory 为实际目录名）",
                0.6
            )

    def _handle_list_files(self, natural_language: str) -> ParsedCommand:
        """处理列出文件请求"""
        return ParsedCommand(
            "ls -la",
            "列出当前目录所有文件（包括隐藏文件）及其详细信息",
            0.9
        )

    def _handle_delete_file(self, natural_language: str) -> ParsedCommand:
        """处理删除文件请求"""
        file_match = re.search(r'["\']([^"\']+)["\']', natural_language)
        if file_match:
            filename = file_match.group(1)
            return ParsedCommand(
                f"rm -f {filename}",
                f"强制删除文件 {filename}",
                0.8
            )
        else:
            return ParsedCommand(
                "rm filename",
                "删除文件（请替换 filename 为实际文件名）",
                0.6
            )

    def _handle_copy_file(self, natural_language: str) -> ParsedCommand:
        """处理复制文件请求"""
        return ParsedCommand(
            "cp source destination",
            "复制文件（请替换 source 和 destination 为实际路径）",
            0.7
        )

    def _handle_move_file(self, natural_language: str) -> ParsedCommand:
        """处理移动文件请求"""
        return ParsedCommand(
            "mv source destination",
            "移动文件（请替换 source 和 destination 为实际路径）",
            0.7
        )

    def _handle_list_processes(self, natural_language: str) -> ParsedCommand:
        """处理查看进程请求"""
        return ParsedCommand(
            "ps aux | grep -v grep",
            "列出所有运行的进程，排除grep命令自身",
            0.85
        )

    def _handle_check_memory(self, natural_language: str) -> ParsedCommand:
        """处理检查内存请求"""
        return ParsedCommand(
            "free -h",
            "显示系统内存使用情况（Human-readable格式）",
            0.9
        )

    def _handle_check_disk_space(self, natural_language: str) -> ParsedCommand:
        """处理检查磁盘空间请求"""
        return ParsedCommand(
            "df -h",
            "显示所有磁盘分区使用情况（Human-readable格式）",
            0.9
        )

    def _handle_system_info(self, natural_language: str) -> ParsedCommand:
        """处理查看系统信息请求"""
        return ParsedCommand(
            "uname -a",
            "显示系统详细信息（内核版本、主机名等）",
            0.85
        )

    def _handle_ping_host(self, natural_language: str) -> ParsedCommand:
        """处理ping主机请求"""
        host_match = re.search(r'([a-zA-Z0-9][a-zA-Z0-9\-\.]+[a-zA-Z]{2,})', natural_language)
        if host_match:
            host = host_match.group(1)
            return ParsedCommand(
                f"ping -c 4 {host}",
                f"向主机 {host} 发送4个ICMP请求包",
                0.75
            )
        else:
            return ParsedCommand(
                "ping -c 4 8.8.8.8",
                "向Google DNS服务器发送ICMP请求测试网络连通性",
                0.7
            )

    def _handle_network_status(self, natural_language: str) -> ParsedCommand:
        """处理网络状态请求"""
        return ParsedCommand(
            "netstat -tulpn",
            "显示TCP/UDP监听端口及对应的进程",
            0.8
        )

    def _handle_restart_service(self, natural_language: str) -> ParsedCommand:
        """处理重启服务请求"""
        service_match = re.search(r'(\w+)\s+(?:服务|service)', natural_language)
        if service_match:
            service = service_match.group(1)
            return ParsedCommand(
                f"systemctl restart {service}",
                f"重启 {service} 服务",
                0.75
            )
        else:
            return ParsedCommand(
                "systemctl restart service_name",
                "重启服务（请替换 service_name 为实际服务名）",
                0.6
            )

    def _handle_start_service(self, natural_language: str) -> ParsedCommand:
        """处理启动服务请求"""
        service_match = re.search(r'(\w+)\s+(?:服务|service)', natural_language)
        if service_match:
            service = service_match.group(1)
            return ParsedCommand(
                f"systemctl start {service}",
                f"启动 {service} 服务",
                0.75
            )
        else:
            return ParsedCommand(
                "systemctl start service_name",
                "启动服务（请替换 service_name 为实际服务名）",
                0.6
            )

    def _handle_stop_service(self, natural_language: str) -> ParsedCommand:
        """处理停止服务请求"""
        service_match = re.search(r'(\w+)\s+(?:服务|service)', natural_language)
        if service_match:
            service = service_match.group(1)
            return ParsedCommand(
                f"systemctl stop {service}",
                f"停止 {service} 服务",
                0.75
            )
        else:
            return ParsedCommand(
                "systemctl stop service_name",
                "停止服务（请替换 service_name 为实际服务名）",
                0.6
            )

    def _handle_service_status(self, natural_language: str) -> ParsedCommand:
        """处理查看服务状态请求"""
        service_match = re.search(r'(\w+)\s+(?:服务|service)', natural_language)
        if service_match:
            service = service_match.group(1)
            return ParsedCommand(
                f"systemctl status {service}",
                f"查看 {service} 服务状态",
                0.75
            )
        else:
            return ParsedCommand(
                "systemctl status service_name",
                "查看服务状态（请替换 service_name 为实际服务名）",
                0.6
            )


# 全局AI转换器实例
ai_converter = AICommandConverter()


async def convert_natural_language_to_command(
    natural_language: str,
    category: Optional[DeviceProductCategory] = None
) -> Optional[ParsedCommand]:
    """全局函数：将自然语言转换为命令"""
    return await ai_converter.convert_natural_language(natural_language, category)