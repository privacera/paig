from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict


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
    request_date_time: datetime = Field(None, alias="requestDateTime")

    model_config = ConfigDict(
        populate_by_name=True
    )


class VectorDBAuthzRequest(BaseModel):
    """
    Represents a VectorDB authorization request.

    Attributes:
        user_id (str): The unique identifier for the user. This is a mandatory field.
        application_key (str): The application key. This is a mandatory field.
    """

    user_id: str = Field(None, alias="userId")
    application_key: str = Field(None, alias="applicationKey")

    model_config = ConfigDict(
        populate_by_name=True
    )