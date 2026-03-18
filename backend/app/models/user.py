"""
用户模型
"""
from sqlalchemy import Column, String, Integer, Boolean, Enum as SQLEnum
from app.models.base import BaseModel
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(BaseModel):
    """用户表"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.VIEWER)
    team_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
