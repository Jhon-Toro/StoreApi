from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.product import ProductResponse
from app.schemas.review import ReviewResponse
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    return category

@router.get("/{category_id}/products", response_model=List[ProductResponse])
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    # Verificamos que la categoría exista
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Obtenemos los productos y sus reseñas con la relación del usuario
    products = db.query(Product).options(
        joinedload(Product.reviews).joinedload(Review.user)
    ).filter(Product.category_id == category_id).all()

    # Creamos las respuestas de productos con los reviews y el username de cada uno
    product_responses = []
    for product in products:
        average_rating = db.query(func.avg(Review.rating)).filter(Review.product_id == product.id).scalar() or 0

        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            category_id=product.category_id,
            price=product.price,
            images=[url for url in [product.image_url_1, product.image_url_2, product.image_url_3] if url],
            reviews=[
                ReviewResponse(
                    id=review.id,
                    rating=review.rating,
                    comment=review.comment,
                    user_id=review.user_id,
                    product_id=review.product_id,
                    username=review.user.username,  # Accedemos al username
                    created_at=review.created_at
                )
                for review in product.reviews
            ],
            average_rating=average_rating
        )
        product_responses.append(product_response)

    return product_responses

@router.post("/", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    new_category = Category(name=category_data.name, image=category_data.image)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


    category.name = category_data.name
    category.image = category_data.image

    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", response_model=CategoryResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category)
    db.commit()
    return category
