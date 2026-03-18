"""
模型模块初始化
"""
from app.models.base import Base, BaseModel
from app.models.user import User, UserRole
from app.models.product import Product, ProductStatus
from app.models.task import Task, TaskLog, TaskStatus, TaskType, LogLevel
from app.models.channel import Channel, ChannelType, ChannelStatus
from app.models.system_config import SystemConfig
from app.models.feedback import Feedback, FeedbackStatus, FeedbackPriority
from app.models.sales_data import SalesData

__all__ = [
    'Base',
    'BaseModel',
    'User',
    'UserRole',
    'Product',
    'ProductStatus',
    'Task',
    'TaskLog',
    'TaskStatus',
    'TaskType',
    'LogLevel',
    'Channel',
    'ChannelType',
    'ChannelStatus',
    'SystemConfig',
    'Feedback',
    'FeedbackStatus',
    'FeedbackPriority',
    'SalesData',
]
