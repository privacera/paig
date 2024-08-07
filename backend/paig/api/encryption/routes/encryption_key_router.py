from typing import List

from fastapi import APIRouter, Depends, status, Query

from core.controllers.paginated_response import Pageable
from api.encryption.api_schemas.encryption_key import EncryptionKeyView, EncryptionKeyFilter
from api.encryption.controllers.encryption_key_controller import EncryptionKeyController
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType
from core.utils import SingletonDepends

encryption_key_router = APIRouter()

encryption_key_controller_instance: EncryptionKeyController = Depends(SingletonDepends(EncryptionKeyController, called_inside_fastapi_depends=True))


@encryption_key_router.get("", response_model=Pageable)
async def list_encryption_keys(
        encryption_key_filter: EncryptionKeyFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
) -> Pageable:
    """
    List all AI encryption keys.
    """
    return await encryption_key_controller.list_encryption_keys(encryption_key_filter, page, size, sort)


@encryption_key_router.post("/generate", response_model=EncryptionKeyView, status_code=status.HTTP_201_CREATED)
async def create_encryption_key(
        key_type: EncryptionKeyType = Query(EncryptionKeyType.MSG_PROTECT_SHIELD,
                                            description="The type of the key to create"),
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
) -> EncryptionKeyView:
    """
    Create a new AI encryption key.
    """
    return await encryption_key_controller.create_encryption_key(key_type)


@encryption_key_router.get("/{id}", response_model=EncryptionKeyView)
async def get_encryption_key(
        id: int,
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
) -> EncryptionKeyView:
    """
    Get an AI encryption key by ID.
    """
    return await encryption_key_controller.get_encryption_key_by_id(id)


@encryption_key_router.get("/public/{id}", response_model=EncryptionKeyView)
async def get_public_encryption_key_by_id(
        id: int,
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
) -> EncryptionKeyView:
    """
    Retrieve the public encryption key by its ID.
    """
    return await encryption_key_controller.get_public_encryption_key_by_id(id)


@encryption_key_router.get("/status/active", response_model=EncryptionKeyView)
async def get_active_encryption_key_by_type(
        key_type: EncryptionKeyType = Query(EncryptionKeyType.MSG_PROTECT_SHIELD,
                                            description="The type of the key to retrieve"),
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
) -> EncryptionKeyView:
    """
    Get the active encryption key.
    """
    return await encryption_key_controller.get_active_encryption_key_by_type(key_type)


@encryption_key_router.put("/disable/{id}", status_code=status.HTTP_200_OK)
async def disable_passive_encryption_key(
        id: int,
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
):
    """
    Disable an AI encryption key by ID.
    """
    return await encryption_key_controller.disable_passive_encryption_key(id)


@encryption_key_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_encryption_key(
        id: int,
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance
):
    """
    Delete an AI encryption key by ID.
    """
    return await encryption_key_controller.delete_disabled_encryption_key(id)
