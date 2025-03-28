from sqlalchemy import Column, String, Enum as SQLEnum
from core.db_models.BaseSQLModel import BaseSQLModel
from api.apikey.database.db_models.base_model import EncryptionKeyStatus



class PaigLevel1EncryptionKeyModel(BaseSQLModel):
    __tablename__ = "paig_level1_encryption_key"

    key_id = Column(String(255), unique=True, nullable=False)
    created_by_id = Column(String(20), nullable=True)
    updated_by_id = Column(String(20), nullable=True)
    paig_key_value = Column(String(1024), nullable=False)
    key_status = Column(SQLEnum(EncryptionKeyStatus), nullable=False)

    def set_attribute(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])