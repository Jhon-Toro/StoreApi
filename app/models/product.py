from sqlalchemy import Boolean, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    price = Column(Float, nullable=False)
    image_url_1 = Column(String(200), nullable=True)
    image_url_2 = Column(String(200), nullable=True)
    image_url_3 = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
