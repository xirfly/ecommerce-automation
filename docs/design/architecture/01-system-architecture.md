# 系统架构总览

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

设计一个基于OpenClaw Agent框架的电商自动化系统，实现：
- 7个专业Agent协作完成选品到上架的全流程自动化
- 支持Web后台和飞书等多渠道交互
- 模块化、可扩展的架构设计
- 高性能、高可用的生产级系统

---

## 2. 整体架构

### 2.1 架构分层

```
┌─────────────────────────────────────────────────────────┐
│                    渠道接入层                            │
│  Web后台(React) | 飞书 | [可配置]其他渠道               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  OpenClaw Gateway                        │
│  渠道路由 | 会话管理 | 并发控制 | 权限验证               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Agent编排层                           │
│  7个专业Agent：选品/图片/视频/文案/详情页/上架/分析     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   业务逻辑层                             │
│  FastAPI | Celery任务队列 | 业务规则引擎                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      数据层                              │
│  MySQL(业务数据) | Redis(缓存/队列/会话)                │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 技术栈 | 职责 |
|------|--------|------|
| **Web前端** | React + Ant Design Pro + TypeScript | 可视化操作界面 |
| **OpenClaw Gateway** | Node.js | 多渠道接入、Agent调度 |
| **业务后端** | FastAPI + SQLAlchemy | RESTful API、业务逻辑 |
| **任务队列** | Celery + Redis | 异步任务调度 |
| **数据库** | MySQL 8.0 | 持久化存储 |
| **缓存** | Redis 7.0 | 缓存、队列、会话 |

---

## 3. 技术栈选型

### 3.1 前端技术栈

**核心框架：** React 18 + TypeScript 5

**UI组件库：** Ant Design Pro 6
- 理由：企业级后台组件库，开箱即用
- 包含：表格、表单、图表、布局等完整组件

**状态管理：** React Context + Hooks
- 理由：项目规模适中，不需要Redux的复杂度
- 使用场景：用户信息、全局配置

**数据请求：** Axios + SWR
- Axios：HTTP客户端
- SWR：数据缓存和自动重新验证

**图表库：** Apache ECharts
- 理由：功能强大，中文文档完善
- 使用场景：仪表盘、数据分析页面

### 3.2 后端技术栈

**核心框架：** FastAPI 0.110+
- 理由：高性能、异步支持、自动生成API文档
- 特性：类型提示、依赖注入、WebSocket支持

**ORM：** SQLAlchemy 2.0
- 理由：成熟稳定，支持复杂查询
- 使用：异步模式（asyncio + aiomysql）

**任务队列：** Celery 5.3 + Redis
- 理由：成熟的分布式任务队列
- 使用场景：Agent任务执行、定时任务

**认证：** JWT (python-jose)
- 理由：无状态认证，适合前后端分离
- 存储：Token存储在Redis，支持撤销

### 3.3 Agent框架

**OpenClaw Gateway**
- 版本：最新稳定版
- 配置：通过`openclaw.json`管理
- 扩展：支持自定义Plugin和Hook

### 3.4 数据库

**MySQL 8.0**
- 存储引擎：InnoDB
- 字符集：utf8mb4
- 使用场景：业务数据、Agent记忆（JSON字段）

**Redis 7.0**
- 持久化：AOF + RDB
- 使用场景：
  - 缓存：热点数据（TTL 5-10分钟）
  - 队列：Celery任务队列
  - 会话：用户会话、OpenClaw会话
  - 限流：API限流计数器

---

## 4. 数据流设计

### 4.1 产品全流程数据流

```
用户操作（Web/飞书）
    ↓
FastAPI接收请求
    ↓
创建Celery任务
    ↓
OpenClaw Gateway调度Agent
    ↓
Agent 1: 选品分析
    ↓ (输出：选品报告)
Agent 2/3/4: 并行生成内容
    ↓ (输出：图片/视频/文案)
Agent 5: 制作详情页
    ↓ (输出：详情页HTML)
Agent 6: 发布到平台
    ↓ (输出：产品链接)
结果存储到MySQL
    ↓
WebSocket推送给前端
    ↓
用户看到结果
```

### 4.2 多渠道消息流

```
用户消息（飞书/Telegram等）
    ↓
OpenClaw Gateway接收
    ↓
根据渠道配置路由到对应Agent
    ↓
Agent处理并返回结果
    ↓
Gateway格式化响应
    ↓
