from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.order import Order, OrderStatus, OrderStatusUpdate, PaymentStatus
from app.models.product import Product
from app.models.order_item import OrderItem
from app.models.review import Review
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.utils.auth import get_current_user
from base64 import b64encode
import requests

router = APIRouter()
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
PAYPAL_CLIENT_ID = "AYtLaXpdoGSDXNB2L3P7fQFApiFbE67_Etgez19KJAbn54AbE8FFQM2MmFgWgFwZZVZUXiBBkE39Pqq0"
PAYPAL_CLIENT_SECRET = "EP8Q0iLDWZBHKxPEgjnO-AaDjHZIUw537POP29HumZI3uVjsU8FQ3FxmHHKcOjvS21T3fxbff6f1mcke"

def get_paypal_access_token():
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    auth = b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise HTTPException(status_code=500, detail="Error al obtener el token de acceso de PayPal")

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    new_order = Order(
        user_id=current_user.id,
        total_price=order_data.total_price,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PACKING
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order_data.items:
        product_obj = db.query(Product).filter(Product.id == item.product_id).first()
        if not product_obj:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product_obj.price * item.quantity
        )
        db.add(order_item)
    db.commit()
    db.refresh(new_order)

    paypal_access_token = get_paypal_access_token()
    headers = {"Authorization": f"Bearer {paypal_access_token}"}
    data = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": str(new_order.total_price)}}],
        "application_context": {
            "return_url": "http://localhost:5173/order/success",
            "cancel_url": "http://localhost:5173/order/cancel"
        }
    }
    response = requests.post(f"{PAYPAL_API_BASE}/v2/checkout/orders", json=data, headers=headers)

    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Error al crear la orden de PayPal")

    approval_url = response.json()["links"][1]["href"]

    order_obj = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.reviews)
    ).filter(Order.id == new_order.id).first()

    order_response = OrderResponse.from_orm(order_obj)
    order_response.approval_url = approval_url
    return order_response

@router.get("/my_orders", response_model=List[OrderResponse])
def get_user_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.reviews)
    ).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.reviews),
        joinedload(Order.user)
    ).all()
    
    response_orders = [
        OrderResponse(
            id=order.id,
            order_status=order.order_status.value,
            total_price=order.total_price,
            created_at=order.created_at,
            username=order.user.username,
            user_id=order.user_id,
            items=[item for item in order.items],  # Cargar items
            payment_status=order.payment_status.value
        )
        for order in orders
    ]
    
    return response_orders


@router.get("/confirm", response_model=OrderResponse)
def confirm_payment(order_id: int, token: str, PayerID: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Get PayPal access token
    paypal_access_token = get_paypal_access_token()
    headers = {"Authorization": f"Bearer {paypal_access_token}"}
    
    # Capture the payment
    capture_url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{token}/capture"
    response = requests.post(capture_url, headers=headers)

    # Find the order and update the payment status
    order_obj = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check the response from PayPal to set the payment status
    if response.status_code == 201:
        order_obj.payment_status = PaymentStatus.APPROVED
    else:
        order_obj.payment_status = PaymentStatus.FAILED

    db.commit()
    db.refresh(order_obj)
    return order_obj

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order_obj = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.reviews)
    ).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_obj

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    order_obj = db.query(Order).filter(Order.id == order_id).first()
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        order_obj.order_status = OrderStatus(status_update.new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order status")

    db.commit()
    db.refresh(order_obj)
    return order_obj
