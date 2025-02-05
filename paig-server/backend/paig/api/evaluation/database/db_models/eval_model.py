from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from core.utils import current_utc_time
from core.db_session import Base
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationModel(CommonBase):
    __tablename__ = "eval_run"
    name = Column(String(255), nullable=True)
    owner = Column(String(255), nullable=False)
    eval_id = Column(String(255), nullable=False)
    config_id = Column(String(255), nullable=False)
    config_name = Column(String())
    application_names = Column(String())
    cumulative_result = Column(String())
    passed = Column(String(), default='0')
    failed = Column(String(), default='0')
    # we can delete report id once reporting page is created
    report_id = Column(String(255), nullable=True, default='')
    base_run_id = Column(String(255))


    # Relationship with EvaluationConfigHistoryModel based on config_id
    config_history = relationship(
        "EvaluationConfigHistoryModel",
        primaryjoin="foreign(EvaluationModel.config_id) == EvaluationConfigHistoryModel.id",
        viewonly=True
    )