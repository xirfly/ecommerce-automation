"""
Prometheus 监控指标
使用单例模式和延迟初始化避免重复注册
"""
from prometheus_client import Counter, Histogram, Gauge, Info, REGISTRY, CollectorRegistry
from typing import Optional
import time


class MetricsRegistry:
    """指标注册表单例"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._init_metrics()

    def _init_metrics(self):
        """初始化所有指标"""
        # 任务指标（Counter 会自动添加 _total 后缀，所以不要手动添加）
        self.task_total = self._create_counter(
            'task', 'Total number of tasks', ['task_type', 'status']
        )
        self.task_duration = self._create_histogram(
            'task_duration_seconds', 'Task execution duration in seconds',
            ['task_type'], buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]
        )
        self.task_running = self._create_gauge(
            'task_running', 'Number of currently running tasks', ['task_type']
        )
        self.task_retries = self._create_counter(
            'task_retries', 'Total number of task retries', ['task_type']
        )
        self.task_queue_length = self._create_gauge(
            'task_queue_length', 'Number of tasks in queue', ['queue_name']
        )

        # Agent 指标
        self.agent_executions = self._create_counter(
            'agent_executions', 'Total number of agent executions',
            ['agent_name', 'status']
        )
        self.agent_duration = self._create_histogram(
            'agent_duration_seconds', 'Agent execution duration in seconds',
            ['agent_name'], buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120]
        )
        self.agent_errors = self._create_counter(
            'agent_errors', 'Total number of agent errors',
            ['agent_name', 'error_type']
        )

        # API 指标
        self.http_requests = self._create_counter(
            'http_requests', 'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        self.http_request_duration = self._create_histogram(
            'http_request_duration_seconds', 'HTTP request duration in seconds',
            ['method', 'endpoint'], buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
        )
        self.http_request_size = self._create_histogram(
            'http_request_size_bytes', 'HTTP request size in bytes',
            ['method', 'endpoint'], buckets=[100, 1000, 10000, 100000, 1000000]
        )
        self.http_response_size = self._create_histogram(
            'http_response_size_bytes', 'HTTP response size in bytes',
            ['method', 'endpoint'], buckets=[100, 1000, 10000, 100000, 1000000]
        )
        self.http_active_connections = self._create_gauge(
            'http_active_connections', 'Number of active HTTP connections'
        )

        # 数据库指标
        self.db_queries = self._create_counter(
            'db_queries', 'Total number of database queries',
            ['operation', 'table']
        )
        self.db_query_duration = self._create_histogram(
            'db_query_duration_seconds', 'Database query duration in seconds',
            ['operation', 'table'], buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
        )
        self.db_pool_size = self._create_gauge(
            'db_pool_size', 'Database connection pool size'
        )
        self.db_pool_available = self._create_gauge(
            'db_pool_available', 'Available database connections in pool'
        )
        self.db_errors = self._create_counter(
            'db_errors', 'Total number of database errors', ['error_type']
        )

        # Redis 指标
        self.redis_operations = self._create_counter(
            'redis_operations', 'Total number of Redis operations',
            ['operation', 'status']
        )
        self.redis_operation_duration = self._create_histogram(
            'redis_operation_duration_seconds', 'Redis operation duration in seconds',
            ['operation'], buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
        )
        self.redis_connected = self._create_gauge(
            'redis_connected', 'Redis connection status (1=connected, 0=disconnected)'
        )

        # Celery Worker 指标
        self.celery_worker_online = self._create_gauge(
            'celery_worker_online', 'Number of online Celery workers'
        )
        self.celery_worker_tasks_processed = self._create_counter(
            'celery_worker_tasks_processed',
            'Total number of tasks processed by workers', ['worker_name']
        )

        # 业务指标
        self.products_total = self._create_gauge(
            'products_total', 'Total number of products', ['status']
        )
        self.users_total = self._create_gauge(
            'users_total', 'Total number of users', ['role']
        )
        self.sales_amount = self._create_counter(
            'sales_amount', 'Total sales amount', ['product_id']
        )
        self.sales_orders = self._create_counter(
            'sales_orders', 'Total number of orders', ['product_id']
        )
        self.feedback_total = self._create_gauge(
            'feedback_total', 'Total number of feedback items',
            ['status', 'priority']
        )
        self.notifications_sent = self._create_counter(
            'notifications_sent', 'Total number of notifications sent',
            ['channel_type', 'status']
        )

    def _create_counter(self, name, doc, labels=None):
        """创建或获取 Counter"""
        try:
            return Counter(name, doc, labels) if labels else Counter(name, doc)
        except ValueError:
            # 已存在，从注册表获取
            for collector in list(REGISTRY._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            return None

    def _create_histogram(self, name, doc, labels=None, buckets=None):
        """创建或获取 Histogram"""
        try:
            kwargs = {'buckets': buckets} if buckets else {}
            return Histogram(name, doc, labels, **kwargs) if labels else Histogram(name, doc, **kwargs)
        except ValueError:
            for collector in list(REGISTRY._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            return None

    def _create_gauge(self, name, doc, labels=None):
        """创建或获取 Gauge"""
        try:
            return Gauge(name, doc, labels) if labels else Gauge(name, doc)
        except ValueError:
            for collector in list(REGISTRY._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            return None


# 创建全局单例实例
_registry = MetricsRegistry()

# 导出所有指标
task_total = _registry.task_total
task_duration = _registry.task_duration
task_running = _registry.task_running
task_retries = _registry.task_retries
task_queue_length = _registry.task_queue_length

agent_executions = _registry.agent_executions
agent_duration = _registry.agent_duration
agent_errors = _registry.agent_errors

http_requests = _registry.http_requests
http_request_duration = _registry.http_request_duration
http_request_size = _registry.http_request_size
http_response_size = _registry.http_response_size
http_active_connections = _registry.http_active_connections

db_queries = _registry.db_queries
db_query_duration = _registry.db_query_duration
db_pool_size = _registry.db_pool_size
db_pool_available = _registry.db_pool_available
db_errors = _registry.db_errors

redis_operations = _registry.redis_operations
redis_operation_duration = _registry.redis_operation_duration
redis_connected = _registry.redis_connected

celery_worker_online = _registry.celery_worker_online
celery_worker_tasks_processed = _registry.celery_worker_tasks_processed

products_total = _registry.products_total
users_total = _registry.users_total
sales_amount = _registry.sales_amount
sales_orders = _registry.sales_orders
feedback_total = _registry.feedback_total
notifications_sent = _registry.notifications_sent


# ==================== 辅助函数 ====================

class MetricsTimer:
    """指标计时器上下文管理器"""

    def __init__(self, histogram, labels: Optional[dict] = None):
        self.histogram = histogram
        self.labels = labels or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.histogram:
            duration = time.time() - self.start_time
            if self.labels:
                self.histogram.labels(**self.labels).observe(duration)
            else:
                self.histogram.observe(duration)


def record_task_execution(task_type: str, status: str, duration: float):
    """记录任务执行"""
    if task_total:
        task_total.labels(task_type=task_type, status=status).inc()
    if task_duration:
        task_duration.labels(task_type=task_type).observe(duration)


def record_agent_execution(agent_name: str, status: str, duration: float):
    """记录 Agent 执行"""
    if agent_executions:
        agent_executions.labels(agent_name=agent_name, status=status).inc()
    if agent_duration:
        agent_duration.labels(agent_name=agent_name).observe(duration)


def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """记录 HTTP 请求"""
    if http_requests:
        http_requests.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    if http_request_duration:
        http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def record_db_query(operation: str, table: str, duration: float):
    """记录数据库查询"""
    if db_queries:
        db_queries.labels(operation=operation, table=table).inc()
    if db_query_duration:
        db_query_duration.labels(operation=operation, table=table).observe(duration)


def record_redis_operation(operation: str, status: str, duration: float):
    """记录 Redis 操作"""
    if redis_operations:
        redis_operations.labels(operation=operation, status=status).inc()
    if redis_operation_duration:
        redis_operation_duration.labels(operation=operation).observe(duration)
