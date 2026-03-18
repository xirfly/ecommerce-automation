"""
销售数据 API
"""
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.sales_data import SalesData
from app.models.product import Product
from app.schemas.sales import (
    SalesDataCreateRequest,
    SalesDataUpdateRequest,
    SalesDataResponse,
    SalesDataListResponse,
    SalesStatistics,
    SalesTrendData,
    ProductSalesRanking,
    SalesAnalyticsResponse,
)
from app.schemas.common import Response

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])


@router.post("/create", response_model=Response[SalesDataResponse])
async def create_sales_data(
    data: SalesDataCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建销售数据"""
    # 检查产品是否存在
    product_query = select(Product).where(Product.id == data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        return Response(code=404, message="产品不存在")

    # 检查是否已存在该日期的数据
    existing_query = select(SalesData).where(
        and_(
            SalesData.product_id == data.product_id,
            SalesData.date == data.date
        )
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        return Response(code=400, message="该产品在此日期的销售数据已存在，请使用更新接口")

    # 创建销售数据
    sales_data = SalesData(
        product_id=data.product_id,
        date=data.date,
        views=data.views,
        clicks=data.clicks,
        orders=data.orders,
        sales_amount=data.sales_amount,
    )
    db.add(sales_data)
    await db.commit()
    await db.refresh(sales_data)

    response_data = SalesDataResponse(
        id=sales_data.id,
        product_id=sales_data.product_id,
        product_name=product.name,
        date=sales_data.date,
        views=sales_data.views,
        clicks=sales_data.clicks,
        orders=sales_data.orders,
        sales_amount=sales_data.sales_amount,
        created_at=sales_data.created_at,
    )

    return Response(code=0, message="创建成功", data=response_data)


@router.get("/list", response_model=Response[SalesDataListResponse])
async def get_sales_data_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    product_id: Optional[int] = Query(None, description="产品ID筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取销售数据列表"""
    # 构建查询
    query = select(SalesData).options(joinedload(SalesData.product))

    # 筛选条件
    conditions = []
    if product_id:
        conditions.append(SalesData.product_id == product_id)
    if start_date:
        conditions.append(SalesData.date >= start_date)
    if end_date:
        conditions.append(SalesData.date <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    # 按日期倒序
    query = query.order_by(desc(SalesData.date))

    # 计算总数
    count_query = select(func.count()).select_from(SalesData)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    sales_data_list = result.scalars().all()

    # 构建响应
    items = [
        SalesDataResponse(
            id=sd.id,
            product_id=sd.product_id,
            product_name=sd.product.name if sd.product else None,
            date=sd.date,
            views=sd.views,
            clicks=sd.clicks,
            orders=sd.orders,
            sales_amount=sd.sales_amount,
            created_at=sd.created_at,
        )
        for sd in sales_data_list
    ]

    return Response(
        code=0,
        message="获取成功",
        data=SalesDataListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.put("/{sales_id}", response_model=Response[SalesDataResponse])
async def update_sales_data(
    sales_id: int,
    data: SalesDataUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新销售数据"""
    query = select(SalesData).options(joinedload(SalesData.product)).where(SalesData.id == sales_id)
    result = await db.execute(query)
    sales_data = result.scalar_one_or_none()

    if not sales_data:
        return Response(code=404, message="销售数据不存在")

    # 更新字段
    if data.views is not None:
        sales_data.views = data.views
    if data.clicks is not None:
        sales_data.clicks = data.clicks
    if data.orders is not None:
        sales_data.orders = data.orders
    if data.sales_amount is not None:
        sales_data.sales_amount = data.sales_amount

    await db.commit()
    await db.refresh(sales_data)

    response_data = SalesDataResponse(
        id=sales_data.id,
        product_id=sales_data.product_id,
        product_name=sales_data.product.name if sales_data.product else None,
        date=sales_data.date,
        views=sales_data.views,
        clicks=sales_data.clicks,
        orders=sales_data.orders,
        sales_amount=sales_data.sales_amount,
        created_at=sales_data.created_at,
    )

    return Response(code=0, message="更新成功", data=response_data)


@router.delete("/{sales_id}", response_model=Response[None])
async def delete_sales_data(
    sales_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除销售数据"""
    if current_user.role != "admin":
        return Response(code=403, message="无权操作")

    query = select(SalesData).where(SalesData.id == sales_id)
    result = await db.execute(query)
    sales_data = result.scalar_one_or_none()

    if not sales_data:
        return Response(code=404, message="销售数据不存在")

    await db.delete(sales_data)
    await db.commit()

    return Response(code=0, message="删除成功")


@router.get("/analytics", response_model=Response[SalesAnalyticsResponse])
async def get_sales_analytics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    product_id: Optional[int] = Query(None, description="产品ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取销售分析数据"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 构建基础查询条件
    conditions = [
        SalesData.date >= start_date,
        SalesData.date <= end_date,
    ]
    if product_id:
        conditions.append(SalesData.product_id == product_id)

    # 1. 统计总数据
    stats_query = select(
        func.sum(SalesData.views).label("total_views"),
        func.sum(SalesData.clicks).label("total_clicks"),
        func.sum(SalesData.orders).label("total_orders"),
        func.sum(SalesData.sales_amount).label("total_sales_amount"),
    ).where(and_(*conditions))

    stats_result = await db.execute(stats_query)
    stats = stats_result.one()

    total_views = stats.total_views or 0
    total_clicks = stats.total_clicks or 0
    total_orders = stats.total_orders or 0
    total_sales_amount = float(stats.total_sales_amount or 0)

    # 计算平均转化率
    avg_conversion_rate = (total_orders / total_clicks * 100) if total_clicks > 0 else 0

    # 2. 趋势数据（按日期分组）
    trend_query = select(
        SalesData.date,
        func.sum(SalesData.views).label("views"),
        func.sum(SalesData.clicks).label("clicks"),
        func.sum(SalesData.orders).label("orders"),
        func.sum(SalesData.sales_amount).label("sales_amount"),
    ).where(and_(*conditions)).group_by(SalesData.date).order_by(SalesData.date)

    trend_result = await db.execute(trend_query)
    trend_rows = trend_result.all()

    trend_data = [
        SalesTrendData(
            date=row.date.isoformat(),
            views=row.views or 0,
            clicks=row.clicks or 0,
            orders=row.orders or 0,
            sales_amount=float(row.sales_amount or 0),
        )
        for row in trend_rows
    ]

    # 3. 产品销售排行（Top 10）
    ranking_query = select(
        Product.id,
        Product.name,
        func.sum(SalesData.orders).label("total_orders"),
        func.sum(SalesData.sales_amount).label("total_sales_amount"),
        func.sum(SalesData.views).label("total_views"),
        func.sum(SalesData.clicks).label("total_clicks"),
    ).join(
        SalesData, Product.id == SalesData.product_id
    ).where(
        and_(
            SalesData.date >= start_date,
            SalesData.date <= end_date,
        )
    ).group_by(
        Product.id, Product.name
    ).order_by(
        desc(func.sum(SalesData.sales_amount))
    ).limit(10)

    ranking_result = await db.execute(ranking_query)
    ranking_rows = ranking_result.all()

    top_products = [
        ProductSalesRanking(
            product_id=row.id,
            product_name=row.name,
            total_orders=row.total_orders or 0,
            total_sales_amount=float(row.total_sales_amount or 0),
            total_views=row.total_views or 0,
            conversion_rate=(row.total_orders / row.total_clicks * 100) if row.total_clicks and row.total_clicks > 0 else 0,
        )
        for row in ranking_rows
    ]

    # 构建响应
    analytics = SalesAnalyticsResponse(
        statistics=SalesStatistics(
            total_views=total_views,
            total_clicks=total_clicks,
            total_orders=total_orders,
            total_sales_amount=total_sales_amount,
            avg_conversion_rate=round(avg_conversion_rate, 2),
            trend_data=trend_data,
        ),
        top_products=top_products,
        period_start=start_date,
        period_end=end_date,
    )

    return Response(code=0, message="获取成功", data=analytics)
