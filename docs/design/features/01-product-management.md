# 产品管理模块

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

实现产品全生命周期管理，支持：
- 产品CRUD操作
- 产品状态流转
- 批量操作
- 产品搜索和筛选

---

## 2. 功能清单

### 2.1 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 创建产品 | 填写产品基础信息 | P0 |
| 查看产品列表 | 分页、筛选、排序 | P0 |
| 查看产品详情 | 完整的产品信息 | P0 |
| 编辑产品 | 修改产品信息 | P0 |
| 删除产品 | 软删除或硬删除 | P0 |
| 批量操作 | 批量删除、批量发布 | P1 |
| 产品搜索 | 按名称、分类搜索 | P1 |
| 产品导入 | Excel批量导入 | P2 |
| 产品导出 | 导出为Excel | P2 |

### 2.2 状态管理

**产品状态流转：**
```
draft (草稿)
    ↓ 触发分析
analyzing (分析中)
    ↓ 分析完成
generating (生成中)
    ↓ 内容生成完成
reviewing (待审核)
    ↓ 审核通过
published (已发布)
    ↓ 下架
offline (已下架)

任何状态 → failed (失败)
```

---

## 3. API设计

### 3.1 RESTful API

**基础URL：** `/api/v1/products`

#### 3.1.1 创建产品

```http
POST /api/v1/products
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "name": "无线蓝牙耳机",
  "category": "数码",
  "price": 199.00,
  "cost": 120.00,
  "target_platforms": ["淘宝", "京东"],
  "description": "产品描述（可选）"
}

Response (201 Created):
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "id": 123,
    "name": "无线蓝牙耳机",
    "category": "数码",
    "price": 199.00,
    "cost": 120.00,
    "status": "draft",
    "target_platforms": ["淘宝", "京东"],
    "created_at": "2026-03-16T10:00:00Z",
    "updated_at": "2026-03-16T10:00:00Z"
  }
}
```

#### 3.1.2 获取产品列表

```http
GET /api/v1/products?page=1&page_size=20&status=published&category=数码&keyword=耳机
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "items": [
      {
        "id": 123,
        "name": "无线蓝牙耳机",
        "category": "数码",
        "price": 199.00,
        "status": "published",
        "created_at": "2026-03-16T10:00:00Z"
      }
    ],
    "total": 245,
    "page": 1,
    "page_size": 20,
    "total_pages": 13
  }
}
```

#### 3.1.3 获取产品详情

```http
GET /api/v1/products/{id}
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "id": 123,
    "name": "无线蓝牙耳机",
    "category": "数码",
    "price": 199.00,
    "cost": 120.00,
    "status": "published",
    "target_platforms": ["淘宝", "京东"],
    "platform_product_ids": {
      "淘宝": "123456789",
      "京东": "987654321"
    },
    "detail_page_url": "https://preview.example.com/xxx",
    "images": {
      "main": "https://cdn.example.com/main.jpg",
      "detail": ["https://cdn.example.com/detail1.jpg"]
    },
    "videos": {
      "demo": "https://cdn.example.com/demo.mp4"
    },
    "description": "产品描述",
    "created_by": 1,
    "created_at": "2026-03-16T10:00:00Z",
    "updated_at": "2026-03-16T10:30:00Z"
  }
}
```

#### 3.1.4 更新产品

```http
PUT /api/v1/products/{id}
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "name": "无线蓝牙耳机（更新）",
  "price": 189.00
}

Response (200 OK):
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "id": 123,
    "name": "无线蓝牙耳机（更新）",
    "price": 189.00,
    "updated_at": "2026-03-16T11:00:00Z"
  }
}
```

#### 3.1.5 删除产品

```http
DELETE /api/v1/products/{id}
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "message": "删除成功"
}
```

#### 3.1.6 批量操作

```http
POST /api/v1/products/batch
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "action": "delete",  // delete | publish | offline
  "product_ids": [123, 124, 125]
}

Response (200 OK):
{
  "code": 0,
  "message": "批量操作成功",
  "data": {
    "success_count": 3,
    "failed_count": 0,
    "failed_ids": []
  }
}
```

---

## 4. 数据模型

### 4.1 Product模型

```python
from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, JSON, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.constants import MySQLTables

class Product(Base):
    """产品模型"""
    __tablename__ = MySQLTables.PRODUCTS

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment='产品名称')
    category = Column(String(100), comment='产品分类')
    price = Column(DECIMAL(10, 2), comment='价格')
    cost = Column(DECIMAL(10, 2), comment='成本')
    status = Column(
        Enum('draft', 'analyzing', 'generating', 'reviewing', 'published', 'offline', 'failed'),
        default='draft',
        comment='状态'
    )
    target_platforms = Column(JSON, comment='目标平台')
    platform_product_ids = Column(JSON, comment='平台产品ID')
    detail_page_url = Column(Text, comment='详情页链接')
    images = Column(JSON, comment='图片URLs')
    videos = Column(JSON, comment='视频URLs')
    description = Column(Text, comment='产品描述')
    created_by = Column(BigInteger, comment='创建人ID')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        comment='更新时间'
    )
```

### 4.2 Pydantic Schema

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ProductCreate(BaseModel):
    """创建产品请求"""
    name: str = Field(..., min_length=1, max_length=255, description="产品名称")
    category: Optional[str] = Field(None, max_length=100, description="产品分类")
    price: Optional[float] = Field(None, ge=0, description="价格")
    cost: Optional[float] = Field(None, ge=0, description="成本")
    target_platforms: List[str] = Field(default_factory=list, description="目标平台")
    description: Optional[str] = Field(None, description="产品描述")

