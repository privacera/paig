from typing import List

from fastapi import APIRouter, Depends, status, Query

from api.guardrails.api_schemas.guardrail import GuardrailFilter, GuardrailView
from api.guardrails.controllers.guardrail_controller import GuardrailController
from core.controllers.paginated_response import Pageable
from core.utils import SingletonDepends

guardrail_router = APIRouter()

gr_controller_instance = Depends(SingletonDepends(GuardrailController, called_inside_fastapi_depends=True))


@guardrail_router.get("", response_model=Pageable, response_model_exclude_none=True, response_model_exclude_unset=True)
async def list(
        filter: GuardrailFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        guardrail_controller: GuardrailController = gr_controller_instance
) -> Pageable:
    """
    List all Guardrails.
    """
    return await guardrail_controller.list(filter, page, size, sort)


@guardrail_router.post("", response_model=GuardrailView, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create(
        request: GuardrailView,
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailView:
    """
    Create a new Guardrail.
    """
    return await guardrail_controller.create(request)


@guardrail_router.get("/{id}", response_model=GuardrailView, response_model_exclude_none=True, response_model_exclude_unset=True)
async def get(
        id: int,
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailView:
    """
    Get a Guardrail by ID.
    """
    return await guardrail_controller.get_by_id(id)


@guardrail_router.get("/application/{app_key}", response_model=List[GuardrailView], response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_all_by_app_key(
        app_key: str,
        guardrail_controller: GuardrailController = gr_controller_instance
) -> List[GuardrailView]:
    """
    Get all Guardrails by app key.
    """
    return await guardrail_controller.get_all_by_app_key(app_key)


@guardrail_router.put("/{id}", response_model=GuardrailView, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update(
        id: int,
        request: GuardrailView,
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailView:
    """
    Update an existing Guardrail by ID.
    """
    return await guardrail_controller.update(id, request)


@guardrail_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        id: int,
        guardrail_controller: GuardrailController = gr_controller_instance
):
    """
    Delete an Guardrail by ID.
    """
    return await guardrail_controller.delete(id)