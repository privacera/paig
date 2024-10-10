from pydantic import BaseModel, ConfigDict
from fastapi import Query
from typing import Union, List


class Conversation(BaseModel):
    conversation_id: str
    created_on: str
    ai_application_name: str
    title: Union[int, None]
    client_app_id: Union[int, None]


class GetAllConversationsRequest(BaseModel):
    offset: Union[int, None] = Query(default=None)
    limit: Union[int, None] = Query(default=None)


class DeleteConversationsRequest(BaseModel):
    conversations_id: str


class GetMesgByIDRequest(BaseModel):
    offset: Union[int, None] = Query(default=None)
    limit: Union[int, None] = Query(default=None)


class PostPromptRequest(BaseModel):
    prompt: str


class PostCreateConversationRequest(BaseModel):
    model_config = ConfigDict()
    model_config['protected_namespaces'] = ()

    prompt: str
    ai_application_name: str


class GetAllConversationsResponse(BaseModel):
    offset: Union[int, None] = Query(default=None)
    limit: Union[int, None] = Query(default=None)
    items: List[Conversation]
    total: int
    limit: int


class PostCreateConversationResponse(BaseModel):
    conversation_id: str
    created_on: str
    title: str
    client_app_id: str
    ai_application_name: str
    messages: list

