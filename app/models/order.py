from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class PaymentStatus(enum.Enum):
    PENDING = "Pendiente"
    APPROVED = "Aprobado"
    FAILED = "Fallido"

class OrderStatus(enum.Enum):
    PACKING = "Empacando"
    SHIPPING = "Enviando"
    DELIVERED = "Entregado"

class OrderStatusUpdate(BaseModel):
    new_status: str

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_price = Column(Float, nullable=False)
    
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.PACKING)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
