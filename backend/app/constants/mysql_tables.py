"""
MySQL表名常量管理类

统一管理所有MySQL表名，便于后续修改和维护。
"""


class MySQLTables:
    """MySQL表名常量"""

    # 用户相关
    USERS = "users"

    # 产品相关
    PRODUCTS = "products"

    # 任务相关
    TASKS = "tasks"
    TASK_LOGS = "task_logs"

    # 渠道相关
    CHANNELS = "channels"

    # Agent记忆
    AGENT_MEMORY = "agent_memory"

    # 销售数据
    SALES_DATA = "sales_data"

    @classmethod
    def all_tables(cls) -> list[str]:
        """获取所有表名"""
        return [
            cls.USERS,
            cls.PRODUCTS,
            cls.TASKS,
            cls.TASK_LOGS,
            cls.CHANNELS,
            cls.AGENT_MEMORY,
            cls.SALES_DATA,
        ]

    @classmethod
    def get_table_comment(cls, table_name: str) -> str:
        """获取表注释"""
        comments = {
            cls.USERS: "用户表",
            cls.PRODUCTS: "产品表",
            cls.TASKS: "任务表",
            cls.TASK_LOGS: "任务日志表",
            cls.CHANNELS: "渠道配置表",
            cls.AGENT_MEMORY: "Agent记忆表",
            cls.SALES_DATA: "销售数据表",
        }
        return comments.get(table_name, "")


class MySQLColumns:
    """MySQL列名常量（可选，用于复杂查询）"""

    class Users:
        """users表列名"""
        ID = "id"
        USERNAME = "username"
        PASSWORD_HASH = "password_hash"
        EMAIL = "email"
        ROLE = "role"
        TEAM_ID = "team_id"
        IS_ACTIVE = "is_active"
        LAST_LOGIN_AT = "last_login_at"
        CREATED_AT = "created_at"
        UPDATED_AT = "updated_at"

    class Products:
        """products表列名"""
        ID = "id"
        NAME = "name"
        CATEGORY = "category"
        PRICE = "price"
        COST = "cost"
        STATUS = "status"
        TARGET_PLATFORMS = "target_platforms"
        PLATFORM_PRODUCT_IDS = "platform_product_ids"
        DETAIL_PAGE_URL = "detail_page_url"
        IMAGES = "images"
        VIDEOS = "videos"
        DESCRIPTION = "description"
        CREATED_BY = "created_by"
        CREATED_AT = "created_at"
        UPDATED_AT = "updated_at"

    class Tasks:
        """tasks表列名"""
        ID = "id"
        TASK_UUID = "task_uuid"
        PRODUCT_ID = "product_id"
        TASK_TYPE = "task_type"
        STATUS = "status"
        INPUT_DATA = "input_data"
        OUTPUT_DATA = "output_data"
        ERROR_MESSAGE = "error_message"
        RETRY_COUNT = "retry_count"
        DURATION_MS = "duration_ms"
        STARTED_AT = "started_at"
        COMPLETED_AT = "completed_at"
        CREATED_BY = "created_by"
        CREATED_AT = "created_at"
        UPDATED_AT = "updated_at"

    class TaskLogs:
        """task_logs表列名"""
        ID = "id"
        TASK_ID = "task_id"
        LOG_LEVEL = "log_level"
        MESSAGE = "message"
        EXTRA_DATA = "extra_data"
        CREATED_AT = "created_at"

    class Channels:
        """channels表列名"""
        ID = "id"
        NAME = "name"
        TYPE = "type"
        CONFIG = "config"
        ROUTING_RULES = "routing_rules"
        IS_ENABLED = "is_enabled"
        CREATED_BY = "created_by"
        CREATED_AT = "created_at"
        UPDATED_AT = "updated_at"

    class AgentMemory:
        """agent_memory表列名"""
        ID = "id"
        SESSION_ID = "session_id"
        AGENT_NAME = "agent_name"
        MEMORY_TYPE = "memory_type"
        MEMORY_DATA = "memory_data"
        IMPORTANCE = "importance"
        EXPIRES_AT = "expires_at"
        CREATED_AT = "created_at"

    class SalesData:
        """sales_data表列名"""
        ID = "id"
        PRODUCT_ID = "product_id"
        PLATFORM = "platform"
        DATE = "date"
        ORDER_COUNT = "order_count"
        SALES_VOLUME = "sales_volume"
        REVENUE = "revenue"
        COST = "cost"
        PROFIT = "profit"
        CREATED_AT = "created_at"
        UPDATED_AT = "updated_at"


# 使用示例
if __name__ == "__main__":
    # 获取表名
    print(f"用户表: {MySQLTables.USERS}")
    print(f"产品表: {MySQLTables.PRODUCTS}")

    # 获取所有表名
    print(f"所有表: {MySQLTables.all_tables()}")

    # 获取列名
    print(f"用户ID列: {MySQLColumns.Users.ID}")
    print(f"产品名称列: {MySQLColumns.Products.NAME}")
