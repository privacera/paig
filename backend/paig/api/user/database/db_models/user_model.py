from sqlalchemy import Boolean, Column, String
from datetime import datetime
from sqlalchemy.orm import relationship
from api.user.database.db_models.base_model import CommonBase
import uuid


class User(CommonBase):
    __tablename__ = "user"
    username = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    is_tenant_owner = Column(Boolean, nullable=False, default=False)
    password = Column(String(255), nullable=True)
    session_token = Column(String(255), nullable=True)

    memberships = relationship("GroupMembers", back_populates="user", cascade="all, delete-orphan", overlaps="groups, user")
    groups = relationship("Groups", secondary="group_member", back_populates="user", overlaps="memberships")

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

    def to_ui_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "createTime": self.create_time.isoformat() if isinstance(self.create_time, datetime) else self.create_time,
            "updateTime": self.update_time.isoformat() if isinstance(self.update_time, datetime) else self.update_time,
            "roles": ["OWNER"] if self.is_tenant_owner else ["USER"]
        }


class Tenant(CommonBase):
    __tablename__ = "tenant"
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()))

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])