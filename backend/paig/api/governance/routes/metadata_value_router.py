from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from core.security.authentication import get_auth_user
from api.governance.api_schemas.metadata_value import MetadataValueFilter, MetadataValueView
from api.governance.controllers.metadata_value_controller import MetadataValueController
from core.utils import SingletonDepends

metadata_value_router = APIRouter(dependencies=[Depends(get_auth_user)])

metadata_value_controller_instance = Depends(SingletonDepends(MetadataValueController, called_inside_fastapi_depends=True))

@metadata_value_router.get("", response_model=Pageable)
async def list_metadata_values(
        metadata_value_filter: MetadataValueFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        metadata_value_controller: MetadataValueController = metadata_value_controller_instance
) -> Pageable:
    """
    List all Metadata Values.
    """
    return await metadata_value_controller.list_metadata_values(metadata_value_filter, page, size, sort)


@metadata_value_router.post("", response_model=MetadataValueView, status_code=status.HTTP_201_CREATED)
async def create_metadata_value(
        create_metadata_request: MetadataValueView,
        metadata_value_controller: MetadataValueController = metadata_value_controller_instance
) -> MetadataValueView:
    """
    Create a new Metadata Values.
    """
    return await metadata_value_controller.create_metadata_value(create_metadata_request)


@metadata_value_router.get("/{id}", response_model=MetadataValueView)
async def get_metadata_value(
        id: int,
        metadata_value_controller: MetadataValueController = metadata_value_controller_instance
) -> MetadataValueView:
    """
    Get Metadata Values by ID.
    """
    return await metadata_value_controller.get_metadata_value_by_id(id)


@metadata_value_router.put("/{id}", response_model=MetadataValueView)
async def update_metadata_value(
        id: int,
        update_metadata_request: MetadataValueView,
        metadata_value_controller: MetadataValueController = metadata_value_controller_instance
) -> MetadataValueView:
    """
    Update an existing Metadata Values by ID.
    """
    return await metadata_value_controller.update_metadata_value(id, update_metadata_request)


@metadata_value_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metadata_value(
        id: int,
        metadata_value_controller: MetadataValueController = metadata_value_controller_instance
):
    """
    Delete an Metadata Values by ID.
    """
    return await metadata_value_controller.delete_metadata_value(id)