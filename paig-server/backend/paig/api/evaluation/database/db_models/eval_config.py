from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationConfigModel(CommonBase):
    __tablename__ = "eval_config"
    name = Column(String(), default='')
    purpose = Column(String(), default='')
    application_ids = Column(String(), default=None)
    application_names = Column(String(), default=None)
    categories = Column(String())
    custom_prompts = Column(String())
    version = Column(Integer, nullable=False)
    owner = Column(String(), nullable=True)

    history = relationship('EvaluationConfigHistoryModel', back_populates="eval_config", cascade="all, delete")
    eval_runs = relationship("EvaluationModel",
                             primaryjoin="EvaluationModel.config_id == foreign(EvaluationConfigModel.id)",
                             viewonly=True,
                             uselist=True
                             )


class EvaluationConfigHistoryModel(CommonBase):
    __tablename__ = "eval_config_history"
    name = Column(String(), default='')
    purpose = Column(String(), default='')
    application_ids = Column(String(), default=None)
    application_names = Column(String(), default=None)
    generated_config = Column(String())
    categories = Column(String())
    custom_prompts = Column(String())
    version = Column(Integer, nullable=False)
    owner = Column(String(), nullable=True)
    eval_config_id = Column(Integer, ForeignKey('eval_config.id'), nullable=False)

    eval_config = relationship('EvaluationConfigModel', back_populates="history")

    # Relationship with EvaluationModel based on config_id
    eval_runs = relationship(
        "EvaluationModel",
        primaryjoin="EvaluationModel.config_id == foreign(EvaluationConfigHistoryModel.id)",
        viewonly=True,
        uselist=True
    )