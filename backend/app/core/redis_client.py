"""
Redis连接池配置
"""
from redis import Redis, ConnectionPool
from redis.asyncio import Redis as AsyncRedis, ConnectionPool as AsyncConnectionPool
from app.core.config import settings
import urllib.parse

# 解析Redis URL
parsed_url = urllib.parse.urlparse(settings.REDIS_URL)

# 同步连接池
sync_pool = ConnectionPool(
    host=parsed_url.hostname or "localhost",
    port=parsed_url.port or 6379,
    password=settings.REDIS_PASSWORD,
    db=int(parsed_url.path.lstrip("/")) if parsed_url.path else 0,
    max_connections=50,        # 最大连接数
    socket_timeout=5,          # Socket超时（秒）
    socket_connect_timeout=5,  # 连接超时（秒）
    socket_keepalive=True,     # 启用TCP keepalive
    health_check_interval=30,  # 健康检查间隔（秒）
    decode_responses=True,     # 自动解码响应为字符串
)

# 同步Redis客户端
redis_client = Redis(connection_pool=sync_pool)

# 异步连接池
async_pool = AsyncConnectionPool(
    host=parsed_url.hostname or "localhost",
    port=parsed_url.port or 6379,
    password=settings.REDIS_PASSWORD,
    db=int(parsed_url.path.lstrip("/")) if parsed_url.path else 0,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30,
    decode_responses=True,
)

# 异步Redis客户端
async_redis_client = AsyncRedis(connection_pool=async_pool)


async def get_redis():
    """获取Redis客户端（依赖注入）"""
    return async_redis_client


def close_redis():
    """关闭Redis连接"""
    redis_client.close()
    sync_pool.disconnect()


async def close_async_redis():
    """关闭异步Redis连接"""
    await async_redis_client.close()
    await async_pool.disconnect()
