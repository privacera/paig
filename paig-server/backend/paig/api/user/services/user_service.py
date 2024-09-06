import logging

from api.user.database.db_operations.groups_repository import GroupRepository
from api.user.database.db_operations.user_repository import UserRepository
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil

from core.exceptions import ConflictException, UnauthorizedException
from core.exceptions import NotFoundException
from core.utils import get_password_hash, SingletonDepends
from core.config import load_config_file
import api.user.constants as users_constants
from core.constants import DEFAULT_TENANT_ID
from core.controllers.paginated_response import create_pageable_response

logger = logging.getLogger(__name__)
config = load_config_file()


def _create_user_model_dict(user_params):
    user_params['is_tenant_owner'] = True if user_params.get('roles')[0] == users_constants.OWNER_ROLE else False
    return user_params


def _update_user_model_dict(user_info, user_params):
    user_params["password"] = user_params.get("password", user_info.password)
    user_params["is_tenant_owner"] = True if user_params.get('roles')[0] == users_constants.OWNER_ROLE else False
    return user_params


def _format_password(roles, secret):
    if secret:
        return get_password_hash(secret)
    else:
        if roles[0] and roles[0] == users_constants.OWNER_ROLE:
            security_config = config.get("security")
            default_secret = security_config.get("basic_auth").get("secret")
            return default_secret


class UserService:

    def __init__(
            self,
            user_repository: UserRepository = SingletonDepends(UserRepository),
            group_repository: GroupRepository = SingletonDepends(GroupRepository),
            gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil)
    ):

        self.user_repository = user_repository
        self.group_repository = group_repository
        self.gov_service_validation_util = gov_service_validation_util

    async def get_user(self, username=None):
        return await self.user_repository.get_user(username=username)

    async def create_user(self, user_params):
        user = await self.user_repository.get_user_by_field(field="username", value=user_params.get("username"))
        if user:
            raise ConflictException(f"User with username {user_params['username']} already exists")

        email = user_params.get("email")
        if email:
            email = email.strip()
            user = await self.user_repository.get_user_by_field(field="email", value=email)
            if user:
                raise ConflictException(f"User with email {email} already exists")

        user_params['password'] = _format_password(roles=user_params['roles'], secret=user_params['password'])
        user_model_params = _create_user_model_dict(user_params)
        groups = user_model_params.pop('groups', [])
        group_model = None
        if groups and len(groups) > 0:
            group_model = await self.group_repository.get_groups_by_in_list('name', groups)
        user = await self.user_repository.create_user(user_model_params, group_model)
        return user.to_ui_dict()

    async def get_user_tenants(self, user: dict):
        user_info = await self.get_user_info(username=user['username'], id=user['id'])
        if user_info is None:
            raise NotFoundException("No user information found for the user")
        resp = user_info.to_ui_dict()
        resp['tenantUserId'] = resp['id']
        tenants_list = list()
        tenant_dict = resp.copy()
        tenant_dict['tenantId'] = resp['id']
        tenants_list.append(tenant_dict)
        resp['tenants'] = tenants_list
        return resp

    async def get_user_info(self, username: [str, None] = None, id: [int, None] = None):
        return await self.user_repository.get_user(username=username, id=id)

    async def get_all_users(self):
        return await self.user_repository.get_all_users()

    async def update_user(self, id: int, user: dict, user_params: dict):
        # Allow owners to update or user himself today is information
        if not(user['roles'][0] == users_constants.OWNER_ROLE or user['id'] == id):
            raise UnauthorizedException("Unauthorized to perform this action")
        user_model = await self.user_repository.get_user_with_related_data(user_id=id)
        if user_model is None:
            raise NotFoundException("User not found")

        email = user_params.get('email')
        if email:
            email = email.strip()
            user = await self.user_repository.get_user_by_field(field="email", value=email)
            if user and user.id != id:
                raise ConflictException(f"User with email {email} already exists")

        user_params['password'] = _format_password(roles=user_params['roles'], secret=user_params['password'])
        user_new_params = _update_user_model_dict(user_model, user_params)
        new_groups = user_new_params.pop('groups', [])
        target_groups = await self.group_repository.get_groups_by_in_list('name', new_groups)
        user_model.groups = target_groups
        updated_user = await self.user_repository.update_user(user_new_params, user_model)
        return updated_user.to_ui_dict()

    async def delete_user(self, id: int, user: dict):
        # Only allow owners to delete and user/owner cant delete himself
        if user['roles'][0] == users_constants.OWNER_ROLE and user['id'] != id:
            user_info = await self.get_user_info(id=id)
            if user_info is None:
                raise NotFoundException("User not found")

            # Validate if users is part of app config, app policy or vector db policy
            await self.gov_service_validation_util.validate_entity_is_not_utilized(user_info.username, "User")
            await self.user_repository.delete_user(user_info)
            return user_info.to_ui_dict()
        raise UnauthorizedException("Unauthorized to perform this action")

    async def get_users_with_groups(self, search_filters, page, size, sort):
        users, total_count = await self.user_repository.get_users_with_groups(search_filters, page, size, sort)
        if users is None:
            raise NotFoundException("No users found")
        users_list = list()
        for user in users:
            groups = [group.name for group in user.groups]
            user_dict = user.to_ui_dict()
            user_dict['tenantId'] = DEFAULT_TENANT_ID
            user_dict['userInvited'] = True
            user_dict['groups'] = groups
            users_list.append(user_dict)
        return create_pageable_response(users_list, total_count, page, size, sort)