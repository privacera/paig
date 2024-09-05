from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView, AIApplicationPolicyFilter
from api.governance.controllers.ai_app_policy_controller import AIAppPolicyController
from core.utils import SingletonDepends

ai_app_policy_router = APIRouter()

ai_app_policy_controller_instance = Depends(SingletonDepends(AIAppPolicyController, called_inside_fastapi_depends=True))


@ai_app_policy_router.get("", response_model=Pageable)
async def list_application_policies(
        app_id: int,
        application_policy_filter: AIApplicationPolicyFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        ai_app_policy_controller: AIAppPolicyController = ai_app_policy_controller_instance
) -> Pageable:
    """
    List all AI applications.
    """
    application_policy_filter.application_id = app_id
    return await ai_app_policy_controller.list_ai_application_policies(application_policy_filter, page, size, sort)


@ai_app_policy_router.get("/{id}", response_model=AIApplicationPolicyView)
async def get_application_policy(
        app_id: int,
        id: int,
        ai_app_policy_controller: AIAppPolicyController = ai_app_policy_controller_instance
) -> AIApplicationPolicyView:
    """
    Get an AI application policy by ID.
    """
    return await ai_app_policy_controller.get_ai_application_policy_by_id(app_id, id)


@ai_app_policy_router.post("")
async def create_application_policy(
        app_id: int,
        create_ai_app_policy_request: AIApplicationPolicyView,
        ai_app_policy_controller: AIAppPolicyController = ai_app_policy_controller_instance
) -> AIApplicationPolicyView:
    """
    Create a new AI application policy.
    """
    return await ai_app_policy_controller.create_ai_application_policy(app_id, create_ai_app_policy_request)


@ai_app_policy_router.put("/{id}", response_model=AIApplicationPolicyView)
async def update_application_policy(
        app_id: int,
        id: int,
        update_ai_app_policy_request: AIApplicationPolicyView,
        ai_app_policy_controller: AIAppPolicyController = ai_app_policy_controller_instance
) -> AIApplicationPolicyView:
    """
    Update an existing AI application policy by ID.
    """
    return await ai_app_policy_controller.update_ai_application_policy(app_id, id, update_ai_app_policy_request)


@ai_app_policy_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_policy(
        app_id: int,
        id: int,
        ai_app_policy_controller: AIAppPolicyController = ai_app_policy_controller_instance
):
    """
    Delete an AI application policy by ID.
    """
    return await ai_app_policy_controller.delete_ai_application_policy(app_id, id)
