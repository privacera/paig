from sqlalchemy import Column, Integer, DateTime

from core.db_session import Base
from core.utils import current_utc_time


class BaseSQLModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(DateTime, index=True, nullable=False, default=current_utc_time())
    update_time = Column(DateTime, index=True, nullable=False, default=current_utc_time(), onupdate=current_utc_time())

    def set_attribute(self, attributes):
        """
        Set multiple attributes of the AI application model instance.

        Args:
            attributes (dict): Dictionary where keys are attribute names and values are new values.
        """
        for key in attributes:
            setattr(self, key, attributes[key])