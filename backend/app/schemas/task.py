"""
任务相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class TaskCreate(BaseModel):
    """创建任务请求"""
    product_id: int = Field(..., description="产品ID")
    task_type: str = Field(..., description="任务类型")


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    task_id: str
    product_id: int
    task_type: str
    status: str
    progress: int
    result: Optional[Any]
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskLogResponse(BaseModel):
    """任务日志响应"""
    id: int
    task_id: int
    agent_name: str
    log_level: str
    message: str
    extra_data: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskRetryRequest(BaseModel):
    """任务重试请求"""
    task_id: int = Field(..., description="任务ID")
