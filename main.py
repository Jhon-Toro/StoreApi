from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import uvicorn
from app.database import engine, Base, get_db
from app.routes import auth_router, product_router, category_router, review_router, order_router, admin_router
from app.utils.auth import get_password_hash
from app.models.user import User

Base.metadata.create_all(bind=engine)

def create_admin_account(db: Session):
    admin_email = "admin@gmail.com"
    admin_username = "admin"
    admin_password = "adminpassword"

    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        hashed_password = get_password_hash(admin_password)
        new_admin = User(
            username=admin_username,
            email=admin_email,
            hashed_password=hashed_password,
            is_admin=True
        )
        db.add(new_admin)
        db.commit()
        print("Cuenta de administrador creada")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    create_admin_account(db)
    yield 

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "API is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(category_router, prefix="/categories", tags=["categories"])
app.include_router(review_router, prefix="/reviews", tags=["reviews"])
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])