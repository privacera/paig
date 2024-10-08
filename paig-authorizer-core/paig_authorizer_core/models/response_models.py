from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict


class AuthzResponse(BaseModel):
    """
    Represents an authorization response.

    Attributes:
        authorized (bool): Whether the request is authorized or not.
        enforce (bool): Whether to enforce the request or not.
        request_id (str): Id of the request.
        request_date_time (datetime): Date and time of the request.
        user_id (str): Id of the user.
        application_name (str): Name of the AI application.
        masked_traits (Optional[Dict[str, str]]): Traits to be masked.
        context (Optional[Dict[str, Any]]): Additional context as list of key-value pairs.
        status_code (int): Request status code. Zero means success. Non-zero means failure.
        status_message (str): Message associated with the status code.
        reason (str): Reason for the status code.
        paig_policy_ids (List[int]): List of Paig audit ids.
    """

    authorized: bool = Field(False, alias="authorized")
    enforce: bool = Field(True, alias="enforce")
    request_id: str = Field(None, alias="requestId")
    request_date_time: datetime = Field(None, alias="requestDateTime")
    user_id: str = Field(None, alias="userId")
    application_name: str = Field(None, alias="applicationName")
    masked_traits: Optional[Dict[str, str]] = Field(None, alias="maskedTraits")
    context: Optional[Dict[str, Any]] = Field(None)
    status_code: int = Field(None, alias="statusCode")
    status_message: str = Field(None, alias="statusMessage")
    reason: str = Field(None, alias="reason")
    paig_policy_ids: List[int] = Field([], alias="paigPolicyIds")

    model_config = ConfigDict(
        populate_by_name=True
    )


class VectorDBAuthzResponse(BaseModel):
    """
    Represents a VectorDB authorization response.

    Attributes:
        vector_db_policy_info (List[Dict[str, str]]): Information about the VectorDB policies.
        vector_db_id (int): The unique identifier for the VectorDB.
        vector_db_name (str): The name of the VectorDB.
        vector_db_type (str): The type of the VectorDB.
        user_enforcement (int): Enforcement level for the user.
        group_enforcement (int): Enforcement level for the group.
        filter_expression (str): Filter expression applied to the request.
        reason (str): Reason for the status code.
    """

    vector_db_policy_info: List[Dict] = Field([], alias="vectorDBPolicyInfo")
    vector_db_id: int = Field(None, alias="vectorDBId")
    vector_db_name: str = Field(None, alias="vectorDBName")
    vector_db_type: str = Field(None, alias="vectorDBType")
    user_enforcement: int = Field(None, alias="userEnforcement")
    group_enforcement: int = Field(None, alias="groupEnforcement")
    filter_expression: str = Field(None, alias="filterExpression")
    reason: str = Field(None, alias="reason")

    model_config = ConfigDict(
        populate_by_name=True
    )