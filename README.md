# 电商自动化管理系统

基于 OpenClaw 框架的智能电商自动化系统，通过 7 个专业 Agent 实现从选品到上架的全流程自动化。

## 🚀 项目特性

- **完整的异步任务系统** - Celery + Redis 实现 6 种任务类型的异步处理
- **实时通信** - WebSocket 实时推送任务进度和系统通知
- **全异步架构** - FastAPI + aiomysql + async Redis，高并发性能
- **任务中心** - 任务创建、监控、重试、日志查看
- **数据分析** - 任务统计、产品分析、趋势图表
- **完整的权限管理** - 基于 RBAC 的三级权限（admin/operator/viewer）
- **固定布局** - 侧边栏和顶部导航固定，优化用户体验

## 📦 技术栈

### 前端
- React 18 + TypeScript 5
- Ant Design 5.12
- React Router 6.21
- Axios + WebSocket
- ECharts 5.4（数据可视化）
- Vite 5.0（代码分割 + Gzip/Brotli 压缩）

### 后端
- FastAPI 0.110 + Python 3.12
- SQLAlchemy 2.0（异步 ORM）+ Alembic
- Celery 5.6 + Redis 7.0（异步任务队列）
- MySQL 8.0（aiomysql 异步驱动）
- WebSocket（实时通信）
- JWT + Redis（认证与会话管理）

### 任务系统
- Celery Worker（异步任务执行）
- Redis（消息队列 + 结果存储）
- 6 种任务类型：选品分析、内容生成、图片生成、视频生成、内容审核、发布上架
- 实时进度推送（WebSocket）

### 监控
- Prometheus + Grafana
- AlertManager（12 条告警规则）
- Loguru（结构化日志）

## 📁 项目结构

```
ecommerce-automation/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── constants/      # 常量管理（MySQLTables, RedisKeys）
│   │   ├── middleware/     # 中间件（安全、日志）
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接池
│   │   └── redis_client.py # Redis 连接池
│   ├── sql/schema.sql      # 数据库初始化脚本
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量模板
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API 接口
│   │   ├── layouts/       # 布局组件
│   │   ├── pages/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   ├── package.json       # 依赖配置
│   └── vite.config.ts     # 构建配置
├── docs/design/           # 设计文档（20 个）
│   ├── architecture/      # 架构设计
│   ├── features/          # 功能模块
│   ├── ui-ux/            # UI/UX 设计
│   ├── database/         # 数据库设计
│   ├── implementation/   # 实施计划
│   └── deployment/       # 部署方案
├── monitoring/           # 监控配置
│   ├── prometheus.yml    # Prometheus 配置
│   ├── alerts.yml        # 告警规则
│   └── alertmanager.yml  # 告警管理
└── nginx/               # Nginx 配置
    └── nginx.conf       # 反向代理配置
```

## 🛠️ 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/xirfly/ecommerce-automation.git
cd ecommerce-automation
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库和 Redis 配置

# 初始化数据库
mysql -u root -p < sql/schema.sql

# 启动后端服务
python run.py

# 启动 Celery Worker（新终端）
python start_celery.py
```

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local，填写 API 地址

# 启动开发服务器
npm run dev
```

### 4. 访问系统

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

**默认账号：** admin / admin123

## 📖 文档

### 设计文档
- [系统架构总览](docs/design/architecture/01-system-architecture.md)
- [Agent 编排设计](docs/design/architecture/02-agent-orchestration.md)
- [多渠道接入设计](docs/design/architecture/03-multi-channel.md)
- [产品管理模块](docs/design/features/01-product-management.md)
- [任务调度模块](docs/design/features/02-task-scheduling.md)
- [数据分析模块](docs/design/features/03-data-analytics.md)
- [UI/UX 设计规范](docs/design/ui-ux/01-design-principles.md)
- [数据库设计](docs/design/database/01-data-model.md)
- [开发环境部署](docs/design/deployment/01-dev-environment.md)
- [生产环境部署](docs/design/deployment/02-prod-environment.md)
- [优化建议](docs/design/OPTIMIZATION.md)

### 开发文档
- [API 开发文档](docs/development/api-documentation.md)
- [后端代码结构](docs/development/backend-structure.md)

## 🎯 开发计划

### 一期（MVP - 已完成）✅
- [x] 基础设施搭建
- [x] 后端核心 API（产品、任务、分析）
- [x] 前端基础框架（React + Ant Design）
- [x] Celery 异步任务系统
- [x] WebSocket 实时通信
- [x] 任务中心完整功能
- [x] 数据分析页面
- [x] 用户认证与权限管理

### 二期（增强 - 进行中）
- [ ] 对接真实 AI 服务（Midjourney/Runway/GPT-4）
- [ ] 多平台适配（淘宝/京东/拼多多）
- [ ] 渠道扩展（飞书/Telegram/企业微信）
- [ ] Agent 编排系统

### 三期（完善 - 规划中）
- [ ] 监控告警完善（Prometheus + Grafana）
- [ ] 性能优化（缓存、CDN）
- [ ] 自动化测试（单元测试 + 集成测试）
- [ ] 文档完善

## 🔒 安全特性

- JWT 认证 + Redis 会话管理
- CORS 跨域配置
- API 速率限制（60 次/分钟）
- SQL 注入防护
- 安全响应头（HSTS、X-Frame-Options）
- 敏感信息脱敏

## 📊 性能优化

- 数据库连接池（pool_size=20）
- Redis 连接池（max_connections=50）
- 前端代码分割（React/Ant Design/ECharts 独立 chunk）
- Gzip + Brotli 双重压缩
- 静态资源缓存（1 年）
- 懒加载路由

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 作者

- 设计与开发：Claude Opus 4.6
- 项目维护：[@xirfly](https://github.com/xirfly)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