class ProductUpdate(BaseModel):
    """更新产品请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    target_platforms: Optional[List[str]] = None
    description: Optional[str] = None

class ProductResponse(BaseModel):
    """产品响应"""
    id: int
    name: str
    category: Optional[str]
    price: Optional[float]
    cost: Optional[float]
    status: str
    target_platforms: List[str]
    platform_product_ids: Optional[Dict[str, str]]
    detail_page_url: Optional[str]
    images: Optional[Dict[str, any]]
    videos: Optional[Dict[str, str]]
    description: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## 5. 业务逻辑

### 5.1 产品服务类

```python
from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate
from app.constants import RedisKeys, RedisTTL

class ProductService:
    """产品服务"""

    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client

    def create_product(self, data: ProductCreate, user_id: int) -> Product:
        """创建产品"""
        product = Product(
            **data.dict(),
            created_by=user_id
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product(self, product_id: int) -> Optional[Product]:
        """获取产品（带缓存）"""
        # 1. 先查缓存
        cache_key = RedisKeys.cache_product(product_id)
        cached = self.redis.hgetall(cache_key)
        if cached:
            return Product(**cached)

        # 2. 缓存未命中，查数据库
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        # 3. 写入缓存
        self.redis.hset(cache_key, mapping=product.__dict__)
        self.redis.expire(cache_key, RedisTTL.CACHE_PRODUCT)

        return product

    def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        """更新产品"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("产品不存在")

        # 更新字段
        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)

        # 删除缓存
        cache_key = RedisKeys.cache_product(product_id)
        self.redis.delete(cache_key)

        return product

    def delete_product(self, product_id: int):
        """删除产品"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("产品不存在")

        self.db.delete(product)
        self.db.commit()

        # 删除缓存
        cache_key = RedisKeys.cache_product(product_id)
        self.redis.delete(cache_key)

    def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> tuple[List[Product], int]:
        """获取产品列表"""
        query = self.db.query(Product)

        # 筛选条件
        if status:
            query = query.filter(Product.status == status)
        if category:
            query = query.filter(Product.category == category)
        if keyword:
            query = query.filter(Product.name.like(f"%{keyword}%"))

        # 总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        products = query.order_by(Product.created_at.desc()).offset(offset).limit(page_size).all()

        return products, total
```

---

## 6. 前端实现

### 6.1 产品列表页面

**组件结构：**
```tsx
// src/pages/ProductList.tsx
import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Select, Space, message } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { getProducts, deleteProduct } from '@/services/product';

const ProductList: React.FC = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [filters, setFilters] = useState({ status: '', category: '', keyword: '' });

  // 加载产品列表
  const loadProducts = async () => {
    setLoading(true);
    try {
      const res = await getProducts({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters
      });
      setProducts(res.data.items);
      setPagination({ ...pagination, total: res.data.total });
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [pagination.current, filters]);

  // 表格列定义
  const columns = [
    {
      title: '产品名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap = {
          draft: { text: '草稿', color: 'default' },
          analyzing: { text: '分析中', color: 'processing' },
          generating: { text: '生成中', color: 'processing' },
          published: { text: '已发布', color: 'success' },
          failed: { text: '失败', color: 'error' },
        };
        return <Tag color={statusMap[status]?.color}>{statusMap[status]?.text}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => handleView(record.id)}>查看</Button>
          <Button type="link" onClick={() => handleEdit(record.id)}>编辑</Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* 筛选栏 */}
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索产品名称"
          prefix={<SearchOutlined />}
          onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
        />
        <Select
          placeholder="状态"
          style={{ width: 120 }}
          onChange={(value) => setFilters({ ...filters, status: value })}
        >
          <Select.Option value="">全部</Select.Option>
          <Select.Option value="draft">草稿</Select.Option>
          <Select.Option value="published">已发布</Select.Option>
        </Select>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          新建产品
        </Button>
      </Space>

      {/* 表格 */}
      <Table
        columns={columns}
        dataSource={products}
        loading={loading}
        pagination={pagination}
        onChange={(newPagination) => setPagination(newPagination)}
        rowKey="id"
      />
    </div>
  );
};

export default ProductList;
```

---

## 7. 权限控制

### 7.1 权限矩阵

| 操作 | 管理员 | 运营人员 | 查看者 |
|------|--------|----------|--------|
| 查看产品列表 | ✅ | ✅ | ✅ |
| 查看产品详情 | ✅ | ✅ | ✅ |
| 创建产品 | ✅ | ✅ | ❌ |
| 编辑产品 | ✅ | ✅ | ❌ |
| 删除产品 | ✅ | ✅ | ❌ |
| 批量操作 | ✅ | ✅ | ❌ |

### 7.2 权限验证

```python
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user

@router.post("/products")
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    """创建产品（需要operator或admin权限）"""
    if current_user.role not in ['operator', 'admin']:
        raise HTTPException(status_code=403, detail="权限不足")

    product = product_service.create_product(data, current_user.id)
    return {"code": 0, "message": "创建成功", "data": product}
```

---

## 8. 相关文档

- [数据模型设计](../database/01-data-model.md) - products表结构
- [任务调度模块](02-task-scheduling.md) - 触发Agent任务
- [系统架构总览](../architecture/01-system-architecture.md) - 整体架构
