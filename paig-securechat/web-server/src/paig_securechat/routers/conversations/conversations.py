from typing import Annotated
from fastapi import APIRouter, Response, Request, Depends, Query
from app.api_schemas.conversations import GetAllConversationsRequest, GetMesgByIDRequest, GetAllConversationsResponse
from app.api_schemas.conversations import DeleteConversationsRequest, PostPromptRequest, PostCreateConversationRequest
from core.factory.controller_initiator import ControllerInitiator
from app.controllers import ConversationController
from app.api_schemas import CommonErrorResponse
from core.security.authentication import get_auth_user
conversations_router = APIRouter()


@conversations_router.get("", responses=CommonErrorResponse)
async def get_all_conversations(
        request: Request,
        query_params: Annotated[GetAllConversationsRequest, Depends(GetAllConversationsRequest)],
        conversation_controller: ConversationController = Depends(ControllerInitiator().get_conversation_controller),
        user: dict = Depends(get_auth_user)
        ):
    offset = query_params.offset
    limit = query_params.limit
    user_id = user['user_id']
    return await conversation_controller.get_conversations(user_id=user_id, skip=offset, limit=limit)


@conversations_router.get("/{conversation_uuid}", responses=CommonErrorResponse)
async def get_messages_by_conversation_id(
        conversation_uuid: str,
        request: Request,
        query_params: Annotated[GetMesgByIDRequest, Depends(GetMesgByIDRequest)],
        conversation_controller: ConversationController = Depends(ControllerInitiator().get_conversation_controller),
        user: dict = Depends(get_auth_user)
        ):
    offset = query_params.offset
    limit = query_params.limit
    user_id = user['user_id']
    return await conversation_controller.get_messages_by_conversation_uuid(conversation_uuid=conversation_uuid, skip=offset, limit=limit, user_id=user_id)


@conversations_router.delete("/{conversation_uuid}", responses=CommonErrorResponse)
async def delete_conversation(
        conversation_uuid: str,
        request: Request,
        conversation_controller: ConversationController = Depends(ControllerInitiator().get_conversation_controller),
        user: dict = Depends(get_auth_user)
        ):
    return await conversation_controller.delete_conversation(conversation_uuid)


@conversations_router.post("/{conversation_uuid}/prompt", responses=CommonErrorResponse)
async def ask_prompt(
        conversation_uuid: str,
        request: Request,
        body_params: PostPromptRequest,
        conversation_controller: ConversationController = Depends(ControllerInitiator().get_conversation_controller),
        user: dict = Depends(get_auth_user)
        ):
    prompt = body_params.prompt
    user_id = user['user_id']
    return await conversation_controller.ask_prompt(user_id, conversation_uuid, prompt)


@conversations_router.post("/prompt", responses=CommonErrorResponse)
async def create_conversation(
        request: Request,
        body_params: PostCreateConversationRequest,
        conversation_controller: ConversationController = Depends(ControllerInitiator().get_conversation_controller),
        user: dict = Depends(get_auth_user)
        ):
    prompt = body_params.prompt
    AI_application = body_params.ai_application_name
    user_id = user['user_id']
    return await conversation_controller.create_conversation(user_id, prompt, AI_application)


