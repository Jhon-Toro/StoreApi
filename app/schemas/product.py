from pydantic import BaseModel
from typing import Optional, List
from app.schemas.review import ReviewResponse
from .category import CategoryResponse

class ProductBase(BaseModel):
    title: str
    price: float
    description: Optional[str] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    images: List[str]

class ProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    images: Optional[List[str]] = []
    reviews: List[ReviewResponse] = None
    average_rating: Optional[float] = None
    category_id: Optional[int] = None

    class Config:
        from_attributes = True
