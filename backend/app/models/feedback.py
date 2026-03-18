"""
用户反馈模型
"""
import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class FeedbackStatus(str, enum.Enum):
    """反馈状态"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    RESOLVED = "resolved"  # 已解决
    CLOSED = "closed"  # 已关闭


class FeedbackPriority(str, enum.Enum):
    """反馈优先级"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class Feedback(BaseModel):
    """用户反馈表"""
    __tablename__ = "feedback"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    title = Column(String(200), nullable=False, comment="反馈标题")
    description = Column(Text, nullable=False, comment="反馈描述")
    images = Column(JSON, nullable=True, comment="图片URL列表")
    status = Column(
        SQLEnum(FeedbackStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=FeedbackStatus.PENDING,
        comment="状态"
    )
    priority = Column(
        SQLEnum(FeedbackPriority, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=FeedbackPriority.MEDIUM,
        comment="优先级"
    )
    admin_reply = Column(Text, nullable=True, comment="管理员回复")

    # 关系
    user = relationship("User", backref="feedbacks")
