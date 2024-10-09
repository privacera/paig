
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, BigInteger
from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Conversations(Base):
    """
           NOTE:
               1. Few values kept it as NULL for base application
    """
    __tablename__ = "conversations"
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    conversation_uuid = Column(String(50), nullable=False, index=True, unique=True, default=str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    created_on = Column(DateTime, index=True, default=func.now())
    modified_on = Column(DateTime, index=True, default=func.now())
    ai_application_name = Column(String(100), index=True, nullable=False)
    title = Column(String(100), nullable=True)  # need to discuss uniqueness
    is_deleted = Column(Boolean, default=False, nullable=False)
    client_app_id = Column(String, nullable=True, index=True)

    user = relationship("User", back_populates="conversations", lazy='joined')
    messages = relationship("Messages", back_populates="conversation")

    __mapper_args__ = {"eager_defaults": True}

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])