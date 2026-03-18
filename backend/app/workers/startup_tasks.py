"""
启动时任务处理
在 Celery Worker 启动时，自动提交所有待执行的任务
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Task, TaskStatus
from app.core.logging_config import setup_logging

logger = setup_logging()


async def submit_pending_tasks():
    """提交所有待执行的任务到 Celery"""
    from app.workers.tasks import execute_task

    async with AsyncSessionLocal() as db:
        # 查询所有待执行的任务
        result = await db.execute(
            select(Task).where(Task.status == TaskStatus.PENDING)
        )
        pending_tasks = result.scalars().all()

        if not pending_tasks:
            logger.info("没有待执行的任务")
            return

        logger.info(f"发现 {len(pending_tasks)} 个待执行任务，正在提交到 Celery...")

        submitted_count = 0
        for task in pending_tasks:
            try:
                # 提交任务到 Celery
                execute_task.delay(task.id, task.task_type)
                submitted_count += 1
                logger.info(f"已提交任务 #{task.id} ({task.task_type})")
            except Exception as e:
                logger.error(f"提交任务 #{task.id} 失败: {e}")

        logger.info(f"成功提交 {submitted_count}/{len(pending_tasks)} 个任务")


def run_startup_tasks():
    """运行启动任务（同步入口）"""
    logger.info("=" * 50)
    logger.info("Celery Worker 启动任务处理")
    logger.info("=" * 50)

    # 创建事件循环并运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(submit_pending_tasks())
    finally:
        loop.close()

    logger.info("=" * 50)
    logger.info("启动任务处理完成")
    logger.info("=" * 50)
