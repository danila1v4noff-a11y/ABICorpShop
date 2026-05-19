from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Category(Base):
    __tablename__ = "Categories"

    CategoryID = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), unique=True, nullable=False)
    Description = Column(Text, nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())