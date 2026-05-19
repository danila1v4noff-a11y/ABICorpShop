from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.category import Category
from pydantic import BaseModel

class CategoryResponse(BaseModel):
    category_id: int
    name: str

    class Config:
        from_attributes = True

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [CategoryResponse(category_id=c.CategoryID, name=c.Name) for c in categories]