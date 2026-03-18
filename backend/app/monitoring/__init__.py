"""
监控模块
"""
from app.monitoring.metrics import (
    # 任务指标
    task_total,
    task_duration,
    task_running,
    task_retries,
    task_queue_length,
    # Agent 指标
    agent_executions,
    agent_duration,
    agent_errors,
    # API 指标
    http_requests,
    http_request_duration,
    http_request_size,
    http_response_size,
    http_active_connections,
    # 数据库指标
    db_queries,
    db_query_duration,
    db_pool_size,
    db_pool_available,
    db_errors,
    # Redis 指标
    redis_operations,
    redis_operation_duration,
    redis_connected,
    # Celery 指标
    celery_worker_online,
    celery_worker_tasks_processed,
    # 业务指标
    products_total,
    users_total,
    sales_amount,
    sales_orders,
    feedback_total,
    notifications_sent,
    # 辅助函数
    MetricsTimer,
    record_task_execution,
    record_agent_execution,
    record_http_request,
    record_db_query,
    record_redis_operation,
)

__all__ = [
    # 任务指标
    'task_total',
    'task_duration',
    'task_running',
    'task_retries',
    'task_queue_length',
    # Agent 指标
    'agent_executions',
    'agent_duration',
    'agent_errors',
    # API 指标
    'http_requests',
    'http_request_duration',
    'http_request_size',
    'http_response_size',
    'http_active_connections',
    # 数据库指标
    'db_queries',
    'db_query_duration',
    'db_pool_size',
    'db_pool_available',
    'db_errors',
    # Redis 指标
    'redis_operations',
    'redis_operation_duration',
    'redis_connected',
    # Celery 指标
    'celery_worker_online',
    'celery_worker_tasks_processed',
    # 业务指标
    'products_total',
    'users_total',
    'sales_amount',
    'sales_orders',
    'feedback_total',
    'notifications_sent',
    # 辅助函数
    'MetricsTimer',
    'record_task_execution',
    'record_agent_execution',
    'record_http_request',
    'record_db_query',
    'record_redis_operation',
]
