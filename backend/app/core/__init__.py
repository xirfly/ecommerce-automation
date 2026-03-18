"""
核心基础设施模块
包含配置、数据库、Redis、日志等核心组件
"""
from app.core.config import settings
from app.core.database import get_db, AsyncSessionLocal
from app.core.redis_client import async_redis_client, redis_client, get_redis
from app.core.logging_config import setup_logging

__all__ = [
    "settings",
    "get_db",
    "AsyncSessionLocal",
    "async_redis_client",
    "redis_client",
    "get_redis",
    "setup_logging",
]
