from typing import List, Optional, Union
from fastapi import APIRouter, Depends, status, Request, Response
from core.controllers.paginated_response import Pageable
from api.apikey.api_schemas.paig_api_key import GenerateApiKeyRequest, GenerateApiKeyResponse
from api.apikey.controllers.paig_api_key_controller import PaigApiKeyController
from core.utils import SingletonDepends
from core.security.authentication import get_auth_user
from fastapi import Query



paig_api_key_router = APIRouter()

paig_api_key_controller_instance: PaigApiKeyController = Depends(SingletonDepends(PaigApiKeyController, called_inside_fastapi_depends=True))


@paig_api_key_router.post("/v2/generate", response_model=GenerateApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_api_key(
        paig_api_key_request: GenerateApiKeyRequest,
        user: dict = Depends(get_auth_user),
        paig_api_key_controller: PaigApiKeyController = paig_api_key_controller_instance
):
    """
    Generate a new API key.
    """
    return await paig_api_key_controller.create_api_key(paig_api_key_request.model_dump(), user.get("id"))


@paig_api_key_router.get("/keys", response_model=List[GenerateApiKeyResponse], status_code=status.HTTP_200_OK)
async def get_api_keys(
        apiKeyIds: List[int] = Query(...),
        user: dict = Depends(get_auth_user),
        paig_api_key_controller: PaigApiKeyController = paig_api_key_controller_instance

):
    """
    Get all API keys.
    """
    return await paig_api_key_controller.get_api_key_by_ids(apiKeyIds)


@paig_api_key_router.get("/application/getKeys", response_model=Pageable, status_code=status.HTTP_200_OK)
async def get_api_keys_by_application_id(
        request: Request,
        response: Response,
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(15, description="The number of items per page"),
        sort: Union[str, List[str]] = Query("tokenExpiry,DESC", description="The sort options"),
        key_status: Union[str, List[str]] = Query("ACTIVE,DISABLED,EXPIRED", description="The key status", alias="keyStatus"),
        api_key_name: Optional[str] = Query(None, description="Search by API key name", alias="apiKeyName"),
        description: Optional[str] = Query(None, description="Search by API key description"),
        exact_match: Optional[bool] = Query(None, description="Exact match for API key name and description", alias="exactMatch"),
        user: dict = Depends(get_auth_user),
        paig_api_key_controller: PaigApiKeyController = paig_api_key_controller_instance
):
    """
    Get all API keys by application ID.
    """
    # get application id from request hearder
    application_id = request.headers.get("x-app-id")
    return await paig_api_key_controller.get_api_keys_by_application_id_with_filters(application_id, api_key_name, description, page, size, sort, key_status, exact_match)


@paig_api_key_router.put("/disableKey/{api_key_id}", response_model=GenerateApiKeyResponse, status_code=status.HTTP_200_OK)
async def disable_api_key(
        api_key_id: int,
        user: dict = Depends(get_auth_user),
        paig_api_key_controller: PaigApiKeyController = paig_api_key_controller_instance
):
    """
    Disable an API key.
    """
    return await paig_api_key_controller.disable_api_key(api_key_id)


@paig_api_key_router.delete("/{api_key_id}", status_code=status.HTTP_200_OK)
async def delete_api_key(
        api_key_id: int,
        user: dict = Depends(get_auth_user),
        paig_api_key_controller: PaigApiKeyController = paig_api_key_controller_instance
):
    """
    Delete an API key.
    """
    return await paig_api_key_controller.permanent_delete_api_key(api_key_id)
