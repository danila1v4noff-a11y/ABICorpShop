from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ProductResponse(BaseModel):
    product_id: int
    name: str
    price: float
    weight: int | None = None
    image_url: str | None = None
    stock: int
    has_expiring: bool = False

    class Config:
        from_attributes = True

class ProductDetailResponse(ProductResponse):
    description: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    expiration_date: Optional[date] = None   # ближайшая истекающая партия (если есть)
    cooking_info: Optional[str] = None       # "2 минуты в микроволновке" и т.п.

class RelatedProduct(BaseModel):
    product_id: int
    name: str
    image_url: str | None = None