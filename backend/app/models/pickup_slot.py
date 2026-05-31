from sqlalchemy import Column, Integer, Date, String, UniqueConstraint
from app.core.database import Base

class PickupSlot(Base):
    __tablename__ = "PickupSlots"
    SlotID = Column(Integer, primary_key=True, index=True)
    PickupDate = Column(Date, nullable=False)
    TimeSlot = Column(String(10), nullable=False)
    BookedCount = Column(Integer, nullable=False, default=0)
    MaxCapacity = Column(Integer, nullable=False, default=20)