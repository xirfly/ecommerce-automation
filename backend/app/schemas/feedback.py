"""
用户反馈相关的 Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    """创建反馈请求"""
    title: str = Field(..., min_length=1, max_length=200, description="反馈标题")
    description: str = Field(..., min_length=1, description="反馈描述")
    images: Optional[List[str]] = Field(default=None, description="图片URL列表")


class FeedbackUpdateRequest(BaseModel):
    """更新反馈请求（管理员）"""
    status: Optional[str] = Field(None, description="状态")
    priority: Optional[str] = Field(None, description="优先级")
    admin_reply: Optional[str] = Field(None, description="管理员回复")


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    user_id: int
    username: Optional[str] = None  # 用户名（关联查询）
    title: str
    description: str
    images: Optional[List[str]] = None
    status: str
    priority: str
    admin_reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackListResponse(BaseModel):
    """反馈列表响应"""
    items: List[FeedbackResponse]
    total: int
    page: int
    page_size: int
