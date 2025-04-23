from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from core.db_models.BaseSQLModel import BaseSQLModel
from sqlalchemy.orm import relationship
from datetime import timezone


class PaigApiKeyModel(BaseSQLModel):
    __tablename__ = "paig_api_key"

    key_id = Column(String(255), unique=True, nullable=False)
    tenant_id = Column(String(255), nullable=False, default='1')
    api_key_name = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_by_id = Column(String(20), nullable=True)
    updated_by_id = Column(String(20), nullable=True)
    key_status = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    last_used_on = Column(DateTime, nullable=True)
    api_key_masked = Column(String(255), nullable=False)
    api_key_encrypted = Column(String(512), nullable=True)
    expiry = Column(DateTime, nullable=True)
    never_expire = Column(Boolean, nullable=False, default=False)
    api_scope_id = Column(String(255), nullable=True, default='3')
    version = Column(String(255), nullable=True, default='v2')
    application_id = Column(Integer, ForeignKey('ai_application.id', ondelete='CASCADE', name='fk_paig_api_key_application_id'), nullable=False)

    ai_app = relationship("AIApplicationModel", back_populates="app_api_keys")

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

    def to_ui_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "tenantId": self.tenant_id,
            "apiKeyName": self.api_key_name,
            "userId": self.user_id,
            "addedById": self.created_by_id,
            "updatedById": self.updated_by_id,
            "keyStatus": self.key_status,
            "description": self.description,
            "apiKeyMasked": self.api_key_masked,
            "tokenExpiry": self.expiry.replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds') if self.expiry else None,
            "neverExpire": self.never_expire,
            "apiScopeId": [self.api_scope_id],
            "version": self.version,
            "applicationId": self.application_id,
            "createTime": self.create_time.replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds') if self.create_time else None,
            "updateTime": self.update_time.replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds') if self.update_time else None
        }

