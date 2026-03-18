"""
任务模型
"""
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from enum import Enum
from app.models.base import BaseModel


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskType(str, Enum):
    """任务类型"""
    PRODUCT_ANALYSIS = "product_analysis"      # 选品分析
    CONTENT_GENERATION = "content_generation"  # 内容生成
    IMAGE_GENERATION = "image_generation"      # 图片生成
    VIDEO_GENERATION = "video_generation"      # 视频生成
    REVIEW = "review"                          # 内容审核
    PUBLISH = "publish"                        # 发布上架


class Task(BaseModel):
    """任务表"""
    __tablename__ = "tasks"

    task_id = Column(String(100), unique=True, nullable=False, comment="Celery任务ID")
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, comment="产品ID")
    task_type = Column(String(50), nullable=False, comment="任务类型")
    status = Column(
        SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TaskStatus.PENDING,
        comment="状态"
    )
    progress = Column(Integer, nullable=False, default=0, comment="进度(0-100)")
    result = Column(JSON, nullable=True, comment="任务结果")
    error_message = Column(Text, nullable=True, comment="错误信息")
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")
    started_at = Column(TIMESTAMP, nullable=True, comment="开始时间")
    completed_at = Column(TIMESTAMP, nullable=True, comment="完成时间")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, comment="创建人")

    # 关系
    product = relationship("Product", back_populates="tasks")
    creator = relationship("User", foreign_keys=[created_by])
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class TaskLog(BaseModel):
    """任务日志表"""
    __tablename__ = "task_logs"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, comment="任务ID")
    agent_name = Column(String(50), nullable=False, comment="Agent名称")
    log_level = Column(
        SQLEnum(LogLevel, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=LogLevel.INFO,
        comment="日志级别"
    )
    message = Column(Text, nullable=False, comment="日志内容")
    extra_data = Column(JSON, nullable=True, comment="额外数据")

    # 关系
    task = relationship("Task", back_populates="logs")
