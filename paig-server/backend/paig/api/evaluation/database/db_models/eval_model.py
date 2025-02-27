from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from api.evaluation.database.db_models.base_model import CommonBase


class EvaluationModel(CommonBase):
    """
    Model for EvaluationModel
    name: The name of the evaluation
    owner: The owner of the evaluation
    purpose: The purpose of the evaluation
    eval_id: The evaluation id
    config_id: The config id of the eval
    config_name: The config name of the eval
    application_names: The application names ran in eval
    cumulative_result: The cumulative result of eval
    passed: The number of evaluations passed
    failed: The number of evaluations failed
    base_run_id: The base run id in case of rerun
    """
    __tablename__ = "eval_run"
    name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    purpose = Column(Text(), default='')
    eval_id = Column(String(255), nullable=False)
    config_id = Column(String(255), nullable=False)
    config_name = Column(String(255))
    application_names = Column(Text())
    cumulative_result = Column(Text())
    passed = Column(String(255), default='0')
    failed = Column(String(255), default='0')
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
    """
    EvaluationResultPromptsModel
    eval_run_id: The evaluation run id
    eval_id: The evaluation id
    prompt_uuid: The prompt uuid
    prompt: The prompt text
    """
    __tablename__ = "eval_result_prompt"
    eval_run_id = Column(String(255), ForeignKey('eval_run.id', ondelete="CASCADE"), nullable=False)
    eval_id = Column(String(255), nullable=False)
    prompt_uuid = Column(String(255), nullable=False)
    prompt = Column(Text(), nullable=False)

    # One-to-Many relationship with EvaluationResultResponseModel
    responses = relationship("EvaluationResultResponseModel",
                                back_populates="prompt",
                                cascade="all, delete-orphan"
                             )
    eval_run = relationship("EvaluationModel", back_populates="prompts")

class EvaluationResultResponseModel(CommonBase):
    """
    EvaluationResultResponseModel
    eval_run_id: The evaluation run id
    eval_result_prompt_uuid: The prompt uuid
    eval_id: The evaluation id
    response: The response text
    application_name: The application name used for the eval
    failure_reason: The failure reason
    category_score: The category score of the prompt
    category: The category ran for against the prompt
    """
    __tablename__ = "eval_result_response"
    eval_run_id = Column(String(255), ForeignKey('eval_run.id', ondelete="CASCADE"), nullable=False)
    eval_result_prompt_uuid = Column(String(255), ForeignKey('eval_result_prompt.prompt_uuid'), nullable=False)
    eval_id = Column(String(255), nullable=False)
    response = Column(Text(), nullable=True)
    application_name = Column(String(255), nullable=False)
    failure_reason = Column(Text(), nullable=True)
    category_score = Column(Text(), nullable=True)
    category = Column(String(255), nullable=True)

    # Back-reference to EvaluationResultPromptsModel
    prompt = relationship("EvaluationResultPromptsModel", back_populates="responses")