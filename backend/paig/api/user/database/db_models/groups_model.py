from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from datetime import datetime
from sqlalchemy.orm import relationship
from api.user.database.db_models.base_model import CommonBase


class Groups(CommonBase):
    __tablename__ = "group"
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True, default=None)

    # Relationships
    user = relationship("User", secondary="group_member", back_populates="groups", overlaps="user")

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

    def to_ui_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "createTime": self.create_time.isoformat() if isinstance(self.create_time, datetime) else self.create_time,
            "updateTime": self.update_time.isoformat() if isinstance(self.update_time, datetime) else self.update_time
        }


class GroupMembers(CommonBase):
    __tablename__ = "group_member"
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # Define relationship to User
    user = relationship("User", back_populates="memberships", overlaps="groups")

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

    def to_ui_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "groupId": self.group_id,
            "userId": self.user_id,
            "createTime": self.create_time.isoformat() if isinstance(self.create_time, datetime) else self.create_time,
            "updateTime": self.update_time.isoformat() if isinstance(self.update_time, datetime) else self.update_time
        }

    # Indexes
    __table_args__ = (
        Index('idx_group_user', 'group_id', 'user_id', unique=True),
    )
