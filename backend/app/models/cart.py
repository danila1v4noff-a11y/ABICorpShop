from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class CartItem(Base):
    __tablename__ = "CartItem"

    CartItemID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.EmployeeID", ondelete="CASCADE"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID", ondelete="CASCADE"), nullable=False)
    BatchID = Column(Integer, ForeignKey("Batches.BatchID", ondelete="CASCADE"), nullable=True)
    Quantity = Column(Integer, nullable=False, default=1)
    AddedAt = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("UserID", "BatchID", name="uq_user_batch"),)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    batch = relationship("Batch", back_populates="cart_items")