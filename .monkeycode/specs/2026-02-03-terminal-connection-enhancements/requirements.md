# 需求文档

## 引言

本文档定义了 smart_term 智能终端工具的终端连接增强功能需求，包括远程终端连接（SSH/Telnet）和基于产品类别的命令历史管理功能。

## 术语表

- **System**: smart_term 智能终端工具系统
- **User**: 使用 smart_term 的终端用户
- **Remote Terminal**: 通过网络连接的远程主机终端（SSH 或 Telnet）
- **Interactive Mode**: 用户直接与远程终端交互的模式
- **AI-Driven Mode**: 通过 AI 理解用户意图并与远程终端交互的模式
- **Command Category**: 命令的类别分类，按设备产品类型区分（如网关_海思、网关_中兴微、OLT_zxic、Olt_烽火）
- **Connection Session**: 一次完整的远程终端连接会话

## 需求

### 需求 1: 远程终端连接

**用户故事**: 作为系统管理员，我希望能够通过 smart_term 连接到远程主机（SSH/Telnet），以便在一个统一的界面上管理多台服务器。

#### 验收标准

1. WHEN 用户发起远程连接请求，System SHALL 验证连接参数（主机地址、端口、认证信息）的有效性
2. WHEN 用户指定端口为 23 或明确指定 Telnet 协议，System SHALL 使用 Telnet 协议建立与远程主机的连接
3. WHEN 用户未指定协议且端口不是 23，System SHALL 使用 SSH 协议建立与远程主机的加密连接
4. WHEN SSH 连接参数有效，System SHALL 让用户手动选择认证方式（密码或密钥）并建立连接
5. WHILE 远程连接已建立，System SHALL 在当前终端界面中显示远程主机的命令提示符
6. WHEN 用户在交互模式下输入命令，System SHALL 将命令直接转发到远程主机并返回执行结果
7. WHEN 用户断开远程连接，System SHALL 关闭与远程主机的连接并返回本地终端模式
8. IF 远程连接失败（认证失败、主机不可达等），System SHALL 显示详细的错误信息和故障排查建议

### 需求 2: 连接管理

**用户故事**: 作为需要管理多台服务器的用户，我希望能够保存和管理多个远程连接配置，以便快速连接到常用主机。

#### 验收标准

1. WHEN 用户保存远程连接配置，System SHALL 存储连接配置信息（主机名、地址、端口、协议类型、认证方式）
2. WHEN 用户创建 SSH 连接配置，System SHALL 提供选项让用户手动选择认证方式（密码或密钥）
3. WHEN 用户查看已保存的连接列表，System SHALL 显示所有已保存连接的名称和基本信息
4. WHEN 用户选择已保存的连接发起连接，System SHALL 使用存储的配置自动建立连接
5. WHEN 用户编辑连接配置，System SHALL 更新存储的配置信息
6. WHEN 用户删除连接配置，System SHALL 从存储中移除该配置
7. WHILE 远程连接会话正在进行，System SHALL 在状态栏显示当前连接的主机信息

### 需求 3: AI 驱动远程交互

**用户故事**: 作为不熟悉远程命令的用户，我希望能够使用自然语言与远程主机交互，让 AI 帮我理解和执行命令。

#### 验收标准

1. WHEN 用户在 AI 模式下输入自然语言描述，System SHALL 通过 AI 服务理解用户意图并转换为可执行的命令
2. WHEN AI 生成命令建议，System SHALL 在执行前显示命令预览并等待用户确认
3. WHEN 用户确认执行命令，System SHALL 将命令发送到远程主机并返回执行结果
4. WHILE AI 处理自然语言请求时，System SHALL 显示处理状态指示器
5. WHEN AI 生成的命令执行失败，System SHALL 分析失败原因并提供建议的修复方案
6. WHEN AI 模式处于激活状态，System SHALL 在提示符中明确标识当前为 AI 模式
7. WHEN 用户切换交互模式和 AI 模式，System SHALL 保存当前会话状态并平滑过渡

### 需求 4: 模式切换与协作

**用户故事**: 作为需要在手动操作和 AI 辅助之间灵活切换的用户，我希望能够在同一个连接会话中切换交互模式，以便根据任务需要选择最合适的方式。

#### 验收标准

1. WHEN 用户切换到交互模式，System SHALL 直接转发用户输入的命令到远程主机
2. WHEN 用户切换到 AI 模式，System SHALL 将用户输入视为自然语言并通过 AI 处理
3. WHILE 用户在任一模式下执行命令，System SHALL 将执行结果添加到当前会话的历史记录
4. WHEN 用户请求查看会话历史，System SHALL 显示当前连接会话中的所有命令和结果（无论来源模式）
5. IF 用户在 AI 模式下直接输入可执行命令（不加自然语言描述），System SHALL 识别并直接执行该命令

