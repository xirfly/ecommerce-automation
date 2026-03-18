"""
Prometheus 监控中间件
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import time

from app.monitoring.metrics import (
    http_requests,
    http_request_duration,
    http_request_size,
    http_response_size,
    http_active_connections,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus 监控中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        # 跳过 metrics 端点本身
        if request.url.path == "/metrics":
            return await call_next(request)

        # 增加活跃连接数
        http_active_connections.inc()

        # 记录请求大小
        content_length = request.headers.get("content-length")
        if content_length:
            http_request_size.labels(
                method=request.method,
                endpoint=self._get_endpoint_pattern(request.url.path)
            ).observe(int(content_length))

        # 记录开始时间
        start_time = time.time()

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时长
            duration = time.time() - start_time

            # 获取端点模式（去除动态参数）
            endpoint = self._get_endpoint_pattern(request.url.path)

            # 记录请求指标
            http_requests.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()

            http_request_duration.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)

            # 记录响应大小
            if hasattr(response, 'headers'):
                content_length = response.headers.get("content-length")
                if content_length:
                    http_response_size.labels(
                        method=request.method,
                        endpoint=endpoint
                    ).observe(int(content_length))

            return response

        finally:
            # 减少活跃连接数
            http_active_connections.dec()

    def _get_endpoint_pattern(self, path: str) -> str:
        """
        获取端点模式，将动态参数替换为占位符
        例如：/api/v1/products/123 -> /api/v1/products/{id}
        """
        # 跳过静态文件和特殊端点
        if path.startswith("/static") or path.startswith("/uploads"):
            return path

        # 简单的模式匹配
        parts = path.split("/")
        normalized_parts = []

        for i, part in enumerate(parts):
            # 如果是数字，替换为 {id}
            if part.isdigit():
                normalized_parts.append("{id}")
            # 如果是 UUID 格式，替换为 {uuid}
            elif len(part) == 36 and part.count("-") == 4:
                normalized_parts.append("{uuid}")
            else:
                normalized_parts.append(part)

        return "/".join(normalized_parts)
