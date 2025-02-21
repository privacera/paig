from http.client import responses
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from core.utils import current_utc_time
from core.db_session import Base
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationModel(CommonBase):
    __tablename__ = "eval_run"
    name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    purpose = Column(String(), default='')
    eval_id = Column(String(255), nullable=False)
    config_id = Column(String(255), nullable=False)
    config_name = Column(String())
    application_names = Column(String())
    cumulative_result = Column(String())
    passed = Column(String(), default='0')
    failed = Column(String(), default='0')
    base_run_id = Column(String(255))


    # Relationship with EvaluationConfigHistoryModel based on config_id
    config_history = relationship(
        "EvaluationConfigHistoryModel",
        primaryjoin="foreign(EvaluationModel.config_id) == EvaluationConfigHistoryModel.id",
        viewonly=True
    )
    # One-to-Many relationship with EvaluationResultPromptsModel
    prompts = relationship("EvaluationResultPromptsModel",
                            back_populates="eval_run",
                            cascade="all, delete-orphan"
                        )


class EvaluationResultPromptsModel(CommonBase):
    __tablename__ = "eval_result_prompt"
    eval_run_id = Column(String(255), ForeignKey('eval_run.id', ondelete="CASCADE"), nullable=False)
    eval_id = Column(String(255), nullable=False)
    prompt_uuid = Column(String(255), nullable=False)
    prompt = Column(String(), nullable=False)

    # One-to-Many relationship with EvaluationResultResponseModel
    responses = relationship("EvaluationResultResponseModel",
                                back_populates="prompt",
                                cascade="all, delete-orphan"
                             )
    eval_run = relationship("EvaluationModel", back_populates="prompts")

class EvaluationResultResponseModel(CommonBase):
    __tablename__ = "eval_result_response"
    eval_run_id = Column(String(255), ForeignKey('eval_run.id', ondelete="CASCADE"), nullable=False)
    eval_result_prompt_uuid = Column(String(255), ForeignKey('eval_result_prompt.prompt_uuid'), nullable=False)
    eval_id = Column(String(255), nullable=False)
    response = Column(String(), nullable=True)
    application_name = Column(String(255), nullable=False)
    failure_reason = Column(String(), nullable=True)
    category_score = Column(String(), nullable=True)
    category = Column(String(255), nullable=True)

    # Back-reference to EvaluationResultPromptsModel
    prompt = relationship("EvaluationResultPromptsModel", back_populates="responses")