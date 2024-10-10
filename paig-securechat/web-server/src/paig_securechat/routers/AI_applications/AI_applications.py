from typing import Annotated

from fastapi import APIRouter, Request, Depends
from core.exceptions import InternalServerError
from app.controllers.AI_applications import AIApplicationController
from core.factory.controller_initiator import ControllerInitiator
from app.api_schemas import CommonErrorResponse
from core.security.authentication import get_auth_user
AI_applications_router = APIRouter()


@AI_applications_router.get("", response_model=dict, responses=CommonErrorResponse)
def get_all_AI_applications(
        request: Request,
        AI_application_controller: AIApplicationController = Depends(ControllerInitiator().get_AI_application_controller),
        user: dict = Depends(get_auth_user)
        ):
    AI_applications = AI_application_controller.get_all_AI_applications()
    if not AI_applications:
        raise InternalServerError("Error occurred while fetching AI_applications")
    return AI_applications
