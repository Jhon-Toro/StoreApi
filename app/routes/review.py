from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ReviewResponse])
def get_all_reviews(db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .join(User, Review.user_id == User.id)
        .options(joinedload(Review.user))
        .all()
    )

    return [
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

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review_by_id(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).options(joinedload(Review.user)).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return ReviewResponse(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        user_id=review.user_id,
        product_id=review.product_id,
        username=review.user.username,
        created_at=review.created_at
    )

@router.post("/", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    new_review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return ReviewResponse(
        id=new_review.id,
        rating=new_review.rating,
        comment=new_review.comment,
        user_id=new_review.user_id,
        product_id=new_review.product_id,
        username=current_user.username,
        created_at=new_review.created_at
    )

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review.rating = review_data.rating
    review.comment = review_data.comment
    db.commit()
    db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        user_id=review.user_id,
        product_id=review.product_id,
        username=current_user.username,
        created_at=review.created_at
    )

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this review")

    db.delete(review)
    db.commit()
    return {"detail": "Review deleted successfully"}