"""
系统配置模型
存储系统级别的配置信息
"""
from sqlalchemy import Column, String, Text, Boolean, Integer
from app.models.base import BaseModel


class SystemConfig(BaseModel):
    """系统配置表"""
    __tablename__ = "system_configs"

    config_key = Column(String(100), nullable=False, unique=True, comment="配置键")
    config_value = Column(Text, nullable=True, comment="配置值")
    config_type = Column(String(20), nullable=False, default="string", comment="配置类型（string/int/bool/json）")
    category = Column(String(50), nullable=False, comment="配置分类（basic/ai/task/notification/security）")
    description = Column(Text, nullable=True, comment="配置描述")
    is_public = Column(Boolean, default=False, comment="是否公开（前端可见）")
    is_encrypted = Column(Boolean, default=False, comment="是否加密存储")

    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, category={self.category})>"
