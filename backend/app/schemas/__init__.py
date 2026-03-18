"""
Schema模块初始化
"""
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo, CurrentUser
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    BatchDeleteRequest,
)
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskLogResponse,
    TaskRetryRequest,
)
from app.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelTestRequest,
    ChannelTestResponse,
    ChannelStatistics,
)
from app.schemas.system_config import (
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigResponse,
    SystemConfigBatchUpdate,
    SystemSettingsResponse,
)
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
    FeedbackResponse,
    FeedbackListResponse,
)
from app.schemas.common import Response, ErrorResponse

__all__ = [
    'LoginRequest',
    'LoginResponse',
    'UserInfo',
    'CurrentUser',
    'ProductCreate',
    'ProductUpdate',
    'ProductResponse',
    'ProductListResponse',
    'BatchDeleteRequest',
    'TaskCreate',
    'TaskResponse',
    'TaskListResponse',
    'TaskLogResponse',
    'TaskRetryRequest',
    'ChannelCreate',
    'ChannelUpdate',
    'ChannelResponse',
    'ChannelTestRequest',
    'ChannelTestResponse',
    'ChannelStatistics',
    'SystemConfigCreate',
    'SystemConfigUpdate',
    'SystemConfigResponse',
    'SystemConfigBatchUpdate',
    'SystemSettingsResponse',
    'FeedbackCreateRequest',
    'FeedbackUpdateRequest',
    'FeedbackResponse',
    'FeedbackListResponse',
    'Response',
    'ErrorResponse',
]
