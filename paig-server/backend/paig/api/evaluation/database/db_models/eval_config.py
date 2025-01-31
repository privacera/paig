from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, JSON
from core.utils import current_utc_time
from core.db_session import Base
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationConfigModel(CommonBase):
    __tablename__ = "eval_config"
    label = Column(String(), default='')
    purpose = Column(String(), default='')
    application_ids = Column(String(), default=None)
    application_names = Column(String(), default=None)
    categories = Column(String())
    custom_prompts = Column(String())
    version = Column(Integer, nullable=False)

    history = relationship('EvaluationConfigHistoryModel', back_populates="eval_config", cascade="all, delete")


class EvaluationConfigHistoryModel(CommonBase):
    __tablename__ = "eval_config_history"
    label = Column(String(), default='')
    purpose = Column(String(), default='')
    application_ids = Column(String(), default=None)
    application_names = Column(String(), default=None)
    generated_config = Column(String())
    categories = Column(String())
    custom_prompts = Column(String())
    version = Column(Integer, nullable=False)
    eval_config_id = Column(Integer, ForeignKey('eval_config.id'), nullable=False)

    eval_config = relationship('EvaluationConfigModel', back_populates="history")