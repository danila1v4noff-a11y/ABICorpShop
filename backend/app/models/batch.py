from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Batch(Base):
    __tablename__ = "Batches"

    BatchID = Column(Integer, primary_key=True, index=True)
    ProductID = Column(Integer, ForeignKey("Products.ProductID", ondelete="CASCADE"), nullable=False)
    Quantity = Column(Integer, nullable=False)
    ExpirationDate = Column(Date, nullable=False)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    cart_items = relationship("CartItem", back_populates="batch")
    product = relationship("Product", back_populates="batches")
    shared_cart_items = relationship("SharedCartItem", back_populates="batch")
    order_items = relationship("OrderItem", back_populates="batch")