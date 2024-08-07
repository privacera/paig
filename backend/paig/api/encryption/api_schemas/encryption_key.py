from typing import Optional

from pydantic import Field

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType, EncryptionKeyStatus


class EncryptionKeyView(BaseView):
    """
    A model representing an encryption key.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        public_key (str): The public key.
        private_key (str): The private key.
        key_status (EncryptionKeyStatus): The status of the key.
        key_type (EncryptionKeyType): The type of the key.
    """

    public_key: Optional[str] = Field(None, description="The public key", alias="publicKeyValue")
    private_key: Optional[str] = Field(None, description="The private key", alias="privateKeyValue")
    key_status: Optional[EncryptionKeyStatus] = Field(None, description="The status of the key", alias="keyStatus")
    key_type: Optional[EncryptionKeyType] = Field(None, description="The type of the key", alias="keyType")


class EncryptionKeyFilter(BaseAPIFilter):
    """
    A model representing a filter for encryption keys.

    Inherits from:
        BaseAPIFilter: The base filter model.

    Attributes:
        key_status (str, optional): Filter by key status.
        key_type (str, optional): Filter by key type.
    """

    key_status: Optional[str] = Field(None, description="The status of the key")
    key_type: Optional[EncryptionKeyType] = Field(None, description="The type of the key")
