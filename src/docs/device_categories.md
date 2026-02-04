# 设备产品类别文档

本文档为不同类型的网络设备提供操作指南和常用命令。

## 海思网关 (网关_海思)

### 常用命令

#### 系统信息
- `hisystem_status` - 查看海思网关系统状态
- `cat /proc/cpuinfo` - 查看CPU信息
- `cat /sys/class/thermal/thermal_zone*/temp` - 查看温度信息
- `reboot` - 重启设备

#### 网络配置
- `ifconfig` - 查看网络接口状态
- `brctl show` - 查看桥接接口
- `hisystem_diag` - 网络诊断命令（特定工具）

#### 日志查看
- `dmesg` - 内核日志
- `hisystem_log` - 系统日志（特定工具）

### 特殊注意事项
- 某些命令可能需要特权用户才能执行
- 海思网关可能使用专有的管理工具

## 中兴微网关 (网关_中兴微)

### 常用命令

#### 系统信息
- `cat /proc/meminfo` - 查看内存使用情况
- `cat /proc/loadavg` - 查看系统负载
- `uname -a` - 系统信息

#### 网络操作
- `zxdiag_netstat` - 网络状态诊断（特定工具）
- `iptables -L` - 查看防火墙规则

#### 服务管理
- `systemctl status [service]` - 查看服务状态
- `systemctl start [service]` - 启动服务
- `systemctl stop [service]` - 停止服务

## OLT设备 (OLT_zxic / Olt_烽火)

### 常用命令

#### ONT/ONU管理
- `display ont info` - 查看ONU信息
- `ont reboot` - 重启ONU
- `display ont optic-power` - 查看光功率

#### VLAN配置
- `vlan config` - VLAN配置
- `display vlan` - 查看VLAN信息

#### 业务配置
- `service-port config` - 业务端口配置

### 注意事项
- OLT设备通常有复杂的配置层级
- 需要先进入配置模式才能执行某些命令
- 修改配置后可能需要保存