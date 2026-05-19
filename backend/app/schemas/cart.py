from pydantic import BaseModel

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    cart_item_id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    total_price: float
    image_url: str | None = None
    discount_price: float | None = None   # цена со скидкой (если есть)

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_sum: float
    total_weight: float