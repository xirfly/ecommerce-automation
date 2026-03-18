"""
销售数据模型
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SalesData(BaseModel):
    """销售数据表"""
    __tablename__ = "sales_data"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, comment="产品ID")
    date = Column(Date, nullable=False, comment="日期")
    views = Column(Integer, nullable=False, default=0, comment="浏览量")
    clicks = Column(Integer, nullable=False, default=0, comment="点击量")
    orders = Column(Integer, nullable=False, default=0, comment="订单量")
    sales_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="销售额")

    # 关系
    product = relationship("Product", backref="sales_data")
