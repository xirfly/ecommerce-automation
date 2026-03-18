# 后端开发指南

## 📦 安装依赖

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 🗄️ 初始化数据库

```bash
# 1. 创建数据库
mysql -u root -p
CREATE DATABASE ecommerce_automation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 2. 导入表结构
mysql -u root -p ecommerce_automation < sql/schema.sql

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库和Redis配置
```

## 🚀 启动开发服务器

```bash
# 启动FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
# http://localhost:8000/docs
```

## 📁 项目结构

```
backend/
├── app/
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证API
│   │   ├── products.py     # 产品API
│   │   └── health.py       # 健康检查
│   ├── dependencies/       # 依赖注入
│   │   ├── __init__.py
│   │   └── auth.py         # 认证依赖
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py         # 基类
│   │   ├── user.py         # 用户模型
│   │   └── product.py      # 产品模型
│   ├── schemas/            # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── common.py       # 通用响应
│   │   ├── auth.py         # 认证Schema
│   │   └── product.py      # 产品Schema
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   └── auth.py         # 认证工具
│   ├── middleware/         # 中间件
│   │   └── security.py     # 安全中间件
│   ├── constants/          # 常量
│   │   ├── __init__.py
│   │   ├── mysql_tables.py
│   │   └── redis_keys.py
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库连接池
│   ├── redis_client.py     # Redis连接池
│   ├── logging_config.py   # 日志配置
│   └── main.py             # 主应用
├── sql/
│   └── schema.sql          # 数据库初始化脚本
├── requirements.txt        # 依赖列表
└── .env.example            # 环境变量模板
```

## 🎯 已实现功能

### 1. 用户认证API

**POST /api/v1/auth/login**
- 用户登录
- JWT Token生成
- Redis会话管理

**GET /api/v1/auth/me**
- 获取当前用户信息
- 权限列表

**POST /api/v1/auth/logout**
- 用户登出
- Token撤销

### 2. 产品管理API

**GET /api/v1/products**
- 产品列表（分页）
- 搜索（关键词）
- 筛选（分类、状态）
- 权限控制（非管理员只看自己的）

**POST /api/v1/products**
- 创建产品
- 表单验证
- 权限检查（需要operator或admin）

**GET /api/v1/products/{id}**
- 产品详情
- 权限检查

**PUT /api/v1/products/{id}**
- 更新产品
- 部分更新支持
- 权限检查

**DELETE /api/v1/products/{id}**
- 删除产品
- 权限检查

**POST /api/v1/products/batch-delete**
- 批量删除
- 权限检查

### 3. 健康检查

**GET /health**
- 服务健康检查

**GET /ready**
- 就绪检查（数据库+Redis）

## 🔐 认证流程

```python
# 1. 登录获取Token
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# 2. 使用Token访问API
GET /api/v1/products
Headers: Authorization: Bearer {token}

# 3. 登出
POST /api/v1/auth/logout
Headers: Authorization: Bearer {token}
```

## 🛡️ 权限系统

### 角色定义
- **admin**: 所有权限
- **operator**: 产品管理、任务管理、数据查看
- **viewer**: 只读权限

### 权限装饰器
```python
from app.dependencies.auth import get_current_user, require_operator, require_admin

# 需要登录
@router.get("/")
async def get_data(current_user: User = Depends(get_current_user)):
    pass

# 需要operator或admin
@router.post("/")
async def create_data(current_user: User = Depends(require_operator)):
    pass

# 需要admin
@router.delete("/")
async def delete_data(current_user: User = Depends(require_admin)):
    pass
```

## 📝 数据模型

### User模型
```python
class User(BaseModel):
    id: int
    username: str
    password_hash: str
    email: str | None
    role: UserRole  # admin/operator/viewer
    team_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Product模型
```python
class Product(BaseModel):
    id: int
    name: str
    category: str
    price: Decimal
    cost: Decimal | None
    status: ProductStatus  # draft/analyzing/generating/reviewing/published/offline
    platform: str | None
    analysis_result: dict | None
    images: list[str] | None
    videos: list[str] | None
    description: str | None
    detail_page_url: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
```

## 🧪 测试API

### 使用curl
```bash
# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 获取产品列表
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer {token}"

# 创建产品
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试产品","category":"数码","price":199.00}'
```

### 使用Swagger UI
访问 http://localhost:8000/docs

## 🐛 常见问题

### 1. 数据库连接失败
- 检查MySQL是否启动
- 检查.env中的DATABASE_URL配置
- 检查数据库是否已创建

### 2. Redis连接失败
- 检查Redis是否启动
- 检查.env中的REDIS_URL配置

### 3. 导入错误
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

## 📚 下一步开发

### 待实现功能
- [ ] 任务管理API
- [ ] Celery任务队列
- [ ] WebSocket实时推送
- [ ] Agent实现
- [ ] 数据分析API
- [ ] 渠道配置API

### 优化建议
- [ ] 添加单元测试
- [ ] 添加API限流
- [ ] 添加请求日志
- [ ] 优化数据库查询

## 🎉 快速测试

```bash
# 1. 启动服务
uvicorn app.main:app --reload

# 2. 访问API文档
# http://localhost:8000/docs

# 3. 测试登录
# 用户名: admin
# 密码: admin123

# 4. 测试产品API
# 创建、查询、更新、删除产品
```
