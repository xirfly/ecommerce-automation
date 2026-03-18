"""
应用配置模块
从环境变量读取配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str
    MYSQL_ROOT_PASSWORD: str
    MYSQL_USER_PASSWORD: str

    # Redis配置
    REDIS_URL: str
    REDIS_PASSWORD: str

    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # OpenClaw配置
    OPENCLAW_API_URL: str = "http://localhost:3000"
    OPENCLAW_API_KEY: str = ""

    # CORS配置
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/var/log/ecommerce/app.log"

    # Celery配置
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_WORKER_CONCURRENCY: int = 4

    # AI服务配置
    AI_SERVICE_TYPE: str = "mock"  # mock/openai
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"

    # 飞书配置
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""
    FEISHU_VERIFICATION_TOKEN: str = ""
    FEISHU_ENCRYPT_KEY: str = ""

    # Telegram配置
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    # 企业微信配置
    WECOM_CORP_ID: str = ""
    WECOM_AGENT_ID: str = ""
    WECOM_SECRET: str = ""

    # 监控配置
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3001

    @property
    def cors_origins_list(self) -> List[str]:
        """获取CORS允许的源列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量


# 全局配置实例
settings = Settings()
