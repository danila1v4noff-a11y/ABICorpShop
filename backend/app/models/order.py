from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmployeeOrder(Base):
    __tablename__ = "EmployeeOrders"

    OrderID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.EmployeeID"), nullable=False)
    DeliveryMethod = Column(String(20), nullable=False)
    OfficeAddress = Column(String(255), nullable=True)
    Cabinet = Column(String(50), nullable=True)
    DeliveryDate = Column(Date, nullable=True)
    DeliveryTimeSlot = Column(String(10), nullable=True)
    PaymentMethod = Column(String(10), nullable=False)
    Status = Column(String(20), default="pending")
    TotalAmount = Column(Numeric(10, 2), nullable=False)
    TotalWeight = Column(Integer, default=0)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    ProcessedBy = Column(Integer, ForeignKey("users.EmployeeID"), nullable=True)
    ManagerComment = Column(String, nullable=True)

    user = relationship("User", back_populates="orders", foreign_keys=[UserID])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "OrderItems"

    OrderItemID = Column(Integer, primary_key=True, index=True)
    OrderID = Column(Integer, ForeignKey("EmployeeOrders.OrderID"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID"), nullable=False)
    Quantity = Column(Integer, nullable=False)
    PriceAtOrder = Column(Numeric(10, 2), nullable=False)
    BatchID = Column(Integer, ForeignKey("Batches.BatchID"), nullable=True)
    ExpirationDate = Column(Date, nullable=True)

    order = relationship("EmployeeOrder", back_populates="items")
    product = relationship("Product")
    batch = relationship("Batch", back_populates="order_items")   