"""
安全中间件
包含CORS、速率限制、SQL注入防护等
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis as AsyncRedis
import time
from typing import Callable
from app.core.config import settings


def setup_cors(app: FastAPI):
    """配置CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
        max_age=3600,
    )


# 添加一个自定义中间件来确保所有响应都有 CORS 头
class CORSFixMiddleware(BaseHTTPMiddleware):
    """确保所有响应都包含 CORS 头的中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        # 处理 OPTIONS 预检请求
        if request.method == "OPTIONS":
            response = JSONResponse(content={})
            response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
            return response

        # 处理正常请求
        response = await call_next(request)

        # 确保响应包含 CORS 头
        origin = request.headers.get("origin")
        if origin and origin in settings.cors_origins_list:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response


def setup_trusted_hosts(app: FastAPI):
    """配置可信主机"""
    if settings.APP_ENV == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.yourdomain.com", "yourdomain.com"]
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """API速率限制中间件"""

    def __init__(self, app: FastAPI, redis_client: AsyncRedis):
        super().__init__(app)
        self.redis = redis_client
        # 默认限制：每分钟60次请求
        self.default_limit = 60
        self.window = 60  # 时间窗口（秒）

    async def dispatch(self, request: Request, call_next: Callable):
        # 获取客户端IP
        client_ip = request.client.host

        # 跳过健康检查端点
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)

        # 构建限流key
        rate_limit_key = f"rate_limit:{client_ip}:{request.url.path}"

        try:
            # 获取当前请求次数（异步）
            current = await self.redis.get(rate_limit_key)

            if current is None:
                # 首次请求，设置计数器（异步）
                await self.redis.setex(rate_limit_key, self.window, 1)
            else:
                current_count = int(current)

                if current_count >= self.default_limit:
                    # 超过限制
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="请求过于频繁，请稍后再试"
                    )

                # 增加计数（异步）
                await self.redis.incr(rate_limit_key)

            # 继续处理请求
            response = await call_next(request)

            # 添加速率限制响应头
            response.headers["X-RateLimit-Limit"] = str(self.default_limit)
            current_val = await self.redis.get(rate_limit_key)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, self.default_limit - int(current_val or 0))
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            # Redis故障时不阻塞请求
            import traceback
            print(f"Rate limit error: {e}")
            print(traceback.format_exc())
            return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


def sanitize_sql_input(value: str) -> str:
    """
    SQL注入防护 - 清理用户输入
    注意：这只是额外的防护层，主要防护应该使用参数化查询
    """
    if not isinstance(value, str):
        return value

    # 危险字符列表
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_", "exec", "execute"]

    # 检查是否包含危险字符
    for char in dangerous_chars:
        if char.lower() in value.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="输入包含非法字符"
            )

    return value


def validate_input_length(value: str, max_length: int = 1000) -> str:
    """验证输入长度，防止DoS攻击"""
    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"输入长度超过限制（最大{max_length}字符）"
        )
    return value


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        # 记录请求信息
        print(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # 记录响应信息
        print(f"Response: {response.status_code} - {process_time:.3f}s")

        return response


def setup_security_middleware(app: FastAPI, redis_client: AsyncRedis):
    """配置所有安全中间件"""
    # CORS - 必须最先添加
    setup_cors(app)

    # 添加 CORS 修复中间件，确保所有响应都有 CORS 头
    app.add_middleware(CORSFixMiddleware)

    # 可信主机
    setup_trusted_hosts(app)

    # 速率限制（暂时禁用以便测试）
    # app.add_middleware(RateLimitMiddleware, redis_client=redis_client)

    # 安全响应头
    app.add_middleware(SecurityHeadersMiddleware)

    # 请求日志
    app.add_middleware(RequestLoggingMiddleware)
