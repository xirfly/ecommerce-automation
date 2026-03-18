"""
产品相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """产品基础信息"""
    name: str = Field(..., min_length=2, max_length=200, description="产品名称")
    category: str = Field(..., max_length=50, description="产品分类")
    price: float = Field(..., gt=0, description="价格")
    platform: Optional[str] = Field(None, max_length=50, description="目标平台")
    description: Optional[str] = Field(None, description="产品描述")


class ProductCreate(ProductBase):
    """创建产品请求"""
    pass


class ProductUpdate(BaseModel):
    """更新产品请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None
    platform: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class ProductResponse(ProductBase):
    """产品响应"""
    id: int
    cost: Optional[float]
    status: str
    analysis_result: Optional[dict]
    images: Optional[List[str]]
    videos: Optional[List[str]]
    detail_page_url: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """产品列表响应"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_length=1, description="产品ID列表")
