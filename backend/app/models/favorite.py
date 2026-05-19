from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class FavoriteProductEmployee(Base):
    __tablename__ = "FavoriteProductEmployee"

    FavoriteID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.EmployeeID", ondelete="CASCADE"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID", ondelete="CASCADE"), nullable=False)
    AddedAt = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("UserID", "ProductID", name="uq_favorite_user_product"),)

    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorited_by")