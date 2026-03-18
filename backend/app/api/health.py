"""
健康检查端点
"""
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.core.database import get_db
from app.core.redis_client import get_redis
from datetime import datetime

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    健康检查端点
    用于负载均衡器检查服务是否存活
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """
    就绪检查端点
    检查服务是否准备好接收流量（数据库和Redis连接正常）
    """
    try:
        # 检查数据库连接
        await db.execute("SELECT 1")

        # 检查Redis连接
        await redis.ping()

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "ok",
                "redis": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get("/metrics")
async def metrics():
    """
    Prometheus指标端点
    """
    # TODO: 实现Prometheus指标收集
    return {
        "message": "Metrics endpoint - to be implemented with prometheus_client"
    }
