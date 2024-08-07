from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


class VectorDBPolicyModel(BaseSQLModel):
    """
    A model representing a VectorDB policy.

    Inherits from:
        BaseSQLModel: The base model containing common fields.

    Attributes:
        name (str): The name of the Vector DB policy.
        description (str): The description of the Vector DB policy.
        allowed_users (list[str]): The list of allowed users.
        allowed_groups (list[str]): The list of allowed groups.
        allowed_roles (list[str]): The list of allowed roles.
        denied_users (list[str]): The list of denied users.
        denied_groups (list[str]): The list of denied groups.
        denied_roles (list[str]): The list of denied roles.
        metadata_key (str): The metadata key for the policy.
        metadata_value (str): The metadata value for the policy.
        operator (str): The operator for the policy.
        vector_db_id (int): The vector db id for the policy.
    """
    __tablename__ = "vector_db_policy"

    name = Column(String(255), nullable=True)
    description = Column(String(4000), nullable=True)
    vector_db_id = Column(Integer, ForeignKey('vector_db.id', ondelete='CASCADE', name='fk_vector_db_policy_vector_db_id'), nullable=False)
    metadata_key = Column(String(255), nullable=False)
    metadata_value = Column(String(255), nullable=False)
    operator = Column(String(255), nullable=False)
    allowed_users = Column(CommaSeparatedList, nullable=True)
    allowed_groups = Column(CommaSeparatedList, nullable=True)
    allowed_roles = Column(CommaSeparatedList, nullable=True)
    denied_users = Column(CommaSeparatedList, nullable=True)
    denied_groups = Column(CommaSeparatedList, nullable=True)
    denied_roles = Column(CommaSeparatedList, nullable=True)

    vector_db = relationship("VectorDBModel", back_populates="vector_db_policies")
