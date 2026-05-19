from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    product_id: int

class FavoriteResponse(BaseModel):
    favorite_id: int
    product_id: int
    product_name: str
    price: float
    image_url: str | None = None

    class Config:
        from_attributes = True