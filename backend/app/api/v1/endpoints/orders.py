from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc, asc
from datetime import date, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.models.order import EmployeeOrder, OrderItem
from app.models.shared_cart import SharedCart
from app.models.batch import Batch
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

MAX_WEIGHT = 25000
MAX_ITEM_QUANTITY = 15

def format_order(order):
    return OrderResponse(
        order_id=order.OrderID,
        user_id=order.UserID,
        user_name=order.user.FIO,
        delivery_method=order.DeliveryMethod,
        office_address=order.OfficeAddress,
        cabinet=order.Cabinet,
        delivery_date=order.DeliveryDate,
        delivery_time_slot=order.DeliveryTimeSlot,
        payment_method=order.PaymentMethod,
        status=order.Status,
        total_amount=float(order.TotalAmount),
        total_weight=order.TotalWeight or 0,
        created_at=order.CreatedAt,
        items=[{
            "product_id": oi.ProductID,
            "product_name": oi.product.Name,
            "price": float(oi.PriceAtOrder),
            "quantity": oi.Quantity,
            "total_price": float(oi.PriceAtOrder) * oi.Quantity,
            "image_url": oi.product.ImageURL
        } for oi in order.items]
    )

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    total_weight = 0
    for item_in in order_data.items:
        product = db.query(Product).filter(Product.ProductID == item_in.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Товар с ID {item_in.product_id} не найден")
        if item_in.quantity > MAX_ITEM_QUANTITY:
            raise HTTPException(status_code=400, detail=f"Максимальное количество '{product.Name}' – {MAX_ITEM_QUANTITY} шт")

        # Проверяем доступное количество (сумма по партиям)
        available = db.query(sqlfunc.coalesce(sqlfunc.sum(Batch.Quantity), 0))\
                      .filter(Batch.ProductID == product.ProductID).scalar()
        if item_in.quantity > available:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара '{product.Name}' на складе")
        if product.Weight:
            total_weight += product.Weight * item_in.quantity

    if total_weight > MAX_WEIGHT:
        raise HTTPException(status_code=400, detail="Общий вес заказа превышает 25 кг")

    total_amount = sum(
        float(db.query(Product).filter(Product.ProductID == item.product_id).first().Price) * item.quantity
        for item in order_data.items
    )

    order = EmployeeOrder(
        UserID=current_user.EmployeeID,
        DeliveryMethod=order_data.delivery_method,
        OfficeAddress=order_data.office_address,
        Cabinet=order_data.cabinet,
        DeliveryDate=order_data.delivery_date,
        DeliveryTimeSlot=order_data.delivery_time_slot,
        PaymentMethod=order_data.payment_method,
        TotalAmount=total_amount,
        TotalWeight=total_weight,
        Status='pending'
    )
    db.add(order)
    db.flush()

    # Списание с партий по FIFO
    for item_in in order_data.items:
        product = db.query(Product).get(item_in.product_id)
        remaining = item_in.quantity
        # Получаем партии, отсортированные по дате окончания (сначала истекающие)
        batches = db.query(Batch).filter(
            Batch.ProductID == product.ProductID,
            Batch.Quantity > 0
        ).order_by(asc(Batch.ExpirationDate)).all()

        for batch in batches:
            if remaining <= 0:
                break
            take = min(remaining, batch.Quantity)
            batch.Quantity -= take
            remaining -= take
            if batch.Quantity == 0:
                db.delete(batch)

        # Создаём запись OrderItem
        order_item = OrderItem(
            OrderID=order.OrderID,
            ProductID=product.ProductID,
            Quantity=item_in.quantity,
            PriceAtOrder=product.Price
        )
        db.add(order_item)

    # Очищаем личную корзину пользователя
    db.query(CartItem).filter(CartItem.UserID == current_user.EmployeeID).delete()

    # Деактивируем активную общую корзину пользователя (если есть)
    shared = db.query(SharedCart).filter(
        SharedCart.owner_id == current_user.EmployeeID,
        SharedCart.is_active == True
    ).first()
    if shared:
        shared.is_active = False

    db.commit()
    db.refresh(order)
    return format_order(order)


@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(EmployeeOrder).filter(
        EmployeeOrder.UserID == current_user.EmployeeID
    ).order_by(EmployeeOrder.CreatedAt.desc()).all()
    return [format_order(o) for o in orders]


# Админский роутер
router_admin = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])

def require_manager(current_user: User = Depends(get_current_user)):
    if current_user.Manager != 1:
        raise HTTPException(status_code=403, detail="Требуются права менеджера")
    return current_user

@router_admin.get("/", response_model=list[OrderResponse])
def get_all_orders(
    manager: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    orders = db.query(EmployeeOrder).order_by(EmployeeOrder.CreatedAt.desc()).all()
    return [format_order(o) for o in orders]

@router_admin.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    manager: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    order = db.query(EmployeeOrder).filter(EmployeeOrder.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    old_status = order.Status
    order.Status = status_update.status
    order.ProcessedBy = manager.EmployeeID

    # При отмене/отклонении возвращаем товары в партии
    if status_update.status in ('rejected', 'cancelled') and old_status not in ('rejected', 'cancelled'):
        for item in order.items:
            return_batch = Batch(
                ProductID=item.ProductID,
                Quantity=item.Quantity,
                ExpirationDate=date.today() + timedelta(days=14)  # условный срок годности возврата
            )
            db.add(return_batch)

    db.commit()
    return {"status": "updated"}