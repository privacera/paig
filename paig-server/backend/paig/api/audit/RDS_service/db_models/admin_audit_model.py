from sqlalchemy import Column, Integer, String, JSON, Double
from core.db_session import Base
from core.utils import current_utc_time_epoch


class AdminAuditModel(Base):
    __tablename__ = 'admin_audits'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    acted_by_user_id = Column(Integer, nullable=True, index=True)
    acted_by_user_name = Column(String(255), nullable=True, index=True)
    action = Column(String(255), nullable=True)
    log_id = Column(String(255), nullable=True, index=True)
    log_time = Column(Double, index=True, nullable=False, default=lambda: current_utc_time_epoch())
    object_id = Column(Integer, nullable=True)
    object_name = Column(String(255), nullable=True)
    object_type = Column(String(255), nullable=True)
    object_state = Column(JSON, nullable=True)
    object_state_previous = Column(JSON, nullable=True)
    tenant_id = Column(String(255), nullable=False, index=True, default="1")
    transaction_id = Column(String(255), nullable=True, index=True)
    transaction_sequence_number = Column(Integer, nullable=True)

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

