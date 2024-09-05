from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from core.security.authentication import get_auth_user
from api.governance.api_schemas.tag import TagFilter, TagView
from api.governance.controllers.tag_controller import TagController
from core.utils import SingletonDepends

tag_router = APIRouter(dependencies=[Depends(get_auth_user)])

tag_controller_instance = Depends(SingletonDepends(TagController, called_inside_fastapi_depends=True))


@tag_router.get("", response_model=Pageable)
async def list_tags(
        tag_filter: TagFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        tag_controller: TagController = tag_controller_instance
) -> Pageable:
    """
    List all Tag.
    """
    return await tag_controller.list_tags(tag_filter, page, size, sort)


@tag_router.post("", response_model=TagView, status_code=status.HTTP_201_CREATED)
async def create_tag(
        create_tag_request: TagView,
        tag_controller: TagController = tag_controller_instance
) -> TagView:
    """
    Create a new Tag.
    """
    return await tag_controller.create_tag(create_tag_request)


@tag_router.get("/{id}", response_model=TagView)
async def get_tag(
        id: int,
        tag_controller: TagController = tag_controller_instance
) -> TagView:
    """
    Get Tag by ID.
    """
    return await tag_controller.get_tag_by_id(id)


@tag_router.put("/{id}", response_model=TagView)
async def update_tag(
        id: int,
        update_tag_request: TagView,
        tag_controller: TagController = tag_controller_instance
) -> TagView:
    """
    Update an existing Tag by ID.
    """
    return await tag_controller.update_tag(id, update_tag_request)


@tag_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
        id: int,
        tag_controller: TagController = tag_controller_instance
):
    """
    Delete an Tag by ID.
    """
    return await tag_controller.delete_tag(id)