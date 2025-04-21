from sqlalchemy import Column, Integer, String, JSON, Text
from .base_model import CommonBase


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
    application_id = Column(Integer, nullable=True)
    config = Column(JSON, nullable=False)
    name = Column(String(255), default='')
    url = Column(Text(), default='')
    target_user = Column(String(255), default='NA')
    tenant_id = Column(String(255), nullable=False, index=True, default="1")
