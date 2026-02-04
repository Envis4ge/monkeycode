```mermaid
graph TB
    subgraph "SmartTerm Web UI"
        A[Web界面入口] --> B[导航栏]
        A --> C[主内容区]

        B --> B1[终端]
        B --> B2[AI助手]
        B --> B3[连接管理]
        B --> B4[会话管理]
        B --> B5[设置]

        C --> D[终端仿真器]
        C --> E[AI交互面板]
        C --> F[连接配置表单]
        C --> G[会话管理表]

        D --> D1[xterm.js终端]
        D --> D2[WebSocket连接]

        E --> E1[自然语言输入]
        E --> E2[AI命令转换]
        E --> E3[执行结果展示]

        F --> F1[添加连接]
        F --> F2[编辑连接]
        F --> F3[删除连接]

        G --> G1[当前会话]
        G --> G2[历史会话]
    end

    subgraph "后端服务"
        H[FastAPI后端]
        H --> I[REST API]
        H --> J[WebSocket服务]

        I --> I1[/api/configs]
        I --> I2[/api/connect]
        I --> I3[/api/command]
        I --> I4[/api/session]

        J --> J1[/ws/terminal]
    end

    subgraph "SmartTerm核心"
        K[连接管理器]
        L[AI命令转换器]
        M[数据库模块]
        N[SSH/Telnet客户端]
    end

    D2 --> J1
    E2 --> I3
    F1 --> I1
    G1 --> I4

    I1 -.-> M
    I2 -.-> K
    I3 -.-> L
    J1 -.-> N

    style A fill:#c8e6c9
    style H fill:#e3f2fd
    style K fill:#fff3e0
    style L fill:#fce4ec
    style M fill:#f3e5f5
    style N fill:#e8f5e8
```