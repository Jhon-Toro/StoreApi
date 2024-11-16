from typing import List
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.review import Review
from app.models.category import Category
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.review import ReviewResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).options(
        joinedload(Product.reviews).joinedload(Review.user)
    ).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    average_rating = db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar() or 0
    
    product_response = ProductResponse(
        id=product.id,
        title=product.title,
        description=product.description,
        category_id=product.category_id,
        price=product.price,
        images=[url for url in [product.image_url_1, product.image_url_2, product.image_url_3] if url is not None],
        reviews=[
            ReviewResponse(
                id=review.id,
                rating=review.rating,
                comment=review.comment,
                user_id=review.user_id,
                product_id=review.product_id,
                username=review.user.username,  # Asegúrate de que el usuario esté cargado
                created_at=review.created_at
            )
            for review in product.reviews
        ],
        average_rating=average_rating
    )
    
    return product_response

@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    product_responses = []

    for product in products:
        reviews = db.query(Review).options(joinedload(Review.user)).filter(Review.product_id == product.id).all()
        average_rating = db.query(func.avg(Review.rating)).filter(Review.product_id == product.id).scalar() or 0

        review_responses = [
            ReviewResponse(
                id=review.id,
                rating=review.rating,
                comment=review.comment,
                user_id=review.user_id,
                product_id=review.product_id,
                username=review.user.username,
                created_at=review.created_at
            )
            for review in reviews
        ]

        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            category_id=product.category_id,
            price=product.price,
            images=[url for url in [product.image_url_1, product.image_url_2, product.image_url_3] if url is not None],
            reviews=review_responses,
            average_rating=average_rating
        )

        product_responses.append(product_response)

    return product_responses

@router.post("/", response_model=ProductResponse)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id {product_data.category_id} no existe."
        )
    
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    new_product = Product(
        title=product_data.title,
        description=product_data.description,
        category_id=product_data.category_id,
        price=product_data.price,
        image_url_1=product_data.images[0] if len(product_data.images) > 0 else None,
        image_url_2=product_data.images[1] if len(product_data.images) > 1 else None,
        image_url_3=product_data.images[2] if len(product_data.images) > 2 else None
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    images = [url for url in [new_product.image_url_1, new_product.image_url_2, new_product.image_url_3] if url is not None]

    return ProductResponse(
        id=new_product.id,
        title=new_product.title,
        description=new_product.description,
        category_id=new_product.category_id,
        price=new_product.price,
        images=images
    )

@router.delete("/{product_id}", response_model=ProductResponse)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    product = db.query(Product).options(
        joinedload(Product.reviews).joinedload(Review.user)
    ).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id {product_data.category_id} no existe."
        )

    product.title = product_data.title
    product.description = product_data.description
    product.category_id = product_data.category_id
    product.price = product_data.price
    product.image_url_1 = product_data.images[0] if len(product_data.images) > 0 else None
    product.image_url_2 = product_data.images[1] if len(product_data.images) > 1 else None
    product.image_url_3 = product_data.images[2] if len(product_data.images) > 2 else None

    db.commit()
    db.refresh(product)

    reviews = [
        ReviewResponse(
            id=review.id,
            rating=review.rating,
            comment=review.comment,
            user_id=review.user_id,
            product_id=review.product_id,
            username=review.user.username,
            created_at=review.created_at
        )
        for review in product.reviews
    ]

    product_response = ProductResponse(
        id=product.id,
        title=product.title,
        description=product.description,
        category_id=product.category_id,
        price=product.price,
        images=[url for url in [product.image_url_1, product.image_url_2, product.image_url_3] if url is not None],
        reviews=reviews,
        average_rating=db.query(func.avg(Review.rating)).filter(Review.product_id == product.id).scalar() or 0
    )

    return product_response
