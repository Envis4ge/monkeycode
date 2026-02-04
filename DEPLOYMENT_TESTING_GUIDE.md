# SmartTerm - 部署和测试文档

## 1. 系统要求

### 硬件要求
- CPU: 任何支持Python 3.8+的处理器
- 内存: 至少 512MB RAM（推荐 1GB+）
- 存储: 至少 100MB 可用空间

### 软件要求
- Python 3.8 或更高版本
- pip (Python包管理器)
- 操作系统: Linux/macOS/Windows

## 2. 依赖安装

### 安装Python依赖
```bash
# 安装项目依赖
pip install -r requirements.txt

# 或者手动安装
pip install paramiko cryptography
```

### 系统依赖 (Linux/macOS)
- OpenSSL (通常已预装)
- SSH客户端 (用于SSH连接测试)

## 3. 快速部署

### 3.1 克隆或下载项目
```bash
# 克隆项目 (如果从版本控制系统)
git clone <repository-url>
cd <project-directory>

# 或直接下载源代码
```

### 3.2 安装依赖
```bash
pip install -r requirements.txt
```

### 3.3 验证安装
```bash
# 检查主程序是否可以运行
python -m src.main --help
```

## 4. 功能测试

### 4.1 基础功能测试

#### 测试命令行界面
```bash
# 查看帮助信息
python -m src.main --help

# 查看特定命令帮助
python -m src.main connect --help
python -m src.main add --help
python -m src.main ai --help
```

#### 测试模块导入
```bash
# 运行综合测试脚本
python comprehensive_test.py
```

### 4.2 连接功能测试

#### 测试连接功能（需有测试服务器）
```bash
# 添加测试配置
python -m src.main add --name "test-server" --host localhost --port 22 --username testuser --password testpass

# 列出配置
python -m src.main list

# 尝试连接（需要有效的SSH服务器）
python -m src.main connect --name "test-server"
```

#### 测试会话功能
```bash
# 在连接状态下
python -m src.main session list
python -m src.main session history
```

### 4.3 AI功能测试

#### 测试AI命令转换
```bash
# 运行专门的AI功能测试
python test_ai_functionality.py

# 或运行综合测试
python comprehensive_test.py
```

## 5. 详细测试流程

### 5.1 模块级测试

#### 远程连接模块测试
```python
# 测试SSH客户端
from src.remote.ssh_client import SSHClient
# 验证SSH客户端功能

# 测试Telnet客户端
from src.remote.telnet_client import TelnetClient
# 验证Telnet客户端功能

# 测试连接管理器
from src.remote.connection_manager import ConnectionManager
# 验证连接管理功能
```

#### AI模块测试
```python
# 测试AI命令转换器
from src.ai.command_converter import convert_natural_language_to_command
# 验证自然语言到命令的转换功能
```

### 5.2 集成测试

#### 交互式功能测试
```bash
# 启动交互式Shell模式
python -m src.main shell

# 启动AI交互模式
python -m src.main ai
```

## 6. 功能验证清单

### 6.1 核心功能验证

- [ ] 命令行界面正常启动
- [ ] 连接配置管理功能（增删改查）
- [ ] SSH连接功能（密码认证）
- [ ] SSH连接功能（密钥认证）
- [ ] Telnet连接功能
- [ ] 交互式Shell模式
- [ ] 命令历史记录功能
- [ ] 命令自动补全功能
- [ ] 会话管理功能
- [ ] AI驱动的自然语言转换功能
- [ ] 设备产品类别管理
- [ ] 安全检查功能
- [ ] 数据持久化功能

### 6.2 高级功能验证

- [ ] 基于设备类别的命令优化
- [ ] 命令执行确认机制
- [ ] 错误处理和恢复
- [ ] 命令历史文件持久化
- [ ] 多会话并发管理

## 7. 常见问题排查

### 7.1 连接问题
```bash
# 检查网络连接
ping <target-host>

# 检查SSH服务
telnet <target-host> 22

# 检查防火墙设置
```

### 7.2 依赖问题
```bash
# 重新安装依赖
pip uninstall paramiko cryptography
pip install paramiko cryptography
```

### 7.3 权限问题
- 确保有执行Python脚本的权限
- 检查配置文件和数据库的读写权限
- 验证SSH密钥文件的权限设置

## 8. 性能基准测试

### 8.1 连接性能测试
- SSH连接建立时间 < 5秒
- 命令执行响应时间 < 2秒
- 会话切换时间 < 1秒

### 8.2 AI转换性能测试
- 自然语言到命令转换 < 100毫秒
- 命令解释准确率 > 80%

## 9. 生产环境部署建议

### 9.1 安全建议
- 使用SSH密钥认证而非密码认证
- 定期更新SSH密钥
- 限制对系统的访问权限
- 不要在生产环境中暴露不必要的端口

### 9.2 监控建议
- 监控连接成功率
- 记录命令执行日志
- 跟踪会话活动
- 监控AI转换准确率

## 10. 维护和升级

### 10.1 日常维护
- 定期备份配置数据库
- 清理过期的会话日志
- 更新依赖包版本

### 10.2 升级流程
1. 备份现有配置和数据
2. 下载新版代码
3. 安装新依赖
4. 测试功能兼容性
5. 逐步切换到新版本

## 11. 故障排除

### 11.1 启动故障
- 检查Python版本兼容性
- 验证依赖包安装
- 确认模块路径设置

### 11.2 连接故障
- 验证目标服务器可达性
- 检查认证凭据
- 确认SSH/Telnet服务运行状态

---

**注意**: 本工具仅供授权环境内的合法用途，使用时请遵守相关法律法规和目标系统的使用政策。