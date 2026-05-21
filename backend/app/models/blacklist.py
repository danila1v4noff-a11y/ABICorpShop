from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Blacklist(Base):
    __tablename__ = "Blacklist"

    BlacklistID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.EmployeeID", ondelete="CASCADE"), unique=True, nullable=False)
    Reason = Column(String, nullable=False)
    CreatedBy = Column(Integer, ForeignKey("users.EmployeeID"), nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="blacklist_entry", foreign_keys=[UserID])
    created_by_manager = relationship("User", foreign_keys=[CreatedBy])