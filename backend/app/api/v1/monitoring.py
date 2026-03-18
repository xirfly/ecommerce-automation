"""
监控 API 端点
"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, Task, Product, Feedback, TaskStatus, FeedbackStatus
from app.schemas import Response as APIResponse
from app.monitoring.metrics import (
    products_total,
    users_total,
    feedback_total,
    db_pool_size,
    db_pool_available,
    redis_connected,
)
from app.core.redis_client import get_redis

router = APIRouter(tags=["监控"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus 指标端点
    返回所有收集的指标数据
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/api/v1/monitoring/health", response_model=APIResponse[dict])
async def health_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    健康检查端点
    检查各个组件的健康状态
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }

    # 检查数据库
    try:
        await db.execute(select(1))
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection is working"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }

    # 检查 Redis
    try:
        redis = await get_redis()
        await redis.ping()
        redis_connected.set(1)
        health_status["components"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection is working"
        }
    except Exception as e:
        redis_connected.set(0)
        health_status["status"] = "unhealthy"
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis error: {str(e)}"
        }

    return APIResponse(
        code=0 if health_status["status"] == "healthy" else 500,
        message="Health check completed",
        data=health_status
    )


@router.get("/api/v1/monitoring/statistics", response_model=APIResponse[dict])
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取系统统计信息
    更新 Prometheus 业务指标
    """
    # 产品统计
    product_stats_query = select(
        Product.status,
        func.count(Product.id).label('count')
    ).group_by(Product.status)
    product_stats_result = await db.execute(product_stats_query)
    product_stats = {row[0].value: row[1] for row in product_stats_result}

    # 更新产品指标
    for status, count in product_stats.items():
        products_total.labels(status=status).set(count)

    # 用户统计
    user_stats_query = select(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role)
    user_stats_result = await db.execute(user_stats_query)
    user_stats = {row[0].value: row[1] for row in user_stats_result}

    # 更新用户指标
    for role, count in user_stats.items():
        users_total.labels(role=role).set(count)

    # 任务统计
    task_stats_query = select(
        Task.status,
        func.count(Task.id).label('count')
    ).group_by(Task.status)
    task_stats_result = await db.execute(task_stats_query)
    task_stats = {row[0].value: row[1] for row in task_stats_result}

    # 反馈统计
    feedback_stats_query = select(
        Feedback.status,
        Feedback.priority,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.status, Feedback.priority)
    feedback_stats_result = await db.execute(feedback_stats_query)

    # 更新反馈指标
    for row in feedback_stats_result:
        feedback_total.labels(
            status=row[0].value,
            priority=row[1].value
        ).set(row[2])

    # 数据库连接池统计
    pool = db.get_bind().pool
    if hasattr(pool, 'size'):
        db_pool_size.set(pool.size())
    if hasattr(pool, 'checkedout'):
        db_pool_available.set(pool.size() - pool.checkedout())

    return APIResponse(
        code=0,
        message="Statistics retrieved successfully",
        data={
            "products": product_stats,
            "users": user_stats,
            "tasks": task_stats,
        }
    )


@router.get("/api/v1/monitoring/alerts", response_model=APIResponse[list])
async def get_active_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前活跃的告警
    """
    alerts = []

    # 检查失败任务数量
    failed_tasks_query = select(func.count(Task.id)).where(
        Task.status == TaskStatus.FAILED
    )
    failed_tasks_result = await db.execute(failed_tasks_query)
    failed_tasks_count = failed_tasks_result.scalar()

    if failed_tasks_count > 10:
        alerts.append({
            "severity": "warning",
            "title": "高失败任务数",
            "message": f"当前有 {failed_tasks_count} 个失败任务",
            "metric": "task_failures",
            "value": failed_tasks_count,
            "threshold": 10
        })

    # 检查待处理反馈数量
    pending_feedback_query = select(func.count(Feedback.id)).where(
        Feedback.status == FeedbackStatus.PENDING
    )
    pending_feedback_result = await db.execute(pending_feedback_query)
    pending_feedback_count = pending_feedback_result.scalar()

    if pending_feedback_count > 20:
        alerts.append({
            "severity": "info",
            "title": "待处理反馈较多",
            "message": f"当前有 {pending_feedback_count} 个待处理反馈",
            "metric": "pending_feedback",
            "value": pending_feedback_count,
            "threshold": 20
        })

    return APIResponse(
        code=0,
        message="Active alerts retrieved",
        data=alerts
    )
