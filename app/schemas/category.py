from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    image: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    image: Optional[str] = None

    class Config:
        from_attributes = True
