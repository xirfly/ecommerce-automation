"""
数据模型基类
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime, timezone, timedelta

Base = declarative_base()

# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))


def get_beijing_time():
    """获取北京时间"""
    return datetime.now(BEIJING_TZ)


class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=get_beijing_time, nullable=False)
    updated_at = Column(DateTime, default=get_beijing_time, onupdate=get_beijing_time, nullable=False)
