"""
认证相关Schema
"""
from pydantic import BaseModel, Field
from typing import List


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    role: str


class CurrentUser(BaseModel):
    """当前用户详细信息"""
    id: int
    username: str
    email: str | None
    role: str
    permissions: List[str]

    class Config:
        from_attributes = True
