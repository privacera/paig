from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from core.utils import current_utc_time
from core.db_session import Base
from sqlalchemy.orm import relationship


class CommonBase(Base):
    __abstract__ = True  # Prevent SQLAlchemy from creating a table for this class
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    create_time = Column(DateTime, default=lambda: current_utc_time())
    update_time = Column(DateTime, default=lambda: current_utc_time(), onupdate=lambda: current_utc_time())
    status = Column(String(255), default='NA')

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])


class EvaluationModel(CommonBase):
    __tablename__ = "evaluation"
    purpose = Column(String(), default='')
    application_name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    application_client = Column(String(255), nullable=False)
    config = Column(String())
    categories = Column(String())
    custom_prompts = Column(String())
    eval_id = Column(String(255), nullable=False)
    cumulative_result = Column(String())
    passed = Column(String(), default='0')
    failed = Column(String(), default='0')
    report_id = Column(String(255), nullable=True, default='')


