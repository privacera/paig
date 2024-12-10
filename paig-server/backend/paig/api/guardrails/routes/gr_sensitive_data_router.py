from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataFilter, GRSensitiveDataView
from api.guardrails.controllers.gr_sensitive_data_controller import GRSensitiveDataController
from core.utils import SingletonDepends

gr_sensitive_data_router = APIRouter()

gr_sensitive_data_controller_instance = Depends(SingletonDepends(GRSensitiveDataController, called_inside_fastapi_depends=True))


@gr_sensitive_data_router.get("", response_model=Pageable)
async def list_gr_sensitive_data(
        gr_sensitive_data_filter: GRSensitiveDataFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        gr_sensitive_data_controller: GRSensitiveDataController = gr_sensitive_data_controller_instance
) -> Pageable:
    """
    List all Guardrail Sensitive Data.
    """
    return await gr_sensitive_data_controller.list_gr_sensitive_datas(gr_sensitive_data_filter, page, size, sort)


@gr_sensitive_data_router.post("", response_model=GRSensitiveDataView, status_code=status.HTTP_201_CREATED)
async def create_gr_sensitive_data(
        create_gr_sensitive_data_request: GRSensitiveDataView,
        gr_sensitive_data_controller: GRSensitiveDataController = gr_sensitive_data_controller_instance
) -> GRSensitiveDataView:
    """
    Create a new Guardrail Sensitive Data.
    """
    return await gr_sensitive_data_controller.create_gr_sensitive_data(create_gr_sensitive_data_request)


@gr_sensitive_data_router.get("/{id}", response_model=GRSensitiveDataView)
async def get_gr_sensitive_data(
        id: int,
        gr_sensitive_data_controller: GRSensitiveDataController = gr_sensitive_data_controller_instance
) -> GRSensitiveDataView:
    """
    Get Guardrail Sensitive Data by ID.
    """
    return await gr_sensitive_data_controller.get_gr_sensitive_data_by_id(id)


@gr_sensitive_data_router.put("/{id}", response_model=GRSensitiveDataView)
async def update_gr_sensitive_data(
        id: int,
        update_gr_sensitive_data_request: GRSensitiveDataView,
        gr_sensitive_data_controller: GRSensitiveDataController = gr_sensitive_data_controller_instance
) -> GRSensitiveDataView:
    """
    Update an existing Guardrail Sensitive Data by ID.
    """
    return await gr_sensitive_data_controller.update_gr_sensitive_data(id, update_gr_sensitive_data_request)


@gr_sensitive_data_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gr_sensitive_data(
        id: int,
        gr_sensitive_data_controller: GRSensitiveDataController = gr_sensitive_data_controller_instance
):
    """
    Delete an Guardrail Sensitive Data by ID.
    """
    return await gr_sensitive_data_controller.delete_gr_sensitive_data(id)