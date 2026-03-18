"""
销售数据相关的 Schema
"""
from typing import Optional, List
from datetime import date as DateType, datetime
from pydantic import BaseModel, Field


class SalesDataCreateRequest(BaseModel):
    """创建销售数据请求"""
    product_id: int = Field(..., description="产品ID")
    date: DateType = Field(..., description="日期")
    views: int = Field(default=0, description="浏览量")
    clicks: int = Field(default=0, description="点击量")
    orders: int = Field(default=0, description="订单量")
    sales_amount: float = Field(default=0.0, description="销售额")


class SalesDataUpdateRequest(BaseModel):
    """更新销售数据请求"""
    views: Optional[int] = Field(default=None, description="浏览量")
    clicks: Optional[int] = Field(default=None, description="点击量")
    orders: Optional[int] = Field(default=None, description="订单量")
    sales_amount: Optional[float] = Field(default=None, description="销售额")


class SalesDataResponse(BaseModel):
    """销售数据响应"""
    id: int
    product_id: int
    product_name: Optional[str] = None  # 关联查询
    date: DateType
    views: int
    clicks: int
    orders: int
    sales_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class SalesDataListResponse(BaseModel):
    """销售数据列表响应"""
    items: List[SalesDataResponse]
    total: int
    page: int
    page_size: int


class SalesTrendData(BaseModel):
    """销售趋势数据"""
    date: str
    views: int
    clicks: int
    orders: int
    sales_amount: float


class SalesStatistics(BaseModel):
    """销售统计数据"""
    total_views: int
    total_clicks: int
    total_orders: int
    total_sales_amount: float
    avg_conversion_rate: float  # 平均转化率
    trend_data: List[SalesTrendData]


class ProductSalesRanking(BaseModel):
    """产品销售排行"""
    product_id: int
    product_name: str
    total_orders: int
    total_sales_amount: float
    total_views: int
    conversion_rate: float


class SalesAnalyticsResponse(BaseModel):
    """销售分析响应"""
    statistics: SalesStatistics
    top_products: List[ProductSalesRanking]
    period_start: DateType
    period_end: DateType
