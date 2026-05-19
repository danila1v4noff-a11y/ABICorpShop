from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CartItem(Base):
    __tablename__ = "CartItem"

    # Предполагаемые имена колонок – уточни по своей БД
    CartItemID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.EmployeeID"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID"), nullable=False)
    Quantity = Column(Integer, default=1)

    # Отношения (если нужны)
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")