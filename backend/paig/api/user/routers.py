from fastapi import APIRouter, Request, Depends, Response, Query
from api.user.api_schemas.user_schema import CreateUserModel, UserLoginRequest, UserLoginResponse, \
    UpdateUserModel, GetUsersFilterRequest
from api.user.api_schemas.groups_schema import GroupCreateRequest, GroupUpdateRequest, GroupMemberUpdateRequest, \
    GetGroupsFilterRequest
from api.user.controllers.user_controller import UserController
from api.user.controllers.data_protect_controller import DataProtectController
from api.user.api_schemas.error_response import CommonErrorResponse
from core.controllers.paginated_response import Pageable
from core.security.jwt import JWTHandler
from core.security.authentication import get_auth_user
from api.encryption.controllers.encryption_key_controller import EncryptionKeyController
from api.user.api_schemas.data_protect_schema import DecryptListMessagesByID
from typing import List

from core.utils import SingletonDepends

user_router = APIRouter()
jwt_handler = JWTHandler()

data_protect_controller = DataProtectController()

user_controller_instance = Depends(SingletonDepends(UserController, called_inside_fastapi_depends=True))
encryption_key_controller_instance = Depends(SingletonDepends(EncryptionKeyController, called_inside_fastapi_depends=True))

@user_router.post("/api/users", response_model=dict)
async def create_user(
        request: Request,
        response: Response,
        user_params: CreateUserModel,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    user_response = await user_controller.create_user(user_params=user_params.model_dump())
    response.status_code = 201
    return user_response


@user_router.post("/api/login", responses=CommonErrorResponse)
async def user_login(
        request: Request,
        response: Response,
        body_params: UserLoginRequest,
        user_controller: UserController = user_controller_instance,
) -> UserLoginResponse:
    return await user_controller.login_user(body_params.model_dump())


@user_router.get("/api/users/tenant", response_model=dict)
async def get_tenants(
        request: Request,
        response: Response,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance,
):
    return await user_controller.get_user_tenants(user=user)


@user_router.get("/api/users/{id}", response_model=dict)
async def get_user_by_id(
        request: Request,
        response: Response,
        id: int,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance,
):
    return await user_controller.get_user_by_id(id=id)


@user_router.get("/api/users", response_model=Pageable)
async def get_all_users(
        request: Request,
        response: Response,
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        search_filters: GetUsersFilterRequest = Depends(),
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance,
):
    return await user_controller.get_users_with_groups(search_filters, page, size, sort)


@user_router.put("/api/users/{id}", response_model=dict)
async def update_user(
        request: Request,
        response: Response,
        id: int,
        body_params: UpdateUserModel,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    return await user_controller.update_user(id=id, user=user, user_params=body_params.model_dump())


@user_router.delete("/api/users/{id}", response_model=dict)
async def delete_user(
        request: Request,
        response: Response,
        id: int,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    return await user_controller.delete_user(id=id, user=user)


@user_router.get("/api/groups", response_model=Pageable)
async def get_user_groups(
        request: Request,
        user: dict = Depends(get_auth_user),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        search_filters: GetGroupsFilterRequest = Depends(),
        user_controller: UserController = user_controller_instance
):
    return await user_controller.group_controller.get_groups_with_members_count(search_filters, page, size, sort)


@user_router.post("/api/groups", response_model=dict)
async def create_user_group(
        request: Request,
        response: Response,
        body_params: GroupCreateRequest,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    updated_group = await user_controller.group_controller.create_group(body_params)
    response.status_code = 201
    return updated_group


@user_router.put("/api/groups/{group_id}", response_model=dict)
async def update_user_group(
        request: Request,
        group_id: int,
        body_params: GroupUpdateRequest,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    return await user_controller.group_controller.update_group(group_id, body_params)


@user_router.delete("/api/groups/{group_id}", response_model=dict)
async def update_user_group(
        request: Request,
        group_id: int,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    return await user_controller.group_controller.delete_group(group_id)


@user_router.put("/api/groups/{group_id}/users", response_model=dict)
async def update_group_members(
        request: Request,
        group_id: int,
        body_params: GroupMemberUpdateRequest,
        user: dict = Depends(get_auth_user),
        user_controller: UserController = user_controller_instance
):
    return await user_controller.group_controller.update_group_members(group_id, body_params)

@user_router.post("/api/data-protect/decrypt", response_model=dict)
async def decrypt_messages(
        request: Request,
        response: Response,
        body_params: DecryptListMessagesByID = DecryptListMessagesByID,
        user: dict = Depends(get_auth_user),
        encryption_key_controller: EncryptionKeyController = encryption_key_controller_instance,
):
    return await data_protect_controller.decrypt_list_messages(encryption_key_controller, body_params)

