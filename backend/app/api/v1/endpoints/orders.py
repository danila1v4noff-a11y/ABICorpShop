from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc, asc
from datetime import date, timedelta, datetime, timezone

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.models.order import EmployeeOrder, OrderItem
from app.models.shared_cart import SharedCart, SharedCartItem
from app.models.batch import Batch
from app.models.pickup_slot import PickupSlot
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
            "image_url": oi.product.ImageURL,
            "batch_id": oi.BatchID,
            "expiration_date": oi.ExpirationDate.isoformat() if oi.ExpirationDate else None
        } for oi in order.items],
        cancelled_by_user=(order.Status == 'cancelled' and order.ProcessedBy is None)
    )

def _book_pickup_slot(db: Session, pickup_date: date, time_slot: str):
    slot = db.query(PickupSlot).filter(
        PickupSlot.PickupDate == pickup_date,
        PickupSlot.TimeSlot == time_slot
    ).first()
    if slot:
        slot.BookedCount += 1
    else:
        slot = PickupSlot(
            PickupDate=pickup_date,
            TimeSlot=time_slot,
            BookedCount=1
        )
        db.add(slot)
    db.commit()

def _release_pickup_slot(db: Session, pickup_date: date, time_slot: str):
    slot = db.query(PickupSlot).filter(
        PickupSlot.PickupDate == pickup_date,
        PickupSlot.TimeSlot == time_slot
    ).first()
    if slot and slot.BookedCount > 0:
        slot.BookedCount -= 1
        db.commit()

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Собираем все позиции из личной корзины
    personal_items = db.query(CartItem).filter(CartItem.UserID == current_user.EmployeeID).all()
    # Собираем позиции из активной общей корзины (где пользователь владелец)
    shared_cart = db.query(SharedCart).filter(
        SharedCart.owner_id == current_user.EmployeeID,
        SharedCart.is_active == True
    ).first()
    shared_items = []
    if shared_cart:
        shared_items = db.query(SharedCartItem).filter(
            SharedCartItem.shared_cart_id == shared_cart.id
        ).all()

    # Объединяем все позиции (product_id, quantity, batch_id)
    all_items = []
    for pi in personal_items:
        all_items.append({
            "product_id": pi.ProductID,
            "quantity": pi.Quantity,
            "batch_id": pi.BatchID
        })
    for si in shared_items:
        all_items.append({
            "product_id": si.product_id,
            "quantity": si.quantity,
            "batch_id": si.batch_id   # может быть None, если старая запись без партии
        })

    if not all_items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    total_weight = 0
    for item in all_items:
        product = db.query(Product).get(item["product_id"])
        if not product:
            raise HTTPException(status_code=400, detail=f"Товар с ID {item['product_id']} не найден")
        if item["quantity"] > MAX_ITEM_QUANTITY:
            raise HTTPException(status_code=400, detail=f"Максимальное количество '{product.Name}' – {MAX_ITEM_QUANTITY} шт")
        available = db.query(sqlfunc.coalesce(sqlfunc.sum(Batch.Quantity), 0))\
                      .filter(Batch.ProductID == product.ProductID).scalar()
        if item["quantity"] > available:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара '{product.Name}' на складе")
        if product.Weight:
            total_weight += product.Weight * item["quantity"]

    if total_weight > MAX_WEIGHT:
        raise HTTPException(status_code=400, detail="Общий вес заказа превышает 25 кг")

    # Проверка доступности слота самовывоза
    if order_data.delivery_method == 'pickup' and order_data.delivery_date and order_data.delivery_time_slot:
        slot = db.query(PickupSlot).filter(
            PickupSlot.PickupDate == order_data.delivery_date,
            PickupSlot.TimeSlot == order_data.delivery_time_slot
        ).first()
        if slot and slot.BookedCount >= slot.MaxCapacity:
            raise HTTPException(status_code=400, detail="Выбранный временной слот уже заполнен")

    total_amount = 0
    for item in all_items:
        product = db.query(Product).get(item["product_id"])
        total_amount += float(product.Price) * item["quantity"]

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

    # Списание товаров и создание OrderItem
    for item in all_items:
        product = db.query(Product).get(item["product_id"])
        remaining = item["quantity"]
        batch_id = item.get("batch_id")
        expiration_date = None   # <-- будем сохранять дату партии

        if batch_id:
            # Прямое списание из указанной партии
            batch = db.query(Batch).filter(Batch.BatchID == batch_id).first()
            if not batch or batch.Quantity < remaining:
                raise HTTPException(status_code=400, detail=f"Недостаточно товара '{product.Name}' в партии")
            batch.Quantity -= remaining
            expiration_date = batch.ExpirationDate   # запоминаем срок
            if batch.Quantity == 0:
                db.delete(batch)
        else:
            # Списание по FIFO для позиций без привязки к партии
            batches = db.query(Batch).filter(
                Batch.ProductID == product.ProductID,
                Batch.Quantity > 0
            ).order_by(asc(Batch.ExpirationDate)).all()
            for batch in batches:
                take = min(remaining, batch.Quantity)
                batch.Quantity -= take
                remaining -= take
                if batch.Quantity == 0:
                    db.delete(batch)
                if remaining == 0:
                    break
            if remaining > 0:
                raise HTTPException(status_code=400, detail=f"Недостаточно товара '{product.Name}' на складе")

        order_item = OrderItem(
            OrderID=order.OrderID,
            ProductID=product.ProductID,
            Quantity=item["quantity"],
            PriceAtOrder=product.Price,
            BatchID=batch_id,
            ExpirationDate=expiration_date      # <-- теперь всегда определён
        )
        db.add(order_item)

    # Очистка личной и общей корзины
    db.query(CartItem).filter(CartItem.UserID == current_user.EmployeeID).delete()
    if shared_cart:
        db.query(SharedCartItem).filter(SharedCartItem.shared_cart_id == shared_cart.id).delete()
        shared_cart.is_active = False

    # Бронирование слота самовывоза
    if order_data.delivery_method == 'pickup' and order_data.delivery_date and order_data.delivery_time_slot:
        _book_pickup_slot(db, order_data.delivery_date, order_data.delivery_time_slot)

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


