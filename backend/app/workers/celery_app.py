"""
Celery 应用配置
"""
from celery import Celery
from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()

# 创建 Celery 应用
celery_app = Celery(
    "ecommerce_automation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,

    # 任务结果过期时间（秒）
    result_expires=3600,

    # 任务执行时间限制（秒）
    task_time_limit=1800,  # 30分钟
    task_soft_time_limit=1500,  # 25分钟软限制

    # 任务重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # 任务优先级
    task_default_priority=5,

    # Broker 连接池配置
    broker_pool_limit=10,
    broker_connection_max_retries=10,

    # 结果后端配置
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },

    # Celery 6.0 新配置：启动时自动重连
    broker_connection_retry_on_startup=True,
)

logger.info("Celery 应用已初始化")
