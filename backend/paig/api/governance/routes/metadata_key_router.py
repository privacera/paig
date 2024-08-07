from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from core.security.authentication import get_auth_user
from api.governance.api_schemas.metadata_key import MetadataKeyView, MetadataKeyFilter
from api.governance.controllers.metadata_key_controller import MetadataKeyController
from core.utils import SingletonDepends

metadata_key_router = APIRouter(dependencies=[Depends(get_auth_user)])

metadata_controller_instance = Depends(SingletonDepends(MetadataKeyController, called_inside_fastapi_depends=True))

@metadata_key_router.get("", response_model=Pageable)
async def list_metadata(
        metadata_filter: MetadataKeyFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        metadata_controller: MetadataKeyController = metadata_controller_instance
) -> Pageable:
    """
    List all MetaData.
    """
    return await metadata_controller.list_metadata(metadata_filter, page, size, sort)


@metadata_key_router.post("", response_model=MetadataKeyView, status_code=status.HTTP_201_CREATED)
async def create_metadata(
        create_metadata_request: MetadataKeyView,
        metadata_controller: MetadataKeyController = metadata_controller_instance
) -> MetadataKeyView:
    """
    Create a new MetaData.
    """
    return await metadata_controller.create_metadata(create_metadata_request)


@metadata_key_router.get("/{id}", response_model=MetadataKeyView)
async def get_metadata(
        id: int,
        metadata_controller: MetadataKeyController = metadata_controller_instance
) -> MetadataKeyView:
    """
    Get MetaData by ID.
    """
    return await metadata_controller.get_metadata_by_id(id)


@metadata_key_router.put("/{id}", response_model=MetadataKeyView)
async def update_metadata(
        id: int,
        update_metadata_request: MetadataKeyView,
        metadata_controller: MetadataKeyController = metadata_controller_instance
) -> MetadataKeyView:
    """
    Update an existing MetaData by ID.
    """
    return await metadata_controller.update_metadata(id, update_metadata_request)


@metadata_key_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metadata(
        id: int,
        metadata_controller: MetadataKeyController = metadata_controller_instance
):
    """
    Delete an MetaData by ID.
    """
    return await metadata_controller.delete_metadata(id)