"""
数据分析API路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models import User, Product, Task, ProductStatus, TaskStatus
from app.schemas import Response
from app.dependencies.auth import get_current_user
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/analytics", tags=["数据分析"])


@router.get("/overview", response_model=Response[Dict[str, Any]])
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取概览统计数据"""

    # 产品统计
    product_count_query = select(func.count(Product.id))
    if current_user.role.value != "admin":
        product_count_query = product_count_query.where(Product.created_by == current_user.id)

    product_count_result = await db.execute(product_count_query)
    total_products = product_count_result.scalar()

    # 按状态统计产品
    product_status_query = select(
        Product.status,
        func.count(Product.id).label('count')
    ).group_by(Product.status)

    if current_user.role.value != "admin":
        product_status_query = product_status_query.where(Product.created_by == current_user.id)

    product_status_result = await db.execute(product_status_query)
    product_by_status = {row[0].value: row[1] for row in product_status_result.fetchall()}

    # 任务统计
    task_count_query = select(func.count(Task.id))
    if current_user.role.value != "admin":
        task_count_query = task_count_query.where(Task.created_by == current_user.id)

    task_count_result = await db.execute(task_count_query)
    total_tasks = task_count_result.scalar()

    # 按状态统计任务
    task_status_query = select(
        Task.status,
        func.count(Task.id).label('count')
    ).group_by(Task.status)

    if current_user.role.value != "admin":
        task_status_query = task_status_query.where(Task.created_by == current_user.id)

    task_status_result = await db.execute(task_status_query)
    task_by_status = {row[0].value: row[1] for row in task_status_result.fetchall()}

    # 计算成功率
    success_count = task_by_status.get('success', 0)
    failed_count = task_by_status.get('failed', 0)
    timeout_count = task_by_status.get('timeout', 0)
    completed_count = success_count + failed_count + timeout_count
    success_rate = (success_count / completed_count * 100) if completed_count > 0 else 0

    # 最近7天的任务趋势
    seven_days_ago = datetime.now() - timedelta(days=7)
    task_trend_query = select(
        func.date(Task.created_at).label('date'),
        func.count(Task.id).label('count')
    ).where(Task.created_at >= seven_days_ago).group_by(func.date(Task.created_at))

    if current_user.role.value != "admin":
        task_trend_query = task_trend_query.where(Task.created_by == current_user.id)

    task_trend_result = await db.execute(task_trend_query)
    task_trend = [
        {
            'date': row[0].strftime('%Y-%m-%d'),
            'count': row[1]
        }
        for row in task_trend_result.fetchall()
    ]

    # 按类型统计任务
    task_type_query = select(
        Task.task_type,
        func.count(Task.id).label('count')
    ).group_by(Task.task_type)

    if current_user.role.value != "admin":
        task_type_query = task_type_query.where(Task.created_by == current_user.id)

    task_type_result = await db.execute(task_type_query)
    task_by_type = {row[0]: row[1] for row in task_type_result.fetchall()}

    # 按分类统计产品
    product_category_query = select(
        Product.category,
        func.count(Product.id).label('count')
    ).group_by(Product.category)

    if current_user.role.value != "admin":
        product_category_query = product_category_query.where(Product.created_by == current_user.id)

    product_category_result = await db.execute(product_category_query)
    product_by_category = {row[0]: row[1] for row in product_category_result.fetchall()}

    return Response(
        code=0,
        data={
            'products': {
                'total': total_products,
                'by_status': product_by_status,
                'by_category': product_by_category,
            },
            'tasks': {
                'total': total_tasks,
                'by_status': task_by_status,
                'by_type': task_by_type,
                'success_rate': round(success_rate, 2),
                'trend': task_trend,
            },
        },
    )


@router.get("/tasks/stats", response_model=Response[Dict[str, Any]])
async def get_task_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务详细统计"""

    # 按状态统计
    status_query = select(
        Task.status,
        func.count(Task.id).label('count')
    ).group_by(Task.status)

    if current_user.role.value != "admin":
        status_query = status_query.where(Task.created_by == current_user.id)

    status_result = await db.execute(status_query)
    by_status = {row[0].value: row[1] for row in status_result.fetchall()}

    # 按类型统计
    type_query = select(
        Task.task_type,
        func.count(Task.id).label('count')
    ).group_by(Task.task_type)

    if current_user.role.value != "admin":
        type_query = type_query.where(Task.created_by == current_user.id)

    type_result = await db.execute(type_query)
    by_type = {row[0]: row[1] for row in type_result.fetchall()}

    # 平均执行时间（只统计已完成的任务）
    avg_time_query = select(
        func.avg(
            func.timestampdiff(
                'SECOND',
                Task.started_at,
                Task.completed_at
            )
        )
    ).where(
        Task.started_at.isnot(None),
        Task.completed_at.isnot(None)
    )

    if current_user.role.value != "admin":
        avg_time_query = avg_time_query.where(Task.created_by == current_user.id)

    avg_time_result = await db.execute(avg_time_query)
    avg_execution_time = avg_time_result.scalar() or 0

    return Response(
        code=0,
        data={
            'by_status': by_status,
            'by_type': by_type,
            'avg_execution_time': round(avg_execution_time, 2),
        },
    )


@router.get("/products/stats", response_model=Response[Dict[str, Any]])
async def get_product_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取产品详细统计"""

    # 按状态统计
    status_query = select(
        Product.status,
        func.count(Product.id).label('count')
    ).group_by(Product.status)

    if current_user.role.value != "admin":
        status_query = status_query.where(Product.created_by == current_user.id)

    status_result = await db.execute(status_query)
    by_status = {row[0].value: row[1] for row in status_result.fetchall()}

    # 按分类统计
    category_query = select(
        Product.category,
        func.count(Product.id).label('count')
    ).group_by(Product.category)

    if current_user.role.value != "admin":
        category_query = category_query.where(Product.created_by == current_user.id)

    category_result = await db.execute(category_query)
    by_category = {row[0]: row[1] for row in category_result.fetchall()}

    # 按平台统计
    platform_query = select(
        Product.platform,
        func.count(Product.id).label('count')
    ).where(Product.platform.isnot(None)).group_by(Product.platform)

    if current_user.role.value != "admin":
        platform_query = platform_query.where(Product.created_by == current_user.id)

    platform_result = await db.execute(platform_query)
    by_platform = {row[0]: row[1] for row in platform_result.fetchall()}

    return Response(
        code=0,
        data={
            'by_status': by_status,
            'by_category': by_category,
            'by_platform': by_platform,
        },
    )
