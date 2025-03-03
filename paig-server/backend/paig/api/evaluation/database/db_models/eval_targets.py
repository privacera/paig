from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, JSON, Text
from core.utils import current_utc_time
from core.db_session import Base
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationTargetModel(CommonBase):
    """
    Model for EvaluationTargetModel
    application_id: The application id
    config: The config of the target
    name: The name of the target
    url: The url of the target
    """
    __tablename__ = "eval_target"
    # application id can be none
    application_id = Column(Integer, ForeignKey('ai_application.id') ,nullable=True)
    config = Column(JSON, nullable=False)
    name = Column(String(255), default='')
    url = Column(Text(), default='')

    ai_app = relationship("AIApplicationModel", back_populates="host")
