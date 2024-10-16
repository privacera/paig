from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from core.database import Base


class Messages(Base):
    """
        NOTE:
                1. Few values kept it as NULL for base application
        """
    __tablename__ = "messages"
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    message_uuid = Column(String(50), nullable=False, index=True, unique=True, default=str(uuid4()))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True, index=True)
    created_on = Column(DateTime, default=func.now(), index=True)
    content = Column(String, nullable=True)
    original_content = Column(String, nullable=True)
    type = Column(String(50), nullable=True, index=True)
    prompt_id = Column(String(50), nullable=True, index=True)
    auth_status = Column(String(50), nullable=True, default=None)

    conversation = relationship("Conversations", back_populates="messages")

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])
