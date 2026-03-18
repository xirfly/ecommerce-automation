"""
通用响应Schema
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: Optional[str] = None
