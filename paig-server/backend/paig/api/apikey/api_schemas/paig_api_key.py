from core.api_schemas.base_view import BaseView
from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from core.factory.database_initiator import BaseAPIFilter
from fastapi import Query




class PaigApiKeyView(BaseView):
    """
    A model representing an API key.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        tenant_id (str): The ID of the tenant associated with the API key.
        api_key_name (str): The name of the API key.
        user_id (str): The ID of the user associated with the API key.
        created_by_id (str): The ID of the user who created the API key.
        updated_by_id (str): The ID of the user who last updated the API key.
        key_status (str): The status of the API key.
        description (str): The description of the API key.
        last_used_on (str): The last time the API key was used.
        api_key_masked (str): The masked value of the API key.
        api_key_encrypted (str): The encrypted value of the API key.
        expiry (str): The expiry time of the token.
        never_expire (bool): A flag indicating whether the token never expires.
        api_scope_id (str): The ID of the API scope associated with the API key.
        version (str): The version of the API key.
        application_id (int): The ID of the application associated with the API key.
    """
    tenant_id: int = Field(default=None, description="The ID of the tenant associated with the API key", alias="tenantId")
    api_key_name: str = Field(default=None, description="The name of the API key", alias="apiKeyName")
    user_id: int = Field(default=None, description="The ID of the user associated with the API key", alias="userId")
    created_by_id: int = Field(default=None, description="The ID of the user who created the API key", alias="addedById")
    updated_by_id: int = Field(default=None, description="The ID of the user who last updated the API key", alias="updatedById")
    key_status: str = Field(default=None, description="The status of the API key")
    description: str = Field(default=None, description="The description of the API key")
    last_used_on: str = Field(default=None, description="The last time the API key was used", alias="lastUsedOn")
    api_key_masked: str = Field(default=None, description="The masked value of the API key", alias="apiKeyMasked")
    api_key_encrypted: str = Field(default=None, description="The encrypted value of the API key", alias="apiKeyEncrypted")
    expiry: str = Field(default=None, description="The expiry time of the token", alias="tokenExpiry")
    never_expire: bool = Field(default=None, description="A flag indicating whether the token never expires", alias="neverExpire")
    api_scope_id: str = Field(default=None, description="The ID of the API scope associated with the API key", alias="apiScopeId")
    version: str = Field(default=None, description="The version of the API key")
    application_id: int = Field(default=None, description="The ID of the application associated with the API key", alias="applicationId")

    model_config = BaseView.model_config



class GenerateApiKeyBase(BaseModel):
    api_key_name: str = Field(None, description="Name of the API key", alias="apiKeyName")
    description: str = Field(None, description="Description of the API key", alias="description")
    never_expire: bool = Field(None, description="Indicates if the key never expires", alias="neverExpire")
    expiry: datetime = Field(None, description="Token expiration timestamp", alias="tokenExpiry")
    application_id: int = Field(..., description="Application ID associated with the API key", alias="applicationId")

class GenerateApiKeyRequest(GenerateApiKeyBase):
    scopes: List[int] = Field(..., description="List of scope IDs associated with the key")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class GenerateApiKeyResponse(GenerateApiKeyBase):
    id: int = Field(..., description="Unique identifier for the API key", alias="id")
    user_id: int = Field(..., description="User ID associated with the API key", alias="userId")
    created_by_id: int = Field(None, description="ID of the user who added the API key", alias="addedById")
    updated_by_id: int = Field(None, description="ID of the user who last updated the key", alias="updatedById")
    status: int = Field(..., description="Status of the API key", alias="status")
    create_time: datetime = Field(..., description="Creation timestamp", alias="createTime")
    update_time: datetime = Field(..., description="Update timestamp", alias="updateTime")
    key_status: str = Field(..., description="Status of the API key, e.g., ACTIVE", alias="keyStatus")
    tenant_id: str = Field(..., description="Tenant ID associated with the API key", alias="tenantId")
    api_key_masked: str = Field(..., description="Masked API key value", alias="apiKeyMasked")
    api_scope_id: List[int] = Field(..., description="List of scope IDs associated with the key", alias="apiScopeId")
    version: str = Field(..., description="Version of the API key", alias="version")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class IncludeApiQueryParams(BaseAPIFilter):
    api_key_name: Optional[str] = Field(None, description="Name of the API key", alias="apiKeyName")
    description: Optional[str] = Field(None, description="Description of the API key")
    exact_match: Optional[bool] = Field(False, description="Indicates if the search should be an exact match", alias="exactMatch")


def include_api_query_params(
        include_query_api_key_name: Optional[str] = Query(None, alias="includeQuery.apiKeyName"),
        include_query_description: Optional[str] = Query(None, alias="includeQuery.description"),
        include_query_exact_match: Optional[bool] = Query(False, alias="includeQuery.exactMatch")
) -> IncludeApiQueryParams:
    return IncludeApiQueryParams(
        apiKeyName=include_query_api_key_name,
        description=include_query_description,
        exactMatch=include_query_exact_match
    )







