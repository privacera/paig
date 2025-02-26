from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, JSON
from core.utils import current_utc_time
from core.db_session import Base


class CommonBase(Base):
    __abstract__ = True  # Prevent SQLAlchemy from creating a table for this class
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    create_time = Column(DateTime, default=lambda: current_utc_time())
    update_time = Column(DateTime, default=lambda: current_utc_time(), onupdate=lambda: current_utc_time())
    status = Column(String(255), default='NA')

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])