### 需求 5: 产品类别化的命令历史

**用户故事**: 作为需要追踪和管理不同设备类型操作的用户，我希望命令历史能够按设备产品类别分类，以便快速查找特定设备类型的命令。

#### 验收标准

1. WHEN System 记录命令历史，System SHALL 根据连接配置关联的设备产品类型自动标记命令类别（网关_海思、网关_中兴微、OLT_zxic、Olt_烽火）
2. WHEN 连接配置未指定设备产品类型，System SHALL 将命令归类为"未分类"类别
3. WHEN 用户手动标记命令的设备产品类别，System SHALL 更新该命令的类别标识
4. WHEN 用户按设备产品类别筛选历史命令，System SHALL 显示属于所选设备类别的所有命令
5. WHEN 用户查看命令历史，System SHALL 按设备产品类别分组显示命令，每组显示类别名称和命令数量
6. WHILE System 自动分类命令时，System SHALL 基于连接配置中保存的设备产品类型信息进行判断
7. WHEN 用户添加自定义设备产品类别，System SHALL 保存新类别并允许后续命令使用该类别

### 需求 6: 设备产品类别管理

**用户故事**: 作为需要管理多种设备类型的用户，我希望能够定义和管理设备产品类别，并为每个连接配置关联对应的设备类型。

#### 验收标准

1. WHEN System 定义设备产品类别，System SHALL 支持创建类别并关联到连接配置
2. WHEN 用户查看设备产品类别列表，System SHALL 显示所有已定义的类别及其包含的连接数量
3. WHEN 用户创建或编辑连接配置，System SHALL 提供选项选择或创建设备产品类别
4. WHEN 用户选择设备产品类别，System SHALL 显示该类别下的所有连接配置
5. WHEN 用户按设备产品类别搜索命令，System SHALL 支持在指定设备类别范围内搜索
6. WHILE System 维护设备产品类别，System SHALL 确保类别与连接配置的引用完整性和一致性

### 需求 7: 历史查询与统计分析

**用户故事**: 作为需要分析命令使用情况的用户，我希望能够按产品类别查询和统计历史命令，以便了解各类操作的使用频率和趋势。

#### 验收标准

1. WHEN 用户请求查看某个类别的命令统计，System SHALL 显示该类别的命令总数、使用频率和最近使用时间
2. WHEN 用户请求查看所有类别的统计概览，System SHALL 显示每个类别的命令数量和占比
3. WHEN 用户按时间范围和类别组合筛选命令，System SHALL 返回符合两个条件的命令列表
4. WHEN 用户搜索命令关键词，System SHALL 在搜索结果中标注每条命令所属的类别
5. WHILE System 统计命令使用情况时，System SHALL 考虑命令的执行成功率和执行时长
6. WHEN 用户导出历史命令，System SHALL 支持按类别分组导出为 JSON 或 CSV 格式

### 需求 8: 远程连接安全

**用户故事**: 作为注重安全的系统管理员，我希望远程连接具有完善的安全机制，以保护敏感信息和防止未授权访问。

#### 验收标准

1. WHEN 用户使用 SSH 连接，System SHALL 支持密码认证和密钥认证两种方式
2. WHEN 用户首次连接到未知 SSH 主机，System SHALL 显示主机指纹并等待用户确认
3. WHEN 用户保存连接配置中的密码，System SHALL 将密码加密存储在本地配置文件中
4. WHEN Telnet 连接正在使用，System SHALL 在状态栏显示安全警告（Telnet 为明文传输）
5. WHEN 检测到 SSH 会话超时，System SHALL 自动断开连接并通知用户
6. IF 检测到连接异常断开，System SHALL 记录断开原因并在用户下次连接时显示警告信息
7. WHILE 用户输入密码进行认证，System SHALL 在终端界面中隐藏密码输入内容

## 非功能性需求

### 性能

1. WHEN 用户发起远程连接请求，System SHALL 在 5 秒内建立连接或返回错误
2. WHEN 用户在交互模式下执行命令，System SHALL 在 1 秒内显示命令执行结果
3. WHEN AI 模式处理自然语言请求，System SHALL 在 10 秒内返回命令建议或错误信息

### 可用性

1. WHEN 用户在远程连接会话中，System SHALL 清晰标识当前是本地终端还是远程终端
2. WHEN 用户在任一模式下操作，System SHALL 提供清晰的模式切换提示
3. WHILE System 显示命令历史，System SHALL 使用颜色或图标区分不同的产品类别

### 可维护性

1. WHEN 需要添加新的远程连接协议，System SHALL 提供可扩展的连接管理接口
2. WHEN 需要扩展产品类别定义，System SHALL 支持通过配置文件自定义类别规则
3. WHILE System 维护命令历史，System SHALL 定期清理过期或过多的历史记录（可配置保留策略）
