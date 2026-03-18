"""
渠道相关的 Pydantic Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class ChannelBase(BaseModel):
    """渠道基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="渠道名称")
    channel_type: str = Field(..., description="渠道类型（ecommerce/notification）")
    platform: str = Field(..., min_length=1, max_length=50, description="平台标识")
    description: Optional[str] = Field(None, description="渠道描述")
    config: Dict[str, Any] = Field(..., description="渠道配置")
    is_default: bool = Field(False, description="是否为默认渠道")

    @field_validator('channel_type')
    @classmethod
    def validate_channel_type(cls, v):
        if v not in ['ecommerce', 'notification']:
            raise ValueError('channel_type 必须是 ecommerce 或 notification')
        return v


class ChannelCreate(ChannelBase):
    """创建渠道 Schema"""
    pass


class ChannelUpdate(BaseModel):
    """更新渠道 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, description="渠道状态（active/inactive/error）")
    is_default: Optional[bool] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ['active', 'inactive', 'error']:
            raise ValueError('status 必须是 active、inactive 或 error')
        return v


class ChannelResponse(ChannelBase):
    """渠道响应 Schema"""
    id: int
    status: str
    usage_count: int
    last_used_at: Optional[str]
    last_error: Optional[str]
    created_by: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ChannelTestRequest(BaseModel):
    """测试渠道连接请求"""
    channel_id: int = Field(..., description="渠道ID")


class ChannelTestResponse(BaseModel):
    """测试渠道连接响应"""
    success: bool = Field(..., description="测试是否成功")
    message: str = Field(..., description="测试结果消息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


class ChannelStatistics(BaseModel):
    """渠道统计信息"""
    total_channels: int = Field(..., description="总渠道数")
    active_channels: int = Field(..., description="启用的渠道数")
    ecommerce_channels: int = Field(..., description="电商平台渠道数")
    notification_channels: int = Field(..., description="通知渠道数")
    total_usage: int = Field(..., description="总使用次数")
