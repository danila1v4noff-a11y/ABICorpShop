from pydantic import BaseModel
from datetime import datetime

class SharedCartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    added_by_user_name: str
    added_by_user_id: int
    image_url: str | None = None

    class Config:
        from_attributes = True

class SharedCartResponse(BaseModel):
    id: int
    owner_id: int
    owner_name: str
    token: str
    is_active: bool
    created_at: datetime
    items: list[SharedCartItemResponse]

class AddItemToSharedCart(BaseModel):
    product_id: int
    quantity: int = 1

class UpdateItemQuantity(BaseModel):
    quantity: int