from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from api.governance.api_schemas.ai_app import AIApplicationView, AIApplicationFilter, GuardrailApplicationsAssociation
from api.governance.controllers.ai_app_controller import AIAppController
from core.utils import SingletonDepends

ai_app_router = APIRouter()

ai_app_controller_instance = Depends(SingletonDepends(AIAppController, called_inside_fastapi_depends=True))


@ai_app_router.get("", response_model=Pageable)
async def list_applications(
        application_filter: AIApplicationFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        ai_app_controller: AIAppController = ai_app_controller_instance
) -> Pageable:
    """
    List all AI applications.
    """
    return await ai_app_controller.list_ai_applications(application_filter, page, size, sort)


@ai_app_router.post("", response_model=AIApplicationView, status_code=status.HTTP_201_CREATED)
async def create_application(
        create_ai_app_request: AIApplicationView,
        ai_app_controller: AIAppController = ai_app_controller_instance
) -> AIApplicationView:
    """
    Create a new AI application.
    """
    return await ai_app_controller.create_ai_application(create_ai_app_request)


@ai_app_router.put("/guardrails")
async def update_application_guardrails(
        request: GuardrailApplicationsAssociation,
        ai_app_controller: AIAppController = ai_app_controller_instance
):
    """
    Associates or disassociates applications with a given guardrail.
    """
    return await ai_app_controller.update_guardrail_application_association(request)


@ai_app_router.get("/{id}", response_model=AIApplicationView)
async def get_application(
        id: int,
        ai_app_controller: AIAppController = ai_app_controller_instance
) -> AIApplicationView:
    """
    Get an AI application by ID.
    """
    return await ai_app_controller.get_ai_application_by_id(id)


@ai_app_router.put("/{id}", response_model=AIApplicationView)
async def update_application(
        id: int,
        update_ai_app_request: AIApplicationView,
        ai_app_controller: AIAppController = ai_app_controller_instance
) -> AIApplicationView:
    """
    Update an existing AI application by ID.
    """
    return await ai_app_controller.update_ai_application(id, update_ai_app_request)


@ai_app_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
        id: int,
        ai_app_controller: AIAppController = ai_app_controller_instance
):
    """
    Delete an AI application by ID.
    """
    return await ai_app_controller.delete_ai_application(id)