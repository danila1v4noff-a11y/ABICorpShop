from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class SharedCart(Base):
    __tablename__ = "SharedCart"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.EmployeeID"), nullable=False)
    token = Column(String(36), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="owned_shared_carts")
    items = relationship("SharedCartItem", back_populates="shared_cart", cascade="all, delete-orphan")

class SharedCartItem(Base):
    __tablename__ = "SharedCartItem"

    id = Column(Integer, primary_key=True, index=True)
    shared_cart_id = Column(Integer, ForeignKey("SharedCart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("Products.ProductID", ondelete="CASCADE"), nullable=False)
    batch_id = Column("BatchID", Integer, ForeignKey("Batches.BatchID", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    added_by_user_id = Column(Integer, ForeignKey("users.EmployeeID"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("shared_cart_id", "product_id", name="uq_shared_cart_product"),)

    shared_cart = relationship("SharedCart", back_populates="items")
    product = relationship("Product")
    added_by_user = relationship("User", foreign_keys=[added_by_user_id])
    batch = relationship("Batch", back_populates="shared_cart_items")