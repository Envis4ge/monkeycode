# ZXA10 C680&C600&C650&C620 命令参考手册 - 知识库

> 中兴光接入局端汇聚设备命令行知识库 | 版本 V1.2.1 | 5211条命令

---

## 📖 项目简介

本知识库基于 ZXA10 C680/C600/C650/C620 光接入局端汇聚设备的官方命令参考手册（V1.2.1）构建，旨在为 AI 助手提供结构化的命令查询能力。

### 源文件信息

| 项目 | 内容 |
|------|------|
| 设备型号 | ZXA10 C680 / C600 / C650 / C620 |
| 文档版本 | V1.2.1 |
| 出版日期 | 2020-08-31 |
| 命令总数 | 5211 条 |
| 章节数量 | 13 个 |

---

## 📁 文件结构

```
output/
│
├── 📄 文档文件
│   ├── README.md                      # 本文件
│   ├── KNOWLEDGE_INDEX.md             # 知识总览
│   ├── INDEX_BY_NAME.md               # 按字母排序索引 (A-Z)
│   ├── INDEX_BY_KEYWORD.md            # 按关键字分类索引
│   ├── SCENARIO_COMMANDS.md           # 场景命令对照表 ⭐
│   ├── LEARNING_GUIDE.md              # 学习指南
│   ├── LEARNING_EXAMPLES.md           # 学习范例
│   ├── QA_REPORT.md                   # 质检报告
│   └── PROJECT_PROGRESS.md            # 项目进度跟踪
│
└── 📋 JSON数据文件
    ├── INDEX.json                     # 总索引 (包含所有命令)
    ├── COMMANDS_FULL.json             # 完整命令列表
    ├── 01_01产品管理.json            # 69条命令
    ├── 02_02运行支撑.json            # 103条命令
    ├── 03_03接口配置.json            # 126条命令
    ├── 04_04产品配置.json            # 1644条命令
    ├── 05_05L2业务.json             # 189条命令
    ├── 06_06L3业务.json             # 308条命令
    ├── 07_07路由配置.json            # 1790条命令 ⚠️最大章节
    ├── 08_08组播配置.json            # 333条命令
    ├── 09_09MPLS配置.json            # 170条命令
    ├── 10_10VxLAN配置.json           # 20条命令
    ├── 11_11OAM命令.json             # 262条命令
    ├── 12_12安全配置.json            # 174条命令
    └── 13_13诊断和统计.json          # 23条命令
```

---

## 📚 13个章节概览

| 编号 | 章节名称 | 命令数 | 主要内容 |
|------|----------|--------|----------|
| 01 | 产品管理 | 69 | 系统管理、版本管理、切片操作、环境监控 |
| 02 | 运行支撑 | 103 | 设备管理、时钟模块、NTP、MIM管理 |
| 03 | 接口配置 | 126 | 端口配置、接口参数 |
| 04 | 产品配置 | 1644 | ACL、QoS、DHCP、L2/L3命令等（最大章节）|
| 05 | L2业务 | 189 | LACP、LLDP、MAC管理、STP生成树 |
| 06 | L3业务 | 308 | BFD、DHCP/DHCPv6、DNS配置 |
| 07 | 路由配置 | 1790 | BGP、ISIS、RIP、OSPF、VRF、静态路由 |
| 08 | 组播配置 | 333 | IPv4/IPv6组播、IGMP、PIM |
| 09 | MPLS配置 | 170 | MPLS、LDP、PWE3、MPLS OAM |
| 10 | VxLAN配置 | 20 | VxLAN隧道配置 |
| 11 | OAM命令 | 262 | FTP/SFTP/TFTP、NETCONF、SNMP、Telnet |
| 12 | 安全配置 | 174 | AAA、RADIUS、SSH、SSL、TACACS+ |
| 13 | 诊断和统计 | 23 | PING、traceroute、性能统计 |

---

## 🎯 使用方式

### 场景查询（推荐）

查询特定场景相关的命令：

