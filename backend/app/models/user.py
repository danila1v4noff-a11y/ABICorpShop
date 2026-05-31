from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    EmployeeID = Column(Integer, primary_key=True, index=True)
    FIO = Column(String, nullable=False)
    Manager = Column(Integer)
    StatusID = Column(Integer)
    Email = Column(String, unique=True, index=True, nullable=False)
    Login = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)

    cart_items = relationship("CartItem", back_populates="user")
    favorites = relationship("FavoriteProductEmployee", back_populates="user")
    owned_shared_carts = relationship("SharedCart", back_populates="owner")
    orders = relationship("EmployeeOrder", back_populates="user", foreign_keys="[EmployeeOrder.UserID]")
    ratings = relationship("ProductRating", back_populates="user")
    blacklist_entry = relationship("Blacklist", back_populates="user", uselist=False, foreign_keys="[Blacklist.UserID]")
    @property
    def is_active(self):
        return self.StatusID == 1