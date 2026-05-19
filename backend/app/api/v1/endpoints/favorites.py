from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.favorite import FavoriteProductEmployee
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.get("/", response_model=list[FavoriteResponse])
def get_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorites = db.query(FavoriteProductEmployee).filter(
        FavoriteProductEmployee.UserID == current_user.EmployeeID
    ).all()
    result = []
    for fav in favorites:
        product = fav.product
        result.append(FavoriteResponse(
            favorite_id=fav.FavoriteID,
            product_id=product.ProductID,
            product_name=product.Name,
            price=float(product.Price),
            image_url=product.ImageURL
        ))
    return result

@router.post("/", response_model=FavoriteResponse)
def add_favorite(
    fav_in: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверим, существует ли товар
    product = db.query(Product).filter(Product.ProductID == fav_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Проверим, нет ли уже в избранном
    existing = db.query(FavoriteProductEmployee).filter(
        FavoriteProductEmployee.UserID == current_user.EmployeeID,
        FavoriteProductEmployee.ProductID == fav_in.product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Товар уже в избранном")
    
    favorite = FavoriteProductEmployee(
        UserID=current_user.EmployeeID,
        ProductID=fav_in.product_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return FavoriteResponse(
        favorite_id=favorite.FavoriteID,
        product_id=product.ProductID,
        product_name=product.Name,
        price=float(product.Price),
        image_url=product.ImageURL
    )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favorite = db.query(FavoriteProductEmployee).filter(
        FavoriteProductEmployee.UserID == current_user.EmployeeID,
        FavoriteProductEmployee.ProductID == product_id
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Товар не найден в избранном")
    db.delete(favorite)
    db.commit()
    return