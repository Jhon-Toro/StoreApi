import datetime
from pydantic import BaseModel
from typing import Optional

class ReviewBase(BaseModel):
    rating: float
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    product_id: int

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int
    username: Optional[str] = None
    created_at: Optional[datetime.datetime ]

    model_config = {'arbitrary_types_allowed': True, 'from_attributes': True}
