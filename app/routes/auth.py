from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.utils.auth import get_password_hash, create_access_token, verify_password
from typing import Any
from datetime import timedelta

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 1440

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_email = db.query(User).filter(User.email == user_data.email).first()
    db_user = db.query(User).filter(User.username == user_data.username).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Username alredy registered")
    
    if db_email:
        raise HTTPException(status_code=400, detail="Email alredy registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username= user_data.username,
        email = user_data.email,
        hashed_password = hashed_password,
        is_admin = False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "isAdmin": user.is_admin
        }
    }