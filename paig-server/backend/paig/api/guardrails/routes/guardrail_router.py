from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query

from api.guardrails.api_schemas.guardrail import GuardrailFilter, GuardrailView, GuardrailsDataView, \
    GRVersionHistoryFilter
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

    Args:
        filter (GuardrailFilter): The filter object containing the search parameters.
        page (int): The page number to retrieve.
        size (int): The number of records to retrieve per page.
        sort (List[str]): The sorting parameters to apply.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        Pageable: The paginated response containing the list of Guardrails.
    """
    return await guardrail_controller.list(filter, page, size, sort)


@guardrail_router.get("/history", response_model=Pageable, response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_all_history(
        filter: GRVersionHistoryFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        guardrail_controller: GuardrailController = gr_controller_instance
) -> Pageable:
    """
    Get the history of all Guardrails.

    Args:
        filter (GRVersionHistoryFilter): The filter object containing the search parameters.
        page (int): The page number to retrieve.
        size (int): The number of records to retrieve per page.
        sort (List[str]): The sorting parameters to apply.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        Pageable: The paginated response containing the list of Guardrail history.
    """
    return await guardrail_controller.get_history(filter=filter, page_number=page, size=size, sort=sort)


@guardrail_router.get("/{id}/history", response_model=Pageable, response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_history(
        id: int,
        filter: GRVersionHistoryFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        guardrail_controller: GuardrailController = gr_controller_instance
) -> Pageable:
    """
    Get the history of a Guardrail by ID.

    Args:
        id (int): The ID of the Guardrail to retrieve history.
        filter (GRVersionHistoryFilter): The filter object containing the search parameters.
        page (int): The page number to retrieve.
        size (int): The number of records to retrieve per page.
        sort (List[str]): The sorting parameters to apply.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        Pageable: The paginated response containing the list of Guardrail history.
    """
    return await guardrail_controller.get_history(id, filter, page, size, sort)


@guardrail_router.post("", response_model=GuardrailView, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create(
        request: GuardrailView,
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailView:
    """
    Create a new Guardrail.

    Args:
        request (GuardrailView): The view object representing the Guardrail to create.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        GuardrailView: The created Guardrail view object.
    """
    return await guardrail_controller.create(request)


@guardrail_router.get("/{id}", response_model=GuardrailView, response_model_exclude_none=True, response_model_exclude_unset=True)
async def get(
        id: int,
        extended: Optional[bool] = Query(False, description="Include extended information"),
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailView:
    """
    Get a Guardrail by ID.

    Args:
        id (int): The ID of the Guardrail to retrieve.
        extended (Optional[bool]): Include extended information of guardrail connection details and guardrail provider response.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        GuardrailView: The Guardrail view object corresponding to the ID.
    """
    return await guardrail_controller.get_by_id(id, extended)


@guardrail_router.get("/application/{app_key}", response_model=GuardrailsDataView, response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_all_by_app_key(
        app_key: str,
        last_known_version: Optional[int] = Query(None, alias="lastKnownVersion"),
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailsDataView:
    """
    Get all Guardrails by app key and lastKnownVersion.

    Args:
        app_key (str): The application key to filter by.
        last_known_version (Optional[int]): The last known version to filter by.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        GuardrailsDataView: The Guardrails data view object containing app_key, version and list of guardrails.
    """
    return await guardrail_controller.get_all_by_app_key(app_key, last_known_version)


@guardrail_router.put("/{id}", response_model=GuardrailView, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update(
        id: int,
        request: GuardrailView,
        guardrail_controller: GuardrailController = gr_controller_instance
) -> GuardrailView:
    """
    Update an existing Guardrail by ID.

    Args:
        id (int): The ID of the Guardrail to update.
        request (GuardrailView): The updated view object representing the Guardrail.
        guardrail_controller (GuardrailController): The guardrail controller

    Returns:
        GuardrailView: The updated Guardrail view object.
    """
    return await guardrail_controller.update(id, request)


@guardrail_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        id: int,
        guardrail_controller: GuardrailController = gr_controller_instance
):
    """
    Delete an Guardrail by ID.

    Args:
        id (int): The ID of the Guardrail to delete.
        guardrail_controller (GuardrailController): The guardrail controller
    """
    await guardrail_controller.delete(id)
