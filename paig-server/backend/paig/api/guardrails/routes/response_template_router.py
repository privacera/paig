from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from core.security.authentication import get_auth_user
from api.guardrails.api_schemas.response_template import ResponseTemplateFilter, ResponseTemplateView
from api.guardrails.controllers.response_template_controller import ResponseTemplateController
from core.utils import SingletonDepends

response_template_router = APIRouter()

response_template_controller_instance = Depends(SingletonDepends(ResponseTemplateController, called_inside_fastapi_depends=True))


@response_template_router.get("", response_model=Pageable)
async def list_response_templates(
        response_template_filter: ResponseTemplateFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        response_template_controller: ResponseTemplateController = response_template_controller_instance
) -> Pageable:
    """
    List all ResponseTemplate.
    """
    return await response_template_controller.list_response_templates(response_template_filter, page, size, sort)


@response_template_router.post("", response_model=ResponseTemplateView, status_code=status.HTTP_201_CREATED)
async def create_response_template(
        create_response_template_request: ResponseTemplateView,
        response_template_controller: ResponseTemplateController = response_template_controller_instance
) -> ResponseTemplateView:
    """
    Create a new ResponseTemplate.
    """
    return await response_template_controller.create_response_template(create_response_template_request)


@response_template_router.get("/{id}", response_model=ResponseTemplateView)
async def get_response_template(
        id: int,
        response_template_controller: ResponseTemplateController = response_template_controller_instance
) -> ResponseTemplateView:
    """
    Get ResponseTemplate by ID.
    """
    return await response_template_controller.get_response_template_by_id(id)


@response_template_router.put("/{id}", response_model=ResponseTemplateView)
async def update_response_template(
        id: int,
        update_response_template_request: ResponseTemplateView,
        response_template_controller: ResponseTemplateController = response_template_controller_instance
) -> ResponseTemplateView:
    """
    Update an existing ResponseTemplate by ID.
    """
    return await response_template_controller.update_response_template(id, update_response_template_request)


@response_template_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_response_template(
        id: int,
        response_template_controller: ResponseTemplateController = response_template_controller_instance
):
    """
    Delete an ResponseTemplate by ID.
    """
    return await response_template_controller.delete_response_template(id)