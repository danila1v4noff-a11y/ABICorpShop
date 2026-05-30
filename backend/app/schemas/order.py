from pydantic import BaseModel
from datetime import date, datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    delivery_method: str
    office_address: str | None = None
    cabinet: str | None = None
    delivery_date: date | None = None
    delivery_time_slot: str | None = None
    payment_method: str
    items: list[OrderItemCreate]

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    total_price: float
    image_url: str | None = None

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    user_name: str
    delivery_method: str
    office_address: str | None = None
    cabinet: str | None = None
    delivery_date: date | None = None
    delivery_time_slot: str | None = None
    payment_method: str
    status: str
    total_amount: float
    total_weight: int
    created_at: datetime
    items: list[OrderItemResponse]
    cancelled_by_user: bool = False
    items: list[dict]   # или конкретный тип, если определён

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

