"""
启动脚本
从backend目录运行: python run.py
"""
import asyncio
import sys
import uvicorn
from loguru import logger
from app.core.config import settings
from app.core.health_check import run_health_checks

# Windows 平台需要设置事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    # 启动前健康检查
    health_ok = asyncio.run(run_health_checks(
        settings.DATABASE_URL,
        settings.REDIS_URL,
        settings.REDIS_PASSWORD
    ))

    if not health_ok:
        logger.warning("启动失败：健康检查未通过")
        sys.exit(1)

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level="info",
    )
