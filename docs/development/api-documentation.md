# API 开发文档

## 基础信息

- **后端地址**：http://localhost:8000
- **前端地址**：http://localhost:3001
- **API 文档**：http://localhost:8000/docs
- **API 版本**：v1

## 认证方式

所有需要认证的 API 都需要在请求头中携带 JWT Token：

```
Authorization: Bearer {access_token}
```

## API 列表

### 1. 认证模块 (`/api/v1/auth`)

#### 1.1 用户登录
- **接口**：`POST /api/v1/auth/login`
- **描述**：用户登录获取 Token
- **请求体**：
```json
{
  "username": "admin",
  "password": "admin123"
}
```
- **响应**：
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

#### 1.2 获取当前用户信息
- **接口**：`GET /api/v1/auth/me`
- **描述**：获取当前登录用户的详细信息
- **需要认证**：是
- **响应**：
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "permissions": ["*"]
  }
}
```

#### 1.3 用户登出
- **接口**：`POST /api/v1/auth/logout`
- **描述**：用户登出
- **需要认证**：是

---

### 2. 产品管理 (`/api/v1/products`)

#### 2.1 获取产品列表
- **接口**：`GET /api/v1/products`
- **描述**：获取产品列表，支持分页、搜索、筛选
- **需要认证**：是
- **查询参数**：
  - `page`：页码（默认 1）
  - `page_size`：每页数量（默认 10，最大 100）
  - `keyword`：搜索关键词（可选）
  - `category`：产品分类（可选）
  - `status`：产品状态（可选）
- **响应**：
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "产品名称",
        "category": "数码",
        "price": 99.00,
        "cost": 50.00,
        "status": "draft",
        "platform": "淘宝,京东",
        "description": "产品描述",
        "images": ["url1", "url2"],
        "videos": ["url1"],
        "detail_page_url": "https://...",
        "created_by": 1,
        "created_at": "2026-03-17T10:00:00",
        "updated_at": "2026-03-17T10:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

#### 2.2 获取产品详情
- **接口**：`GET /api/v1/products/{id}`
- **描述**：获取指定产品的详细信息
- **需要认证**：是
- **路径参数**：
  - `id`：产品 ID

#### 2.3 创建产品
- **接口**：`POST /api/v1/products`
- **描述**：创建新产品
- **需要认证**：是（需要 operator 或 admin 权限）
- **请求体**：
```json
{
  "name": "产品名称",
  "category": "数码",
  "price": 99.00,
  "platform": "淘宝,京东",
  "description": "产品描述"
}
```

#### 2.4 更新产品
- **接口**：`PUT /api/v1/products/{id}`
- **描述**：更新产品信息
- **需要认证**：是（需要 operator 或 admin 权限）
- **路径参数**：
  - `id`：产品 ID
- **请求体**：（所有字段可选）
```json
{
  "name": "新产品名称",
  "category": "服饰",
  "price": 199.00,
  "cost": 100.00,
  "status": "published",
  "platform": "拼多多",
  "description": "新描述"
}
```

#### 2.5 删除产品
- **接口**：`DELETE /api/v1/products/{id}`
- **描述**：删除指定产品
- **需要认证**：是（需要 operator 或 admin 权限）
- **路径参数**：
  - `id`：产品 ID

#### 2.6 批量删除产品
- **接口**：`POST /api/v1/products/batch-delete`
- **描述**：批量删除多个产品
- **需要认证**：是（需要 operator 或 admin 权限）
- **请求体**：
```json
{
  "ids": [1, 2, 3]
}
```

---

### 3. 任务管理 (`/api/v1/tasks`)

#### 3.1 获取任务列表
- **接口**：`GET /api/v1/tasks`
- **描述**：获取任务列表，支持分页、筛选
- **需要认证**：是
- **查询参数**：
  - `page`：页码（默认 1）
  - `page_size`：每页数量（默认 10，最大 100）
  - `product_id`：产品 ID（可选）
  - `task_type`：任务类型（可选）
  - `status`：任务状态（可选）
- **响应**：
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "task_id": "uuid",
        "product_id": 1,
        "task_type": "product_analysis",
        "status": "pending",
        "progress": 0,
        "result": null,
        "error_message": null,
        "retry_count": 0,
        "started_at": null,
        "completed_at": null,
        "created_by": 1,
        "created_at": "2026-03-17T10:00:00",
        "updated_at": "2026-03-17T10:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 10
  }
}
```

#### 3.2 获取任务详情
- **接口**：`GET /api/v1/tasks/{id}`
- **描述**：获取指定任务的详细信息
- **需要认证**：是
- **路径参数**：
  - `id`：任务 ID

#### 3.3 创建任务
- **接口**：`POST /api/v1/tasks`
- **描述**：为产品创建新任务
- **需要认证**：是（需要 operator 或 admin 权限）
- **请求体**：
```json
{
  "product_id": 1,
  "task_type": "product_analysis"
}
```
- **任务类型**：
  - `product_analysis`：选品分析
  - `content_generation`：内容生成
  - `image_generation`：图片生成
  - `video_generation`：视频生成
  - `review`：内容审核
  - `publish`：发布上架

