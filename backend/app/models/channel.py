"""
渠道模型
支持电商平台和通知渠道的配置管理
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ChannelType(str, enum.Enum):
    """渠道类型"""
    ECOMMERCE = "ecommerce"  # 电商平台
    NOTIFICATION = "notification"  # 通知渠道


class ChannelStatus(str, enum.Enum):
    """渠道状态"""
    ACTIVE = "active"  # 启用
    INACTIVE = "inactive"  # 禁用
    ERROR = "error"  # 错误


class Channel(BaseModel):
    """渠道配置表"""
    __tablename__ = "channels"

    name = Column(String(100), nullable=False, comment="渠道名称")
    channel_type = Column(
        SQLEnum(ChannelType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="渠道类型"
    )
    platform = Column(String(50), nullable=False, comment="平台标识（taobao/jd/lark/telegram等）")
    description = Column(Text, nullable=True, comment="渠道描述")

    # 配置信息（JSON 格式存储）
    config = Column(JSON, nullable=False, comment="渠道配置（API密钥、Webhook等）")

    # 状态
    status = Column(
        SQLEnum(ChannelStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ChannelStatus.ACTIVE,
        comment="渠道状态"
    )
    is_default = Column(Boolean, default=False, comment="是否为默认渠道")

    # 统计信息
    usage_count = Column(Integer, default=0, comment="使用次数")
    last_used_at = Column(String(50), nullable=True, comment="最后使用时间")
    last_error = Column(Text, nullable=True, comment="最后错误信息")

    # 创建者
    created_by = Column(Integer, nullable=False, comment="创建者ID")

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, platform={self.platform}, status={self.status})>"
