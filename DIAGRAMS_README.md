# SmartTerm Web UI - 系统架构与功能图

本文档包含了SmartTerm Web UI项目的各种架构图和功能图。

## 1. 系统架构流程图
![系统架构流程图](architecture_flow.md)

此图展示了SmartTerm Web UI的整体架构流程，包括：
- 用户通过Web界面访问各个功能模块
- 前端与后端服务的交互
- 后端服务与SmartTerm核心组件的集成
- 远程服务器的连接

## 2. Web功能架构图
![Web功能架构图](web_function_diagram.md)

此图详细展示了Web界面的功能架构：
- 前端各功能模块的组织
- 后端API和WebSocket服务
- 与SmartTerm核心功能的关联

## 3. 系统架构图
![系统架构图](system_architecture.md)

此图描绘了完整的系统架构：
- 客户端层：浏览器和React前端
- 传输层：网络协议
- 服务层：FastAPI后端
- 业务逻辑层：SmartTerm服务
- 数据层：SQLite数据库
- 外部资源：远程服务器
- AI组件：智能功能模块

## 4. 模块关系图
![模块关系图](module_relationship.md)

此图显示了前端和后端各模块之间的依赖关系：
- 前端组件之间的关系
- 后端模块的组织结构
- 与SmartTerm核心模块的连接

## 功能特点

### 前端功能
- 终端仿真器（xterm.js）
- AI助手面板
- 连接管理器
- 会话管理器
- 设置面板

### 后端服务
- REST API接口
- WebSocket终端连接
- 与原生SmartTerm组件的集成
- 数据持久化

### 核心功能
- AI驱动的自然语言转换
- SSH/Telnet连接管理
- 会话状态跟踪
- 安全检查

这些图表全面展示了SmartTerm Web UI项目的架构设计和功能组织。