@router.post("/{order_id}/cancel")
def cancel_order_by_user(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(EmployeeOrder).filter(EmployeeOrder.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.UserID != current_user.EmployeeID:
        raise HTTPException(status_code=403, detail="Вы не можете отменить чужой заказ")
    if order.Status != 'pending':
        raise HTTPException(status_code=400, detail="Заказ уже обработан или отменён")

    elapsed = datetime.now(timezone.utc) - order.CreatedAt
    if elapsed > timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="Время для отмены истекло (5 минут)")

    order.Status = 'cancelled'
    for item in order.items:
        return_batch = Batch(
            ProductID=item.ProductID,
            Quantity=item.Quantity,
            ExpirationDate=date.today() + timedelta(days=14)
        )
        db.add(return_batch)

    if order.DeliveryMethod == 'pickup' and order.DeliveryDate and order.DeliveryTimeSlot:
        _release_pickup_slot(db, order.DeliveryDate, order.DeliveryTimeSlot)

    db.commit()
    return {"status": "cancelled"}


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

    if status_update.status in ('rejected', 'cancelled') and old_status not in ('rejected', 'cancelled'):
        for item in order.items:
            return_batch = Batch(
                ProductID=item.ProductID,
                Quantity=item.Quantity,
                ExpirationDate=date.today() + timedelta(days=14)
            )
            db.add(return_batch)
        if order.DeliveryMethod == 'pickup' and order.DeliveryDate and order.DeliveryTimeSlot:
            _release_pickup_slot(db, order.DeliveryDate, order.DeliveryTimeSlot)

    db.commit()
    return {"status": "updated"}

@router_admin.get("/pending-count")
def get_pending_orders_count(
    manager: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    count = db.query(EmployeeOrder).filter(EmployeeOrder.Status == "pending").count()
    return {"pending_count": count}