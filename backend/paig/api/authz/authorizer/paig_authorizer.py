from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.utils import current_utc_time


class AuthzRequest(BaseModel):
    """
    Represents an authorization request.

    Attributes:
        conversation_id (Optional[str]): The unique identifier for the conversation.
            This is the parent for all the prompts and replies in the thread.
        request_id (str): The unique identifier for the request. Both prompts and responses have unique
            requestIds and in a conversation, they will share the same conversationId.
        thread_id (str): If this is a reply or enriched_prompts, then threadId is the requestId of the prompt.
            This helps in associating the enriched_prompt and replies with the prompt.
        sequence_number (int): Sequence number of the messages within the request. E.g., user prompt might lead to
            multiple enriched prompts. Sequence starts from 1.
        application_key (str): AI application key. This is mandatory for all requests. Ideally, this should come from
            the plugin.
        client_application_key (str): Client application key. If not sent, unknown will be used.
        enforce (bool): Whether the actions are enforced or not. Defaults to True.
        user_id (str): The unique identifier for the user.
        request_type (str): The type of request. Valid values are: prompt, reply, enriched_prompt.
        traits (List[str]): List of traits.
        context (Optional[Dict[str, Any]]): Additional context as list of key-value pairs.
        request_date_time (datetime): Date and time of the request. If not sent by client,
            server will generate one and return in the response.
    """

    conversation_id: Optional[str] = Field(None, alias="conversationId")
    request_id: str = Field(None, alias="requestId")
    thread_id: str = Field(None, alias="threadId")
    sequence_number: int = Field(0, alias="sequenceNumber")
    application_key: str = Field(None, alias="applicationKey")
    client_application_key: str = Field("unknown", alias="clientApplicationKey")
    enforce: bool = Field(True)
    user_id: str = Field(None, alias="userId")
    request_type: str = Field(None, alias="requestType")
    traits: List[str] = Field(None)
    context: Optional[Dict[str, Any]] = Field(None)
    request_date_time: datetime = Field(current_utc_time(), alias="requestDateTime")

    class Config:
        allow_population_by_field_name = True


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

    class Config:
        allow_population_by_field_name = True


class VectorDBAuthzRequest(BaseModel):
    """
    Represents a VectorDB authorization request.

    Attributes:
        user_id (str): The unique identifier for the user. This is a mandatory field.
        application_key (str): The application key. This is a mandatory field.
    """

    user_id: str = Field(None, alias="userId")
    application_key: str = Field(None, alias="applicationKey")

    class Config:
        allow_population_by_field_name = True


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

    class Config:
        allow_population_by_field_name = True


class PAIGAuthorizer(ABC):

    @abstractmethod
    async def authorize(self, request: AuthzRequest) -> AuthzResponse:
        """
        Authorize the request.

        Args:
            request (AuthzRequest): The authorization request.

        Returns:
            AuthzResponse: The authorization response.
        """
        pass

    @abstractmethod
    async def authorize_vector_db(self, request: VectorDBAuthzRequest) -> VectorDBAuthzResponse:
        """
        Authorize the VectorDB request.

        Args:
            request (VectorDBAuthzRequest): The VectorDB authorization request.

        Returns:
            VectorDBAuthzResponse: The VectorDB authorization response.
        """
        pass
