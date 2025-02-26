from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationConfigModel(CommonBase):
    """
    EvaluationConfigModel is the model for the evaluation configuration.
    name: Name of the evaluation configuration.
    purpose: Purpose of the evaluation configuration.
    application_ids: Application IDs for the evaluation configuration.
    application_names: Application names for the evaluation configuration.
    categories: Categories for the evaluation configuration.
    custom_prompts: Custom prompts for the evaluation configuration.
    version: Version of the evaluation configuration.
    owner: Owner of the evaluation configuration.
    """
    __tablename__ = "eval_config"
    name = Column(String(255), default='')
    purpose = Column(Text(), default='')
    application_ids = Column(String(255), default=None)
    application_names = Column(Text(), default=None)
    categories = Column(Text())
    custom_prompts = Column(Text())
    version = Column(Integer, nullable=False)
    owner = Column(String(255), nullable=True)

    history = relationship('EvaluationConfigHistoryModel', back_populates="eval_config", cascade="all, delete")
    eval_runs = relationship("EvaluationModel",
                             primaryjoin="EvaluationModel.config_id == foreign(EvaluationConfigModel.id)",
                             viewonly=True,
                             uselist=True
                             )


class EvaluationConfigHistoryModel(CommonBase):
    """
    EvaluationConfigHistoryModel is the model for the evaluation configuration history.
    name: Name of the evaluation configuration.
    purpose: Purpose of the evaluation configuration.
    application_ids: Application IDs for the evaluation configuration.
    generated_config: Generated configuration for the evaluation configuration.
    categories: Categories for the evaluation configuration.
    custom_prompts: Custom prompts for the evaluation configuration.
    version: Version of the evaluation configuration.
    """
    __tablename__ = "eval_config_history"
    name = Column(String(255), default='')
    purpose = Column(Text(), default='')
    application_ids = Column(String(255), default=None)
    application_names = Column(Text(), default=None)
    generated_config = Column(Text())
    categories = Column(Text())
    custom_prompts = Column(Text())
    version = Column(Integer, nullable=False)
    owner = Column(String(255), nullable=True)
    eval_config_id = Column(Integer, ForeignKey('eval_config.id'), nullable=False)

    eval_config = relationship('EvaluationConfigModel', back_populates="history")

    # Relationship with EvaluationModel based on config_id
    eval_runs = relationship(
        "EvaluationModel",
        primaryjoin="EvaluationModel.config_id == foreign(EvaluationConfigHistoryModel.id)",
        viewonly=True,
        uselist=True
    )