from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProductRating(Base):
    __tablename__ = "ProductRatings"

    RatingID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.EmployeeID", ondelete="CASCADE"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID", ondelete="CASCADE"), nullable=False)
    Rating = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("UserID", "ProductID", name="uq_user_product_rating"),)

    user = relationship("User", back_populates="ratings")
    product = relationship("Product", back_populates="ratings")