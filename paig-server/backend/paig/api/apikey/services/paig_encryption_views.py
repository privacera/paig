from core.api_schemas.base_view import BaseView
from pydantic import Field


class LevelEncryptionKeyBaseView(BaseView):
    """
    A base model for encryption keys.
    Inherits from:
        BaseView: The base model containing common fields.
    Attributes:
        key_id (str): The ID of the key.
        created_by_id (str): The ID of the user who created the key.
        updated_by_id (str): The ID of the user who last updated the key.
        key_status (str): The status of the key.
    """
    key_id: str = Field(default=None, description="The ID of the key", alias="keyId")
    created_by_id: str = Field(default=None, description="The ID of the user who created the key", alias="createdById")
    updated_by_id: str = Field(default=None, description="The ID of the user who last updated the key",
                               alias="updatedById")
    key_status: str = Field(None, description="The status of the key", alias="keyStatus")



class PaigLevel1EncryptionKeyView(LevelEncryptionKeyBaseView):
    """
    A model representing a level 1 encryption key.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        paig_key_value (str): The value of the key.
    """
    paig_key_value: str = Field(default=None, description="The value of the key", alias="Level1KeyValue")

    model_config = BaseView.model_config



class PaigLevel2EncryptionKeyView(LevelEncryptionKeyBaseView):
    """
    A model representing a level 2 encryption key.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        paig_key_value (str): The value of the key.
    """
    paig_key_value: str = Field(default=None, description="The value of the key", alias="Level2KeyValue")

    model_config = BaseView.model_config