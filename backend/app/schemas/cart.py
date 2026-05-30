from pydantic import BaseModel
from datetime import date

class CartItemCreate(BaseModel):
    product_id: int
    batch_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    cart_item_id: int
    product_id: int
    product_name: str
    batch_id: int
    batch_quantity: int
    expiration_date: date | None = None
    price: float
    quantity: int
    total_price: float
    image_url: str | None = None
    discount_price: float | None = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_sum: float
    total_weight: float