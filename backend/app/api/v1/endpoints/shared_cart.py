import uuid
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.shared_cart import SharedCart, SharedCartItem
from app.models.batch import Batch
from app.schemas.shared_cart import (
    SharedCartResponse,
    SharedCartItemResponse,
    AddItemToSharedCart,
    UpdateItemQuantity,
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/shared-cart", tags=["Shared Cart"])

def enrich_item(item, db):
    """Добавляет скидку для товара, если есть истекающая партия."""
    product = item.product
    price = float(product.Price)
    threshold = date.today() + timedelta(days=14)
    has_expiring = db.query(Batch).filter(
        Batch.ProductID == product.ProductID,
        Batch.Quantity > 0,
        Batch.ExpirationDate <= threshold
    ).first() is not None
    discount_price = round(price * 0.6) if has_expiring else None
    return SharedCartItemResponse(
        id=item.id,
        product_id=product.ProductID,
        product_name=product.Name,
        price=price,
        discount_price=discount_price,
        quantity=item.quantity,
        added_by_user_name=item.added_by_user.FIO,
        added_by_user_id=item.added_by_user_id,
        image_url=product.ImageURL,
    )

@router.post("/", response_model=SharedCartResponse)
def create_shared_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(SharedCart).filter(
        SharedCart.owner_id == current_user.EmployeeID,
        SharedCart.is_active == True,
    ).update({"is_active": False})
    db.flush()

    token = str(uuid.uuid4())
    cart = SharedCart(owner_id=current_user.EmployeeID, token=token)
    db.add(cart)
    db.commit()
    db.refresh(cart)

    return SharedCartResponse(
        id=cart.id,
        owner_id=cart.owner_id,
        owner_name=current_user.FIO,
        token=cart.token,
        is_active=cart.is_active,
        created_at=cart.created_at,
        items=[],
    )

@router.get("/{token}", response_model=SharedCartResponse)
def get_shared_cart(token: str, db: Session = Depends(get_db)):
    cart = db.query(SharedCart).filter(SharedCart.token == token).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Общая корзина не найдена")
    items = [enrich_item(item, db) for item in cart.items]
    return SharedCartResponse(
        id=cart.id,
        owner_id=cart.owner_id,
        owner_name=cart.owner.FIO,
        token=cart.token,
        is_active=cart.is_active,
        created_at=cart.created_at,
        items=items,
    )

@router.post("/{token}/add", response_model=SharedCartItemResponse)
def add_item_to_shared_cart(
    token: str,
    item_in: AddItemToSharedCart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = db.query(SharedCart).filter(
        SharedCart.token == token, SharedCart.is_active == True
    ).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Активная общая корзина не найдена")
    product = db.query(Product).filter(Product.ProductID == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    existing_item = db.query(SharedCartItem).filter(
        SharedCartItem.shared_cart_id == cart.id,
        SharedCartItem.product_id == item_in.product_id,
    ).first()
    if existing_item:
        existing_item.quantity += item_in.quantity
        db.commit()
        db.refresh(existing_item)
        return enrich_item(existing_item, db)

    item = SharedCartItem(
        shared_cart_id=cart.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity,
        added_by_user_id=current_user.EmployeeID,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return enrich_item(item, db)

@router.put("/{token}/item/{item_id}", response_model=SharedCartItemResponse)
def update_item_in_shared_cart(
    token: str,
    item_id: int,
    update: UpdateItemQuantity,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = db.query(SharedCart).filter(
        SharedCart.token == token, SharedCart.is_active == True
    ).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Общая корзина не найдена")

    item = db.query(SharedCartItem).filter(
        SharedCartItem.id == item_id,
        SharedCartItem.shared_cart_id == cart.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    if cart.owner_id != current_user.EmployeeID and item.added_by_user_id != current_user.EmployeeID:
        raise HTTPException(status_code=403, detail="Нет прав для изменения")

    if update.quantity <= 0:
        db.delete(item)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    item.quantity = update.quantity
    db.commit()
    db.refresh(item)
    return enrich_item(item, db)

@router.delete("/{token}/item/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_shared_cart(
    token: str,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = db.query(SharedCart).filter(
        SharedCart.token == token, SharedCart.is_active == True
    ).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Общая корзина не найдена")

    item = db.query(SharedCartItem).filter(
        SharedCartItem.id == item_id,
        SharedCartItem.shared_cart_id == cart.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    if cart.owner_id != current_user.EmployeeID and item.added_by_user_id != current_user.EmployeeID:
        raise HTTPException(status_code=403, detail="Нет прав для удаления")

    db.delete(item)
    db.commit()
    return