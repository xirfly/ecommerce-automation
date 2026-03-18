"""
系统配置相关的 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class SystemConfigBase(BaseModel):
    """系统配置基础 Schema"""
    config_key: str = Field(..., min_length=1, max_length=100, description="配置键")
    config_value: Optional[str] = Field(None, description="配置值")
    config_type: str = Field("string", description="配置类型（string/int/bool/json）")
    category: str = Field(..., description="配置分类")
    description: Optional[str] = Field(None, description="配置描述")
    is_public: bool = Field(False, description="是否公开")
    is_encrypted: bool = Field(False, description="是否加密")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置 Schema"""
    pass


class SystemConfigUpdate(BaseModel):
    """更新系统配置 Schema"""
    config_value: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SystemConfigResponse(SystemConfigBase):
    """系统配置响应 Schema"""
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SystemConfigBatchUpdate(BaseModel):
    """批量更新系统配置 Schema"""
    configs: List[Dict[str, Any]] = Field(..., description="配置列表")


class SystemSettingsResponse(BaseModel):
    """系统设置响应 Schema（按分类组织）"""
    basic: Dict[str, Any] = Field(default_factory=dict, description="基本设置")
    ai: Dict[str, Any] = Field(default_factory=dict, description="AI服务配置")
    task: Dict[str, Any] = Field(default_factory=dict, description="任务配置")
    notification: Dict[str, Any] = Field(default_factory=dict, description="通知配置")
    security: Dict[str, Any] = Field(default_factory=dict, description="安全设置")
