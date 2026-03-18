"""
FastAPI主应用
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.middleware.security import setup_security_middleware
from app.monitoring.middleware import PrometheusMiddleware
from app.core.redis_client import async_redis_client, close_redis, close_async_redis
from app.api.v1 import auth, products, tasks, analytics, agents, channels as channels_v1, settings as settings_api, users, feedback, sales, monitoring
from app.api import channels as webhook_channels
from app.api.webhooks import alertmanager as alertmanager_webhook
from app.websocket import routes as websocket
from app.core.logging_config import setup_logging

# 导入 Celery 任务以确保任务被注册
from app.workers import tasks as celery_tasks  # noqa: F401

# 设置日志
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("应用启动中...")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"调试模式: {settings.APP_DEBUG}")

    yield

    # 关闭时
    logger.info("应用关闭中...")
    close_redis()
    await close_async_redis()
    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="电商自动化管理系统",
    description="基于OpenClaw框架的智能电商自动化系统",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# 配置安全中间件（使用异步 Redis）
setup_security_middleware(app, async_redis_client)

# 添加 Prometheus 监控中间件
app.add_middleware(PrometheusMiddleware)

# 注册路由
app.include_router(monitoring.router)  # 监控 API（需要在最前面，/metrics 端点无需认证）
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(tasks.router)
app.include_router(analytics.router)
app.include_router(agents.router)
app.include_router(channels_v1.router)  # 渠道管理 API
app.include_router(settings_api.router)  # 系统设置 API
app.include_router(users.router)  # 用户管理 API
app.include_router(feedback.router)  # 反馈 API
app.include_router(sales.router)  # 销售数据 API
app.include_router(websocket.router)
app.include_router(webhook_channels.router)  # Webhook 回调
app.include_router(alertmanager_webhook.router)  # AlertManager Webhook

# 配置静态文件服务（用于访问上传的图片）
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.APP_DEBUG else None,
        },
    )


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "电商自动化管理系统",
        "version": "1.0.0",
        "status": "running",
    }


# 测试端点（无需认证）
@app.get("/test")
async def test():
    """测试端点"""
    return {"message": "test ok"}


# 测试登录端点（简化版）
@app.post("/test-login")
async def test_login():
    """测试登录端点"""
    return {"message": "login test ok"}


# 健康检查（已在health.py中定义，这里导入）
from app.api.health import router as health_router
app.include_router(health_router)
