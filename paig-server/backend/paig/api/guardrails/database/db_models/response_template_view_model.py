from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum

from api.guardrails import ResponseTemplateType
from core.db_session import Base
from core.utils import current_utc_time


class ResponseTemplateViewModel(Base):
    """
    SQLAlchemy model representing combined records from response template and predefined response template.

    Attributes:
        id (int): Primary key identifier for the record.
        status (int): Status of the record.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        response (str): Response template.
        description (str): Description of response template.
        tenant_id (str): Tenant identifier.
        type (ResponseTemplateType): Type of response template.
    """

    __tablename__ = "response_template_view"

    synthetic_id = Column(String(255), primary_key=True, index=True)
    id = Column(Integer, nullable=False, index=True)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(DateTime, index=True, nullable=False, default=lambda: current_utc_time())
    update_time = Column(DateTime, index=True, nullable=False, default=lambda: current_utc_time(),
                         onupdate=lambda: current_utc_time())
    response = Column(String(4000), nullable=False)
    description = Column(String(4000), nullable=True)
    tenant_id = Column(String(255), nullable=False, index=True, default="1")
    type = Column(SQLEnum(ResponseTemplateType), nullable=False)
