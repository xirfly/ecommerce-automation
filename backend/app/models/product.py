"""
产品模型
"""
from sqlalchemy import Column, String, Integer, Numeric, Enum as SQLEnum, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ProductStatus(str, enum.Enum):
    """产品状态枚举"""
    DRAFT = "draft"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    PUBLISHED = "published"
    OFFLINE = "offline"


class Product(BaseModel):
    """产品表"""
    __tablename__ = "products"

    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=True)
    status = Column(SQLEnum(ProductStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ProductStatus.DRAFT, index=True)
    platform = Column(String(50), nullable=True)
    analysis_result = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    videos = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    detail_page_url = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # 关系
    tasks = relationship("Task", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, status={self.status})>"
