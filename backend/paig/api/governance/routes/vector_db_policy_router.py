from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from api.governance.api_schemas.vector_db_policy import VectorDBPolicyFilter, VectorDBPolicyView
from api.governance.controllers.vector_db_policy_controller import VectorDBPolicyController
from core.utils import SingletonDepends

vector_db_policy_router = APIRouter()

vector_db_policy_controller_instance = Depends(SingletonDepends(VectorDBPolicyController, called_inside_fastapi_depends=True))

@vector_db_policy_router.get("", response_model=Pageable)
async def list_vector_db_policy(
        vector_db_id: int,
        vector_db_policy_filter: VectorDBPolicyFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        vector_db_policy_controller: VectorDBPolicyController = vector_db_policy_controller_instance
) -> Pageable:
    """
    List all Vector DB policies.
    """
    vector_db_policy_filter.vector_db_id = vector_db_id
    return await vector_db_policy_controller.list_vector_db_policies(vector_db_policy_filter, page, size, sort)


@vector_db_policy_router.post("", response_model=VectorDBPolicyView, status_code=status.HTTP_201_CREATED)
async def create_vector_db_policy(
        vector_db_id: int,
        create_vector_db_request: VectorDBPolicyView,
        vector_db_policy_controller: VectorDBPolicyController = vector_db_policy_controller_instance
) -> VectorDBPolicyView:
    """
    Create a new Vector DB policies.
    """
    return await vector_db_policy_controller.create_vector_db_policies(vector_db_id, create_vector_db_request)


@vector_db_policy_router.get("/{id}", response_model=VectorDBPolicyView)
async def get_vector_db_policy(
        vector_db_id: int,
        id: int,
        vector_db_policy_controller: VectorDBPolicyController = vector_db_policy_controller_instance
) -> VectorDBPolicyView:
    """
    Get a Vector DB policy by ID.
    """
    return await vector_db_policy_controller.get_vector_db_policy_by_id(vector_db_id, id)


@vector_db_policy_router.put("/{id}", response_model=VectorDBPolicyView)
async def update_vector_db_policy(
        vector_db_id: int,
        id: int,
        update_vector_db_request: VectorDBPolicyView,
        vector_db_policy_controller: VectorDBPolicyController = vector_db_policy_controller_instance
) -> VectorDBPolicyView:
    """
    Update an existing Vector DB policy by ID.
    """
    return await vector_db_policy_controller.update_vector_db_policy(vector_db_id, id, update_vector_db_request)


@vector_db_policy_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vector_db_policy(
        vector_db_id: int,
        id: int,
        vector_db_policy_controller: VectorDBPolicyController = vector_db_policy_controller_instance
):
    """
    Delete a Vector DB policy by ID.
    """
    return await vector_db_policy_controller.delete_vector_db_policy(vector_db_id, id)
