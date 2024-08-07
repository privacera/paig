import logging

from fastapi import responses
from api.user.controllers.group_controller import GroupController
from core.exceptions import UnauthorizedException
from core.exceptions import InternalServerError, NotFoundException
from core.security.jwt import JWTHandler
from core.utils import verify_password, SingletonDepends

from api.user.services.user_service import UserService
from api.user.services.group_service import GroupService

logger = logging.getLogger(__name__)
jwt_handler = JWTHandler()


class UserController:
    def __init__(
            self,
            user_service: UserService = SingletonDepends(UserService),
            group_service: GroupService = SingletonDepends(GroupService)
    ):
        self.user_service = user_service
        self.group_service = group_service
        self.group_controller = GroupController(
            user_service,
            group_service
        )

    async def login_user(self, login_params):
        username = login_params["username"]
        password = login_params["password"]
        if not username or not password:
            raise InternalServerError("Invalid user credentials")
        user = await self.user_service.get_user(username=username)
        if user is None:
            raise UnauthorizedException("Invalid user credentials")
        # only allow owners to login
        if not user.is_tenant_owner:
            raise UnauthorizedException("Unauthorized to perform this action")
        if verify_password(password, user.password):
            response = responses.RedirectResponse(url="/", status_code=303)
            response.set_cookie(
                key="PRIVACERAPAIGSESSION",
                value=jwt_handler.encode({"id": user.id, "username": user.username}),
                httponly=True
            )
            return response
        raise UnauthorizedException("Invalid user credentials")

    async def create_user(self, user_params):
        return await self.user_service.create_user(user_params)

    async def get_user_tenants(self, user: dict):
        return await self.user_service.get_user_tenants(user)

    async def get_user_info(self, username: [str, None] = None, id: [int, None] = None):
        return await self.user_service.get_user_info(username=username, id=id)

    async def get_user_by_id(self, id: int):
        user_info = await self.get_user_info(username=None, id=id)
        if user_info is None:
            raise NotFoundException("User not found")
        return user_info.to_ui_dict()

    async def get_all_users(self):
        return await self.user_service.get_all_users()

    async def update_user(self, id: int, user: dict, user_params: dict):
        return await self.user_service.update_user(id, user, user_params)

    async def delete_user(self, id: int, user: dict):
        return await self.user_service.delete_user(id, user)

    async def get_users_with_groups(self, search_filters, page, size, sort):
        return await self.user_service.get_users_with_groups(search_filters, page, size, sort)
