"""
生产级部署方案 — Agent 系统上线指南
====================================
目标：理解从 Demo 到 Production 的关键差距和解决方案

核心话题：
- 架构设计
- Docker 部署
- 成本控制
- 监控告警
- 安全防护
"""

# ============ Demo vs Production ============

COMPARISON = """
Demo 到 Production 的差距:

维度          Demo                    Production
─────────────────────────────────────────────────────
运行环境      本地开发机              Docker/K8s 容器化
用户规模      单用户                  并发处理 + 队列
模型调用      直连 OpenAI             LLM 网关(路由/限流/缓存)
数据存储      本地文件                数据库 + 向量DB + Redis
监控          print()                 Prometheus + Grafana
密钥管理      .env 文件               Vault / KMS 密钥管理
错误处理      try-except              重试 + 降级 + 熔断
缓存          无                      Redis 多级缓存
部署          手动启动                CI/CD 自动化
日志          终端输出                 结构化日志 + 链路追踪
"""


# ============ 系统架构 ============

ARCHITECTURE = """
生产级 Agent 系统架构:

用户 → CDN → API 网关(限流/认证/路由)
                  ↓
           Agent 服务集群 (×N 实例)
                  ↓
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
  工具服务      向量数据库      LLM 网关
  (沙箱隔离)    (Milvus)     (模型路由)
                  ↓          ↓
              向量存储    模型提供商
              (S3/OSS)   (OpenAI/Ollama)
                  ↓
              缓存层 (Redis)
                  ↓
              数据库 (PostgreSQL)
                  ↓
              消息队列 (RabbitMQ)
                  ↓
              监控 (Prometheus + Grafana)
"""


# ============ Docker 部署 ============

DOCKERFILE = """
# Dockerfile — Agent 服务部署
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 启动
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

DOCKER_COMPOSE = """
# docker-compose.yml — 完整部署
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@db:5432/agent
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on:
      - redis
      - db
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: agent
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pg_data:/var/lib/postgresql/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"

volumes:
  redis_data:
  pg_data:
"""


# ============ 成本控制 ============

COST_CONTROL = """
LLM 成本控制策略:

1. 模型分级
   - 简单问题 → 小模型 (GPT-4o-mini, $0.15/1M tokens)
   - 复杂问题 → 大模型 (GPT-4o, $2.5/1M tokens)
   - 节省 94% 成本

2. 缓存优先
   - 语义相似度 > 0.95 → 直接返回缓存
   - 相同问题不再调用 LLM
   - 节省 30-50% 调用

3. Prompt 压缩
   - 去除冗余描述
   - 历史消息压缩为摘要
   - 节省 20-40% tokens

4. 流式 + 流控
   - 流式响应减少等待时间
   - 请求队列控制并发
   - 限流防止超支

5. 预算告警
   - 日预算上限
   - 实时监控消费
   - 超支自动降级
"""


# ============ 安全防护 ============

SECURITY = """
Agent 安全防护检查清单:

输入安全:
  ✅ 输入长度限制 (防 DoS)
  ✅ Prompt 注入检测
  ✅ 敏感信息过滤 (PII 脱敏)
  ✅ 内容安全审核

工具安全:
  ✅ 工具执行沙箱 (Docker/容器)
  ✅ 工具调用白名单
  ✅ 超时限制
  ✅ 资源限制 (CPU/内存/网络)

输出安全:
  ✅ 输出内容审核
  ✅ 敏感信息过滤
  ✅ Token 用量限制
  ✅ 幻觉检测

系统安全:
  ✅ API 密钥环境变量注入
  ✅ 最小权限原则
  ✅ HTTPS 强制
  ✅ 请求签名验证
"""


# ============ 监控体系 ============

MONITORING = """
监控指标体系:

基础指标:
  - QPS (每秒请求数)
  - 延迟 P50/P95/P99
  - 错误率
  - 可用性 (SLA)

LLM 指标:
  - 调用次数/频率
  - Token 消耗 (输入/输出)
  - 延迟 (首 token / 总耗时)
  - 费用累计
  - 模型可用性

Agent 指标:
  - 任务完成率
  - 平均推理步数
  - 工具调用分布
  - 用户满意度

告警规则:
  - 错误率 > 5% → P1 告警
  - P99 延迟 > 10s → P2 告警
  - 日费用超预算 → P1 告警
  - 模型不可用 → P0 告警
"""


# ============ 部署检查清单 ============

CHECKLIST = """
上线前检查清单:

环境:
  ✅ Docker 镜像构建成功
  ✅ 环境变量配置完整
  ✅ 密钥通过 Vault/KMS 注入
  ✅ 数据库迁移完成
  ✅ 向量库初始化完成

功能:
  ✅ 所有测试用例通过
  ✅ 压力测试达标 (100 QPS)
  ✅ 故障恢复测试通过
  ✅ 数据备份策略确认

监控:
  ✅ Prometheus 采集正常
  ✅ Grafana 仪表盘就绪
  ✅ 告警规则配置
  ✅ 日志收集就绪

安全:
  ✅ 渗透测试通过
  ✅ 数据加密验证
  ✅ 访问控制确认
  ✅ 审计日志开启
"""


# ============ 演示 ============

if __name__ == '__main__':
    print("=" * 60)
    print("生产级 Agent 部署方案")
    print("=" * 60)
    
    print(COMPARISON)
    print(ARCHITECTURE)
    print(COST_CONTROL)
    print(SECURITY)
    print(MONITORING)
    print(CHECKLIST)
    
    print("\n" + "=" * 60)
    print("Dockerfile 示例")
    print("=" * 60)
    print(DOCKERFILE)
    
    print("\n" + "=" * 60)
    print("docker-compose.yml 示例")
    print("=" * 60)
    print(DOCKER_COMPOSE)
