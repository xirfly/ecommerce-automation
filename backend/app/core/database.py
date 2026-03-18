"""
数据库连接池配置（纯异步）
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 异步引擎（用于 FastAPI 和 Alembic）
# 注意：异步引擎会自动使用 AsyncAdaptedQueuePool，不需要显式指定 poolclass
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,              # 连接池大小
    max_overflow=10,           # 超过pool_size后最多创建的连接数
    pool_timeout=30,           # 获取连接的超时时间（秒）
    pool_recycle=3600,         # 连接回收时间（秒），防止MySQL连接超时
    pool_pre_ping=True,        # 连接前先ping，确保连接有效
    echo=False,                # 关闭 SQL 日志打印
)

# 会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """获取数据库会话（依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
