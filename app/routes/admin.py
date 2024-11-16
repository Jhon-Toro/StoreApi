from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import product
from app.models.user import User
from app.schemas.product import ProductResponse
from app.utils.auth import get_current_user

router = APIRouter()

@router.delete("/products/{product_id}", response_model=ProductResponse)
def delete_product_as_admin(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    product = db.query(product).filter(product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return product
