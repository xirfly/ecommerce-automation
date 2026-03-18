"""
日志配置模块
"""
import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    """拦截标准logging日志，转发到loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """配置日志系统"""

    # 移除默认handler
    logger.remove()

    # 控制台输出（开发环境）
    if settings.APP_DEBUG:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True,
        )

    # 文件输出
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 普通日志
    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="100 MB",  # 日志轮转：文件大小超过100MB
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
        enqueue=True,  # 异步写入
    )

    # 错误日志单独记录
    logger.add(
        settings.LOG_FILE.replace(".log", "_error.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="zip",
        enqueue=True,
        backtrace=True,  # 显示完整堆栈
        diagnose=True,  # 显示变量值
    )

    # 拦截标准logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 拦截uvicorn日志
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

    return logger


def mask_sensitive_data(data: dict) -> dict:
    """脱敏敏感信息"""
    sensitive_keys = ["password", "token", "secret", "api_key", "access_token"]
    masked_data = data.copy()

    for key in masked_data:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            masked_data[key] = "***MASKED***"

    return masked_data
