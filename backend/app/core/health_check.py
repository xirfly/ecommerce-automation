"""
启动前健康检查
检查 MySQL 和 Redis 连接
"""
import asyncio
import sys
from loguru import logger
from sqlalchemy import text
from redis.asyncio import Redis as AsyncRedis
import urllib.parse


async def check_mysql(database_url: str) -> bool:
    """检查 MySQL 连接"""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(database_url, pool_pre_ping=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        await engine.dispose()
        logger.success("[OK] MySQL connected")
        return True
    except Exception as e:
        logger.error(f"[FAIL] MySQL connection failed: {e}")
        return False


async def check_redis(redis_url: str, redis_password: str) -> bool:
    """检查 Redis 连接"""
    try:
        parsed_url = urllib.parse.urlparse(redis_url)

        redis_client = AsyncRedis(
            host=parsed_url.hostname or "localhost",
            port=parsed_url.port or 6379,
            password=redis_password if redis_password else None,
            db=int(parsed_url.path.lstrip("/")) if parsed_url.path else 0,
            socket_connect_timeout=5,
            decode_responses=True,
        )

        await redis_client.ping()
        await redis_client.close()
        logger.success("[OK] Redis connected")
        return True
    except Exception as e:
        logger.error(f"[FAIL] Redis connection failed: {e}")
        return False


async def run_health_checks(database_url: str, redis_url: str, redis_password: str) -> bool:
    """运行所有健康检查"""
    logger.debug("="*50)
    logger.debug("Health Check Before Startup")
    logger.debug("="*50)

    # Windows 平台设置事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    mysql_ok = await check_mysql(database_url)
    redis_ok = await check_redis(redis_url, redis_password)

    logger.debug("="*50)

    if mysql_ok and redis_ok:
        logger.success("[OK] All checks passed, starting server...\n")
        return True
    else:
        logger.error("[FAIL] Health check failed, please check configuration\n")
        return False
