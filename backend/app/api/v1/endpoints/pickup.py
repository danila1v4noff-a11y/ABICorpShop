from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import List
from app.core.database import get_db
from app.models.pickup_slot import PickupSlot
from pydantic import BaseModel

router = APIRouter(prefix="/pickup-slots", tags=["PickupSlots"])

class SlotInfo(BaseModel):
    date: date
    time_slot: str
    remaining: int

@router.get("/available", response_model=List[SlotInfo])
def get_available_slots(
    db: Session = Depends(get_db),
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    now = datetime.now()
    today = now.date()

    # Если даты не переданы, вычисляем как в корзине: три ближайших будних дня,
    # но если сейчас >16:00, то начиная с завтра
    if start_date is None:
        start = today
        if now.hour >= 16:
            start += timedelta(days=1)
        # Пропускаем выходные
        while start.weekday() >= 5:
            start += timedelta(days=1)
        start_date = start
    if end_date is None:
        # Берём 3 рабочих дня от start_date
        dates = []
        current = start_date
        while len(dates) < 3:
            if current.weekday() < 5:
                dates.append(current)
            current += timedelta(days=1)
        end_date = dates[-1] if dates else start_date

    time_slots = ["10-12", "14-16"]
    result = []

    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # только будние
            for ts in time_slots:
                slot = db.query(PickupSlot).filter(
                    PickupSlot.PickupDate == current,
                    PickupSlot.TimeSlot == ts
                ).first()
                if not slot:
                    slot = PickupSlot(PickupDate=current, TimeSlot=ts, BookedCount=0, MaxCapacity=20)
                    db.add(slot)
                    db.commit()
                    db.refresh(slot)
                remaining = slot.MaxCapacity - slot.BookedCount
                result.append(SlotInfo(date=current, time_slot=ts, remaining=remaining))
        current += timedelta(days=1)

    return result
