from typing import List, Dict, Any

from fastapi import APIRouter, Depends, status, Query

from api.guardrails.api_schemas.gr_connection import GRConnectionFilter, GRConnectionView
from api.guardrails.controllers.gr_connection_controller import GRConnectionController
from core.controllers.paginated_response import Pageable
from core.utils import SingletonDepends

gr_connection_router = APIRouter()

gr_connection_controller_instance = Depends(SingletonDepends(GRConnectionController, called_inside_fastapi_depends=True))


@gr_connection_router.get("", response_model=Pageable)
async def list(
        filter: GRConnectionFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
) -> Pageable:
    """
    List all Guardrail Connections.
    """
    return await gr_connection_controller.list(filter, page, size, sort)


@gr_connection_router.get("_providers", response_model=List[str])
async def list_connection_provider_names(
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
) -> List[str]:
    """
    List all Guardrail Connection Providers.
    """
    return await gr_connection_controller.list_connection_provider_names()


@gr_connection_router.post("", response_model=GRConnectionView, status_code=status.HTTP_201_CREATED)
async def create(
        request: GRConnectionView,
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
) -> GRConnectionView:
    """
    Create a new Guardrail Connection.
    """
    return await gr_connection_controller.create(request)


@gr_connection_router.get("/{id}", response_model=GRConnectionView)
async def get(
        id: int,
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
) -> GRConnectionView:
    """
    Get a Guardrail Connection by ID.
    """
    return await gr_connection_controller.get_by_id(id)


@gr_connection_router.put("/{id}", response_model=GRConnectionView)
async def update(
        id: int,
        request: GRConnectionView,
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
) -> GRConnectionView:
    """
    Update an existing Guardrail Connection by ID.
    """
    return await gr_connection_controller.update(id, request)


@gr_connection_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        id: int,
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
):
    """
    Delete a Guardrail Connection by ID.
    """
    return await gr_connection_controller.delete(id)


@gr_connection_router.post("_test", response_model=Dict[str, Any])
async def test_connection(
        request: GRConnectionView,
        gr_connection_controller: GRConnectionController = gr_connection_controller_instance
) -> Dict[str, Any]:
    """
    Test the connection to the Guardrail provider.
    """
    return await gr_connection_controller.test_connection(request)