发送回用户渠道
```

---

## 5. 核心接口定义

### 5.1 前后端接口

**基础URL：** `http://localhost:8000/api/v1`

**认证方式：** Bearer Token (JWT)

**核心API：**

```
# 产品管理
POST   /products              创建产品
GET    /products              获取产品列表
GET    /products/{id}         获取产品详情
PUT    /products/{id}         更新产品
DELETE /products/{id}         删除产品

# 任务管理
POST   /tasks/analyze         触发选品分析
POST   /tasks/generate        触发内容生成
POST   /tasks/publish         触发产品发布
GET    /tasks/{id}            查询任务状态
GET    /tasks                 获取任务列表

# 渠道配置
POST   /channels              添加渠道
GET    /channels              获取渠道列表
PUT    /channels/{id}         更新渠道配置
DELETE /channels/{id}         删除渠道

# 数据分析
GET    /analytics/dashboard   仪表盘数据
GET    /analytics/reports     生成报表
```

### 5.2 OpenClaw Gateway接口

**配置文件：** `~/.openclaw/openclaw.json`

**核心配置：**
```json
{
  "agents": {
    "list": [
      {
        "name": "product-analyzer",
        "model": { "primary": "claude-opus-4" },
        "workspace": "~/.openclaw/workspace/analyzer"
      },
      // ... 其他6个Agent
    ]
  },
  "bindings": [
    {
      "channel": "feishu",
      "agent": "product-analyzer"
    }
  ]
}
```

---

## 6. 依赖关系

### 6.1 模块依赖

```
Web前端
  ↓ (HTTP API)
FastAPI后端
  ↓ (任务调度)
Celery Worker
  ↓ (Agent调用)
OpenClaw Gateway
  ↓ (数据存储)
MySQL + Redis
```

### 6.2 外部依赖

| 依赖 | 用途 | 是否必需 |
|------|------|----------|
| OpenClaw Gateway | Agent编排 | ✅ 必需 |
| MySQL | 数据存储 | ✅ 必需 |
| Redis | 缓存/队列 | ✅ 必需 |
| AI服务API | 内容生成 | ❌ 一期使用模拟数据 |
| 电商平台API | 产品发布 | ❌ 一期使用Mock |

---

## 7. 非功能性需求

### 7.1 性能指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| API响应时间 | P95 < 200ms | Prometheus监控 |
| 任务执行时间 | 平均 < 10分钟 | 任务日志统计 |
| 并发支持 | ≥ 100 QPS | 压力测试 |
| 系统可用性 | ≥ 99.5% | 监控告警 |

### 7.2 安全要求

- **认证：** JWT Token，有效期24小时
- **授权：** RBAC权限控制
- **数据加密：** HTTPS传输，敏感数据加密存储
- **SQL注入防护：** 使用ORM参数化查询
- **XSS防护：** 前端输入过滤，后端输出转义

### 7.3 可扩展性

- **水平扩展：** FastAPI无状态，支持多实例部署
- **任务队列：** Celery支持分布式Worker
- **数据库：** MySQL支持主从复制、读写分离
- **缓存：** Redis支持集群模式

---

## 8. 实施要点

### 8.1 开发顺序

1. **基础设施** - 数据库、Redis、OpenClaw Gateway搭建
2. **后端API** - FastAPI核心接口开发
3. **Agent编排** - 7个Agent逻辑实现
4. **前端页面** - React页面开发
5. **多渠道接入** - 飞书集成
6. **测试优化** - 性能测试、安全加固

### 8.2 关键风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| OpenClaw不稳定 | 高 | 深入研究文档，准备降级方案 |
| Agent编排复杂 | 中 | 先实现串行，再优化并行 |
| 性能瓶颈 | 中 | 提前做压力测试，优化热点 |

### 8.3 技术债务管理

- **代码规范：** 使用ESLint、Black格式化
- **单元测试：** 核心逻辑覆盖率 > 80%
- **文档更新：** 代码变更同步更新文档
- **技术评审：** 关键模块代码评审

---

## 9. 相关文档

- [Agent编排设计](02-agent-orchestration.md) - 7个Agent的详细设计
- [多渠道接入设计](03-multi-channel.md) - 渠道配置和路由规则
- [数据模型设计](../database/01-data-model.md) - 数据库表结构
- [任务拆分与优先级](../implementation/01-task-breakdown.md) - 开发任务列表
