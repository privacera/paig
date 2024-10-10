from sqlalchemy import Boolean, Column, Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class User(Base):
    """
        NOTE:
            1. Few values kept it as NULL for base application
    """
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), unique=True, nullable=True)
    email_id = Column(String(100), unique=True, index=True, nullable=True)
    role = Column(String(50), nullable=True)
    created_on = Column(DateTime, index=True, default=func.now())
    modified_on = Column(DateTime, index=True, default=func.now())
    is_active = Column(Boolean, default=True)

    conversations = relationship("Conversations", back_populates="user")

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])