| 场景 | 关键字示例 | 命令数 |
|------|-----------|--------|
| 系统基本操作 | reload, reset, reboot | 23 |
| 用户和权限管理 | user, password, aaa | 94 |
| 接口配置 | interface, port, mtu | 316 |
| VLAN配置 | vlan, trunk, access | 159 |
| DHCP配置 | dhcp, ip pool | 107 |
| BGP配置 | bgp, neighbor, ebgp | 895 |
| OSPF配置 | ospf, area | 116 |
| QoS配置 | qos, traffic, queue | 191 |
| ACL配置 | acl, permit, deny | 28 |
| MPLS配置 | mpls, label, ldp | 139 |
| VxLAN配置 | vxlan, vni, nve | 17 |
| 组播配置 | multicast, igmp, pim | 267 |
| 安全认证 | radius, ssh, ssl | 93 |
| SNMP网管 | snmp, trap, mib | 115 |
| 诊断排查 | ping, traceroute, debug | 298 |

### 关键字查询

按命令名关键字查询：

```
bgp          → BGP相关命令
ospf         → OSPF相关命令
vlan         → VLAN相关命令
dhcp         → DHCP相关命令
acl          → ACL相关命令
qos          → QoS相关命令
show         → 显示类命令
```

### 字母排序查询

按命令首字母快速定位：

```
A, B, C... Z
```

---

## 📝 JSON数据结构

每条命令包含以下字段：

```json
{
  "name": "reload system",
  "syntax": "reload system force [＜reload-reason＞]",
  "mode": "特权模式",
  "level": 10,
  "description": "系统复位",
  "usage": "缺省情况下强制操作并不输入原因。",
  "examples": [
    "ZXR10#reload system force",
    "Proceed with reload system? [yes/no]:yes"
  ],
  "chapter": "产品管理",
  "section": "基本配置",
  "source_file": "sect2_1.html"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 命令名称 |
| syntax | string | 命令语法格式 |
| mode | string | 命令执行模式 |
| level | int | 权限级别 (1-10) |
| description | string | 功能描述 |
| usage | string | 使用说明 |
| examples | array | 配置范例 |
| chapter | string | 所属章节 |
| section | string | 所属小节 |
| source_file | string | 原始HTML文件 |

---

## 🔧 应用示例

### 场景：如何配置带宽限速？

**Step 1：创建流量模板**
```
全局配置模式:
traffic-profile 5M cir 5000 cbs 5000 pir 5000 pbs 5000
```

**Step 2：应用模板到接口**
```
接口配置模式:
interface xgei-1/6/1
qos traffic-shaping 5M
```

**Step 3：查看配置**
```
show qos traffic-profile name 5M
show qos traffic-shaping
```

---

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| HTML源文件 | 5241 个 |
| 命令总数 | 5211 条 |
| 章节数 | 13 个 |
| 场景覆盖 | 23 个 |
| JSON数据量 | ~12 MB |
| Markdown文档 | 7 个 |

---

## 🔍 查询示例

### 示例1：配置BGP邻居
```
Q: 如何配置BGP邻居？
A: 
   命令: router bgp <AS号>
   命令: neighbor <地址> remote-as <对端AS号>
   命令: neighbor <地址> activate
```

### 示例2：配置ACL
```
Q: 如何配置标准ACL？
A:
   命令: acl number <ID>
   命令: rule <规则ID> permit source <网段> <通配符>
   命令: rule <规则ID> deny source <网段> <通配符>
   命令: traffic-filter inbound acl <ID>
```

### 示例3：VLAN配置
```
Q: 如何创建VLAN？
A:
   命令: vlan <VLAN ID>
   命令: port default vlan <VLAN ID>
```

---

## 📋 命令模式说明

| 模式 | 提示符 | 说明 |
|------|--------|------|
| 用户模式 | `>` | 查看基本信息 |
| 特权模式 | `#` | 系统管理、调试 |
| 全局配置 | `(config)#` | 全局参数配置 |
| 接口配置 | `(config-if)#` | 接口参数配置 |
| 路由配置 | `(config-router)#` | 路由协议配置 |
| VLAN配置 | `(config-vlan)#` | VLAN参数配置 |

---

## ⚠️ 注意事项

1. **单位说明**
   - 带宽单位：kbps（千比特/秒）
   - 5M = 5000 kbps

2. **权限级别**
   - 级别1-3：普通用户
   - 级别10：管理员

3. **配置保存**
   - 完成后记得执行 `save` 保存配置

---

## 📅 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-28 | 1.0 | 初始版本，构建完成 |

---

## 📞 联系方式

- 设备厂商：中兴通讯股份有限公司
- 文档版本：V1.2.1
- 出版日期：2020-08-31

---

*本知识库由 AI 自动构建，源数据来自官方命令参考手册。*
