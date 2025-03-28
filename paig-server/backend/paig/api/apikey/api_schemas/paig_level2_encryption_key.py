from core.api_schemas.base_view import BaseView
from pydantic import Field
from typing import Optional
from api.apikey.database.db_models.base_model import EncryptionKeyStatus


class PaigLevel2EncryptionKeyView(BaseView):
    """
    A model representing a level 2 encryption key.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        created_by_id (str): The ID of the user who created the key.
        updated_by_id (str): The ID of the user who last updated the key.
        paig_key_value (str): The value of the key.
        key_status (str): The status of the key.
    """
    key_id: str = Field(default=None, description="The ID of the key", alias="keyId")
    created_by_id: str = Field(default=None, description="The ID of the user who created the key", alias="createdById")
    updated_by_id: str = Field(default=None, description="The ID of the user who last updated the key",
                               alias="updatedById")
    paig_key_value: str = Field(default=None, description="The value of the key", alias="Level2KeyValue")
    key_status: Optional[EncryptionKeyStatus] = Field(None, description="The status of the key", alias="keyStatus")

    model_config = BaseView.model_config