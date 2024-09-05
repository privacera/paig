from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from api.governance.api_schemas.vector_db import VectorDBView, VectorDBFilter
from api.governance.controllers.vector_db_controller import VectorDBController
from core.utils import SingletonDepends

vector_db_router = APIRouter()

vector_db_controller_instance = Depends(SingletonDepends(VectorDBController, called_inside_fastapi_depends=True))

@vector_db_router.get("", response_model=Pageable)
async def list_vector_db(
        filters: VectorDBFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        vector_db_controller: VectorDBController = vector_db_controller_instance
) -> Pageable:
    """
    List all Vector DB.
    """
    return await vector_db_controller.list_vector_dbs(filters, page, size, sort)


@vector_db_router.post("", response_model=VectorDBView, status_code=status.HTTP_201_CREATED)
async def create_vector_db(
        create_vector_db_request: VectorDBView,
        vector_db_controller: VectorDBController = vector_db_controller_instance
) -> VectorDBView:
    """
    Create a new Vector DB.
    """
    return await vector_db_controller.create_vector_db(create_vector_db_request)


@vector_db_router.get("/{id}", response_model=VectorDBView)
async def get_vector_db(
        id: int,
        vector_db_controller: VectorDBController = vector_db_controller_instance
) -> VectorDBView:
    """
    Get an Vector DB by ID.
    """
    return await vector_db_controller.get_vector_db_by_id(id)


@vector_db_router.put("/{id}", response_model=VectorDBView)
async def update_vector_db(
        id: int,
        update_vector_db_request: VectorDBView,
        vector_db_controller: VectorDBController = vector_db_controller_instance
) -> VectorDBView:
    """
    Update an existing Vector DB by ID.
    """
    return await vector_db_controller.update_vector_db(id, update_vector_db_request)


@vector_db_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vector_db(
        id: int,
        vector_db_controller: VectorDBController = vector_db_controller_instance
):
    """
    Delete an Vector DB by ID.
    """
    return await vector_db_controller.delete_vector_db(id)
