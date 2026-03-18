# 后端代码结构说明

## 目录结构

```
backend/
├── app/
│   ├── core/                    # 核心基础设施
│   │   ├── __init__.py
│   │   ├── config.py           # 应用配置
│   │   ├── database.py         # 数据库连接池
│   │   ├── redis_client.py     # Redis 连接池
│   │   ├── logging_config.py   # 日志配置
│   │   └── health_check.py     # 启动前健康检查
│   │
│   ├── workers/                 # Celery 异步任务
│   │   ├── __init__.py
│   │   ├── celery_app.py       # Celery 应用配置
│   │   ├── tasks.py            # 任务定义
│   │   └── startup_tasks.py    # 启动时任务处理
│   │
│   ├── websocket/               # WebSocket 实时通信
│   │   ├── __init__.py
│   │   ├── websocket_manager.py # 连接管理器
│   │   └── routes.py           # WebSocket 路由
│   │
│   ├── api/                     # REST API 路由
│   │   ├── v1/                 # API v1 版本
│   │   │   ├── auth.py         # 认证接口
│   │   │   ├── products.py     # 产品管理
│   │   │   ├── tasks.py        # 任务管理
│   │   │   └── analytics.py    # 数据分析
│   │   ├── channels.py         # 多渠道 Webhook
│   │   └── health.py           # 健康检查端点
│   │
│   ├── channels/                # 多渠道接入
│   │   ├── base.py             # 渠道基类
│   │   ├── lark.py             # 飞书渠道
│   │   └── manager.py          # 渠道管理器
│   │
│   ├── services/                # 业务服务
│   │   └── ai_service.py       # AI 服务抽象层
│   │
│   ├── models/                  # 数据模型
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── task.py
│   │
│   ├── schemas/                 # Pydantic 模式
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── task.py
│   │   └── common.py
│   │
│   ├── dependencies/            # FastAPI 依赖项
│   │   └── auth.py             # 认证依赖
│   │
│   ├── middleware/              # 中间件
│   │   └── security.py         # 安全中间件
│   │
│   ├── utils/                   # 工具函数
│   │   └── auth.py             # 认证工具
│   │
│   ├── constants/               # 常量定义
│   │   ├── mysql_tables.py
│   │   └── redis_keys.py
│   │
│   └── main.py                  # FastAPI 应用入口
│
├── run.py                       # 启动脚本
├── start_celery.py              # Celery Worker 启动脚本
└── .env                         # 环境变量配置

```

## 模块说明

### 1. core/ - 核心基础设施
存放应用的核心基础设施组件，这些组件被整个应用广泛使用：
- **config.py**: 从环境变量读取配置
- **database.py**: 异步数据库连接池和会话管理
- **redis_client.py**: 同步和异步 Redis 连接池
- **logging_config.py**: 基于 loguru 的日志配置
- **health_check.py**: 启动前的健康检查（MySQL、Redis）

### 2. workers/ - Celery 异步任务
所有与 Celery 相关的代码：
- **celery_app.py**: Celery 应用实例和配置
- **tasks.py**: 异步任务定义（选品分析、内容生成、审核）
- **startup_tasks.py**: Worker 启动时自动提交待执行任务

### 3. websocket/ - WebSocket 实时通信
WebSocket 相关功能：
- **websocket_manager.py**: 连接管理器，管理所有活跃连接
- **routes.py**: WebSocket 路由和认证

### 4. api/ - REST API 路由
HTTP API 端点：
- **v1/**: API v1 版本，包含认证、产品、任务、分析等接口
- **channels.py**: 多渠道 Webhook 回调接口
- **health.py**: 健康检查和就绪检查端点

### 5. channels/ - 多渠道接入
支持多种消息渠道（飞书、Telegram、企业微信）：
- **base.py**: 渠道抽象基类
- **lark.py**: 飞书渠道实现
- **manager.py**: 统一管理所有渠道实例

### 6. services/ - 业务服务
业务逻辑服务层：
- **ai_service.py**: AI 服务抽象层，支持 Mock 和 OpenAI

### 7. models/ - 数据模型
SQLAlchemy ORM 模型定义

### 8. schemas/ - Pydantic 模式
API 请求/响应的数据验证模式

### 9. dependencies/ - FastAPI 依赖项
可复用的依赖注入函数

### 10. middleware/ - 中间件
CORS、速率限制、安全响应头等中间件

### 11. utils/ - 工具函数
通用工具函数（密码哈希、JWT 等）

### 12. constants/ - 常量定义
数据库表名、Redis 键名等常量

## 导入规范

### 核心模块导入
```python
from app.core.config import settings
from app.core.database import get_db, AsyncSessionLocal
from app.core.redis_client import async_redis_client
from app.core.logging_config import setup_logging
```

### Workers 模块导入
```python
from app.workers.celery_app import celery_app
from app.workers.tasks import execute_task
from app.workers.startup_tasks import run_startup_tasks
```

### WebSocket 模块导入
```python
from app.websocket.websocket_manager import manager
from app.websocket import routes as websocket
```

## 启动方式

### 启动 FastAPI 服务
```bash
python run.py
```

### 启动 Celery Worker
```bash
python start_celery.py
```

## 重组优势

1. **清晰的模块划分**: 按功能将代码组织到不同目录
2. **更好的可维护性**: 相关代码集中在一起，易于查找和修改
3. **降低耦合度**: 核心基础设施与业务逻辑分离
4. **便于扩展**: 新功能可以按模块添加，不会污染根目录
5. **符合最佳实践**: 遵循 Python 项目的标准组织方式

## 注意事项

1. 所有导入路径已更新为新的模块结构
2. `__init__.py` 文件提供了便捷的导入接口
3. 启动脚本已更新以适配新结构
4. 所有测试通过，确保代码可正常运行
