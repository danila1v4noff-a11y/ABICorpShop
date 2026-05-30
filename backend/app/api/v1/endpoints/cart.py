from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
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
        batch = item.batch
        if not product or not batch:
            continue

        has_expiring = batch.ExpirationDate and batch.ExpirationDate <= threshold
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
            batch_id=batch.BatchID,
            batch_quantity=batch.Quantity,
            expiration_date=batch.ExpirationDate,
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
        raise HTTPException(status_code=403, detail=f"Вы находитесь в чёрном списке. Причина: {blacklist_entry.Reason}")

    product = db.query(Product).filter(Product.ProductID == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    batch = db.query(Batch).filter(Batch.BatchID == item_in.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Партия не найдена")
    if batch.ProductID != product.ProductID:
        raise HTTPException(status_code=400, detail="Партия не принадлежит товару")

    # Проверка общего лимита товара (сумма по всем партиям этого товара)
    total_in_cart = db.query(func.sum(CartItem.Quantity)).filter(
        CartItem.UserID == current_user.EmployeeID,
        CartItem.ProductID == product.ProductID
    ).scalar() or 0

    if total_in_cart + item_in.quantity > 15:
        raise HTTPException(status_code=400, detail="Общее количество товара в корзине не может превышать 15 шт.")

    # Проверка остатка конкретной партии
    if item_in.quantity > batch.Quantity:
        raise HTTPException(status_code=400, detail="Недостаточно товара в выбранной партии")

    existing = db.query(CartItem).filter(
        CartItem.UserID == current_user.EmployeeID,
        CartItem.BatchID == item_in.batch_id
    ).first()

    if existing:
        existing.Quantity += item_in.quantity
        db.commit()
        db.refresh(existing)
        cart_item = existing
    else:
        cart_item = CartItem(
            UserID=current_user.EmployeeID,
            ProductID=product.ProductID,
            BatchID=item_in.batch_id,
            Quantity=item_in.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

    threshold = date.today() + timedelta(days=14)
    has_expiring = batch.ExpirationDate and batch.ExpirationDate <= threshold
    price = float(product.Price)
    discount_price = round(price * 0.6) if has_expiring else None
    final_price = discount_price if has_expiring else price
    total_price = final_price * cart_item.Quantity

    return CartItemResponse(
        cart_item_id=cart_item.CartItemID,
        product_id=product.ProductID,
        product_name=product.Name,
        batch_id=batch.BatchID,
        batch_quantity=batch.Quantity,
        expiration_date=batch.ExpirationDate,
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

    batch = cart_item.batch
    if item_update.quantity > batch.Quantity:
        raise HTTPException(status_code=400, detail="Недостаточно товара в выбранной партии")

    if item_update.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return CartItemResponse(
            cart_item_id=cart_item.CartItemID,
            product_id=cart_item.ProductID,
            product_name=cart_item.product.Name,
            batch_id=batch.BatchID,
            batch_quantity=batch.Quantity,
            expiration_date=batch.ExpirationDate,
            price=float(cart_item.product.Price),
            quantity=0,
            total_price=0,
            image_url=cart_item.product.ImageURL,
            discount_price=None
        )

    cart_item.Quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)

    threshold = date.today() + timedelta(days=14)
    has_expiring = batch.ExpirationDate and batch.ExpirationDate <= threshold
    price = float(cart_item.product.Price)
    discount_price = round(price * 0.6) if has_expiring else None
    total_price = (discount_price if has_expiring else price) * cart_item.Quantity

    return CartItemResponse(
        cart_item_id=cart_item.CartItemID,
        product_id=cart_item.ProductID,
        product_name=cart_item.product.Name,
        batch_id=batch.BatchID,
        batch_quantity=batch.Quantity,
        expiration_date=batch.ExpirationDate,
        price=price,
        quantity=cart_item.Quantity,
        total_price=total_price,
        image_url=cart_item.product.ImageURL,
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