#### 3.4 重试任务
- **接口**：`POST /api/v1/tasks/{id}/retry`
- **描述**：重试失败或超时的任务
- **需要认证**：是（需要 operator 或 admin 权限）
- **路径参数**：
  - `id`：任务 ID

#### 3.5 获取任务日志
- **接口**：`GET /api/v1/tasks/{id}/logs`
- **描述**：获取任务的执行日志
- **需要认证**：是
- **路径参数**：
  - `id`：任务 ID
- **响应**：
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "task_id": 1,
      "agent_name": "AnalysisAgent",
      "log_level": "INFO",
      "message": "开始分析产品...",
      "extra_data": {},
      "created_at": "2026-03-17T10:00:00"
    }
  ]
}
```

#### 3.6 删除任务
- **接口**：`DELETE /api/v1/tasks/{id}`
- **描述**：删除指定任务（不能删除正在运行的任务）
- **需要认证**：是（需要 operator 或 admin 权限）
- **路径参数**：
  - `id`：任务 ID

---

### 4. 数据分析 (`/api/v1/analytics`)

#### 4.1 获取概览统计
- **接口**：`GET /api/v1/analytics/overview`
- **描述**：获取系统概览统计数据
- **需要认证**：是
- **响应**：
```json
{
  "code": 0,
  "data": {
    "products": {
      "total": 100,
      "by_status": {
        "draft": 20,
        "published": 50,
        "offline": 30
      },
      "by_category": {
        "数码": 40,
        "服饰": 30,
        "家居": 30
      }
    },
    "tasks": {
      "total": 500,
      "by_status": {
        "pending": 10,
        "running": 5,
        "success": 450,
        "failed": 30,
        "timeout": 5
      },
      "by_type": {
        "product_analysis": 200,
        "content_generation": 150,
        "image_generation": 100,
        "video_generation": 50
      },
      "success_rate": 90.00,
      "trend": [
        {
          "date": "2026-03-11",
          "count": 50
        },
        {
          "date": "2026-03-12",
          "count": 60
        }
      ]
    }
  }
}
```

#### 4.2 获取任务统计
- **接口**：`GET /api/v1/analytics/tasks/stats`
- **描述**：获取任务详细统计数据
- **需要认证**：是
- **响应**：
```json
{
  "code": 0,
  "data": {
    "by_status": {
      "pending": 10,
      "running": 5,
      "success": 450,
      "failed": 30,
      "timeout": 5
    },
    "by_type": {
      "product_analysis": 200,
      "content_generation": 150
    },
    "avg_execution_time": 120.50
  }
}
```

#### 4.3 获取产品统计
- **接口**：`GET /api/v1/analytics/products/stats`
- **描述**：获取产品详细统计数据
- **需要认证**：是
- **响应**：
```json
{
  "code": 0,
  "data": {
    "by_status": {
      "draft": 20,
      "published": 50
    },
    "by_category": {
      "数码": 40,
      "服饰": 30
    },
    "by_platform": {
      "淘宝": 30,
      "京东": 25,
      "拼多多": 20
    }
  }
}
```

---

## 数据模型

### 产品状态 (ProductStatus)
- `draft`：草稿
- `analyzing`：分析中
- `generating`：生成中
- `reviewing`：审核中
- `published`：已发布
- `offline`：已下架

### 任务状态 (TaskStatus)
- `pending`：待执行
- `running`：执行中
- `success`：成功
- `failed`：失败
- `timeout`：超时

### 任务类型 (TaskType)
- `product_analysis`：选品分析
- `content_generation`：内容生成
- `image_generation`：图片生成
- `video_generation`：视频生成
- `review`：内容审核
- `publish`：发布上架

### 用户角色 (UserRole)
- `admin`：管理员（所有权限）
- `operator`：操作员（读写权限）
- `viewer`：查看者（只读权限）

---

## 错误码

- `0`：成功
- `400`：请求参数错误
- `401`：未认证或认证失败
- `403`：权限不足
- `404`：资源不存在
- `422`：请求参数验证失败
- `429`：请求过于频繁
- `500`：服务器内部错误

---

## 权限说明

### 管理员 (admin)
- 可以查看所有用户的数据
- 可以执行所有操作

### 操作员 (operator)
- 只能查看和操作自己创建的数据
- 可以创建、编辑、删除产品和任务

### 查看者 (viewer)
- 只能查看自己创建的数据
- 不能创建、编辑、删除

---

## 开发环境

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (aiomysql)
- Redis
- MySQL 8.0

### 前端
- React 18
- TypeScript
- Ant Design
- ECharts
- Vite

---

## 快速开始

### 启动后端
```bash
cd backend
python run.py
```

### 启动前端
```bash
cd frontend
npm run dev
```

### 默认账号
- 用户名：admin
- 密码：admin123

---

## API 测试示例

### 使用 curl 测试

```bash
# 1. 登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -s | python -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

# 2. 获取产品列表
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"

# 3. 创建任务
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"task_type":"product_analysis"}'

# 4. 获取统计数据
curl -X GET http://localhost:8000/api/v1/analytics/overview \
  -H "Authorization: Bearer $TOKEN"
```

---

## 注意事项

1. 所有时间字段使用 ISO 8601 格式
2. 所有金额字段保留两位小数
3. 分页从 1 开始计数
4. Token 有效期为 24 小时
5. 非管理员用户只能操作自己创建的数据
