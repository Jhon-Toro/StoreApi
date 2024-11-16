from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .product import ProductResponse

class PayPalApprovalResponse(BaseModel):
    order_id: int
    approval_url: str

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    total_price: float

class OrderItemResponse(BaseModel):
    product: ProductResponse
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    total_price: float
    items: List[OrderItemResponse]
    payment_status: str
    order_status: str
    approval_url: Optional[str] = None
    
    class Config:
        from_attributes = True
