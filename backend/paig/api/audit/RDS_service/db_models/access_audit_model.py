from sqlalchemy import Column, Integer, String, JSON, Double
from core.db_session import Base


class AccessAuditModel(Base):
    __tablename__ = 'access_audits'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    app_key = Column(String(255), nullable=True)
    app_name = Column(String(255), nullable=True, index=True)
    client_app_key = Column(String(255), nullable=True)
    client_app_name = Column(String(255), nullable=True)
    client_host_name = Column(String(255), nullable=True)
    client_ip = Column(String(255), nullable=True)
    context = Column(JSON, nullable=True)
    event_id = Column(String(255), nullable=True)
    event_time = Column(Double, nullable=True)
    masked_traits = Column(JSON, nullable=True)
    messages = Column(JSON, nullable=True)
    no_of_tokens = Column(Integer, nullable=True)
    paig_policy_ids = Column(JSON, nullable=True)
    request_id = Column(String(255), nullable=True)
    request_type = Column(String(255), nullable=True, index=True)
    result = Column(String(255), nullable=True, index=True)
    tenant_id = Column(String(255), nullable=True)
    thread_id = Column(String(255), nullable=True, index=True)
    thread_sequence_number = Column(Integer, nullable=True)
    traits = Column(JSON, nullable=True)
    user_id = Column(String(255), nullable=True, index=True)
    encryption_key_id = Column(Integer, nullable=True)
    log_time = Column(Integer, nullable=True)
    transaction_sequence_number = Column(Integer, nullable=True)

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

