from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "Products"

    ProductID = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255), nullable=False)
    Description = Column(Text, nullable=True)
    Price = Column(Numeric(10, 2), nullable=False)
    Weight = Column(Integer, nullable=True)
    ImageURL = Column(String(500), nullable=True)
    CategoryID = Column(Integer, ForeignKey("Categories.CategoryID"), nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    cart_items = relationship("CartItem", back_populates="product")
    favorited_by = relationship("FavoriteProductEmployee", back_populates="product")
    batches = relationship("Batch", back_populates="product", cascade="all, delete-orphan")
    category = relationship("Category", backref="products")
    ratings = relationship("ProductRating", back_populates="product")