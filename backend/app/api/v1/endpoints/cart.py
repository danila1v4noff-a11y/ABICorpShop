from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.models.batch import Batch
from app.models.blacklist import Blacklist
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_items = db.query(CartItem).filter(CartItem.UserID == current_user.EmployeeID).all()
    items_response = []
    total_sum = 0.0
    total_weight = 0.0
    threshold = date.today() + timedelta(days=14)

    for item in cart_items:
        product = item.product
        if not product:
            continue

        # Проверяем, есть ли истекающая партия
        has_expiring = db.query(Batch).filter(
            Batch.ProductID == product.ProductID,
            Batch.Quantity > 0,
            Batch.ExpirationDate <= threshold
        ).first() is not None

        price = float(product.Price)
        discount_price = round(price * 0.6) if has_expiring else None
        final_price = discount_price if has_expiring else price
        total_price = final_price * item.Quantity
        total_sum += total_price
        if product.Weight:
            total_weight += product.Weight * item.Quantity

        items_response.append(CartItemResponse(
            cart_item_id=item.CartItemID,
            product_id=product.ProductID,
            product_name=product.Name,
            price=price,
            quantity=item.Quantity,
            total_price=total_price,
            image_url=product.ImageURL,
            discount_price=discount_price
        ))

    return CartResponse(
        items=items_response,
        total_sum=total_sum,
        total_weight=total_weight
    )

@router.post("/add", response_model=CartItemResponse)
def add_to_cart(
    item_in: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверка чёрного списка
    blacklist_entry = db.query(Blacklist).filter(Blacklist.UserID == current_user.EmployeeID).first()
    if blacklist_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Вы находитесь в чёрном списке. Причина: {blacklist_entry.Reason}"
        )

    product = db.query(Product).filter(Product.ProductID == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    existing_item = db.query(CartItem).filter(
        CartItem.UserID == current_user.EmployeeID,
        CartItem.ProductID == item_in.product_id
    ).first()

    if existing_item:
        existing_item.Quantity += item_in.quantity
        db.commit()
        db.refresh(existing_item)
        cart_item = existing_item
    else:
        cart_item = CartItem(
            UserID=current_user.EmployeeID,
            ProductID=item_in.product_id,
            Quantity=item_in.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

    # Рассчитываем ответ с учётом скидки
    threshold = date.today() + timedelta(days=14)
    has_expiring = db.query(Batch).filter(
        Batch.ProductID == product.ProductID,
        Batch.Quantity > 0,
        Batch.ExpirationDate <= threshold
    ).first() is not None
    price = float(product.Price)
    discount_price = round(price * 0.6) if has_expiring else None
    final_price = discount_price if has_expiring else price
    total_price = final_price * cart_item.Quantity

    return CartItemResponse(
        cart_item_id=cart_item.CartItemID,
        product_id=product.ProductID,
        product_name=product.Name,
        price=price,
        quantity=cart_item.Quantity,
        total_price=total_price,
        image_url=product.ImageURL,
        discount_price=discount_price
    )

@router.put("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItem).filter(
        CartItem.CartItemID == item_id,
        CartItem.UserID == current_user.EmployeeID
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")

    if item_update.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        raise HTTPException(status_code=204, detail="Элемент удалён")

    cart_item.Quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)

    product = cart_item.product
    threshold = date.today() + timedelta(days=14)
    has_expiring = db.query(Batch).filter(
        Batch.ProductID == product.ProductID,
        Batch.Quantity > 0,
        Batch.ExpirationDate <= threshold
    ).first() is not None
    price = float(product.Price)
    discount_price = round(price * 0.6) if has_expiring else None
    final_price = discount_price if has_expiring else price
    total_price = final_price * cart_item.Quantity

    return CartItemResponse(
        cart_item_id=cart_item.CartItemID,
        product_id=product.ProductID,
        product_name=product.Name,
        price=price,
        quantity=cart_item.Quantity,
        total_price=total_price,
        image_url=product.ImageURL,
        discount_price=discount_price
    )

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItem).filter(
        CartItem.CartItemID == item_id,
        CartItem.UserID == current_user.EmployeeID
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")
    db.delete(cart_item)
    db.commit()
    return