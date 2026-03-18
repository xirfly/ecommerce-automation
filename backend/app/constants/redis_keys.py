"""
Redis键名常量管理类

统一管理所有Redis键名模板，便于后续修改和维护。
"""


class RedisKeys:
    """Redis键名常量"""

    # ==================== 缓存相关 ====================

    @staticmethod
    def cache_product(product_id: int) -> str:
        """产品信息缓存

        Args:
            product_id: 产品ID

        Returns:
            cache:product:{product_id}
        """
        return f"cache:product:{product_id}"

    @staticmethod
    def cache_user(user_id: int) -> str:
        """用户信息缓存

        Args:
            user_id: 用户ID

        Returns:
            cache:user:{user_id}
        """
        return f"cache:user:{user_id}"

    @staticmethod
    def cache_channel(channel_id: int) -> str:
        """渠道配置缓存

        Args:
            channel_id: 渠道ID

        Returns:
            cache:channel:{channel_id}
        """
        return f"cache:channel:{channel_id}"

    # ==================== Celery任务队列 ====================

    @staticmethod
    def celery_queue(queue_name: str = "default") -> str:
        """Celery任务队列

        Args:
            queue_name: 队列名称（default/agent/report）

        Returns:
            celery:queue:{queue_name}
        """
        return f"celery:queue:{queue_name}"

    @staticmethod
    def celery_result(task_id: str) -> str:
        """Celery任务结果

        Args:
            task_id: 任务ID

        Returns:
            celery:result:{task_id}
        """
        return f"celery:result:{task_id}"

    # ==================== 会话管理 ====================

    @staticmethod
    def session_user(user_id: int, token_id: str) -> str:
        """用户会话（JWT Token）

        Args:
            user_id: 用户ID
            token_id: Token ID

        Returns:
            session:user:{user_id}:{token_id}
        """
        return f"session:user:{user_id}:{token_id}"

    @staticmethod
    def session_openclaw(session_id: str) -> str:
        """OpenClaw Gateway会话

        Args:
            session_id: 会话ID

        Returns:
            session:openclaw:{session_id}
        """
        return f"session:openclaw:{session_id}"

    # ==================== 限流控制 ====================

    @staticmethod
    def ratelimit_user(user_id: int, endpoint: str) -> str:
        """用户级限流

        Args:
            user_id: 用户ID
            endpoint: API端点

        Returns:
            ratelimit:user:{user_id}:{endpoint}
        """
        return f"ratelimit:user:{user_id}:{endpoint}"

    @staticmethod
    def ratelimit_ip(ip_address: str) -> str:
        """IP级限流

        Args:
            ip_address: IP地址

        Returns:
            ratelimit:ip:{ip_address}
        """
        return f"ratelimit:ip:{ip_address}"

    # ==================== Agent记忆 ====================

    @staticmethod
    def memory_agent(session_id: str) -> str:
        """Agent短期记忆

        Args:
            session_id: 会话ID

        Returns:
            memory:agent:{session_id}
        """
        return f"memory:agent:{session_id}"

    # ==================== 锁机制 ====================

    @staticmethod
    def lock_product(product_id: int) -> str:
        """产品操作锁

        Args:
            product_id: 产品ID

        Returns:
            lock:product:{product_id}
        """
        return f"lock:product:{product_id}"

    @staticmethod
    def lock_task(task_id: str) -> str:
        """任务执行锁

        Args:
            task_id: 任务ID

        Returns:
            lock:task:{task_id}
        """
        return f"lock:task:{task_id}"

    # ==================== 统计计数 ====================

    @staticmethod
    def counter_product_views(product_id: int) -> str:
        """产品浏览次数

        Args:
            product_id: 产品ID

        Returns:
            counter:product:views:{product_id}
        """
        return f"counter:product:views:{product_id}"

    @staticmethod
    def counter_task_total(date: str) -> str:
        """每日任务总数

        Args:
            date: 日期（YYYY-MM-DD）

        Returns:
            counter:task:total:{date}
        """
        return f"counter:task:total:{date}"

    # ==================== 工具方法 ====================

    @staticmethod
    def pattern_cache_all() -> str:
        """所有缓存键的匹配模式"""
        return "cache:*"

    @staticmethod
    def pattern_session_user_all(user_id: int) -> str:
        """某用户所有会话的匹配模式"""
        return f"session:user:{user_id}:*"

    @staticmethod
    def pattern_ratelimit_user_all(user_id: int) -> str:
        """某用户所有限流键的匹配模式"""
        return f"ratelimit:user:{user_id}:*"


class RedisTTL:
    """Redis键过期时间常量（秒）"""

    # 缓存TTL
    CACHE_PRODUCT = 300  # 5分钟
    CACHE_USER = 600  # 10分钟
    CACHE_CHANNEL = 600  # 10分钟

    # 会话TTL
    SESSION_USER = 86400  # 24小时
    SESSION_OPENCLAW = 3600  # 1小时

    # 限流TTL
    RATELIMIT = 60  # 1分钟

    # Agent记忆TTL
    MEMORY_AGENT = 3600  # 1小时

    # 锁TTL
    LOCK_DEFAULT = 30  # 30秒
    LOCK_TASK = 300  # 5分钟（任务执行时间较长）

    # 计数器TTL
    COUNTER_DAILY = 86400  # 24小时


class RedisDB:
    """Redis数据库编号"""

    DEFAULT = 0  # 默认数据库（缓存、会话）
    CELERY = 1  # Celery任务队列
    CACHE = 2  # 专用缓存数据库（可选）


# 使用示例
if __name__ == "__main__":
    # 生成键名
    product_key = RedisKeys.cache_product(123)
    print(f"产品缓存键: {product_key}")

    user_session_key = RedisKeys.session_user(1, "abc123")
    print(f"用户会话键: {user_session_key}")

    ratelimit_key = RedisKeys.ratelimit_user(1, "/api/products")
    print(f"限流键: {ratelimit_key}")

    # 获取TTL
    print(f"产品缓存TTL: {RedisTTL.CACHE_PRODUCT}秒")
    print(f"用户会话TTL: {RedisTTL.SESSION_USER}秒")

    # 匹配模式
    print(f"所有缓存键: {RedisKeys.pattern_cache_all()}")
    print(f"用户1的所有会话: {RedisKeys.pattern_session_user_all(1)}")
