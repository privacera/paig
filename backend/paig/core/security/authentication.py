from api.user.controllers.user_controller import UserController
from core.exceptions import UnauthorizedException
from fastapi import Depends, Request
from core.security.jwt import JWTHandler
from core import constants
from core.utils import SingletonDepends

jwt_handler = JWTHandler()

user_controller_instance = Depends(SingletonDepends(UserController, called_inside_fastapi_depends=True))

async def get_auth_user(
    request: Request,
    user_controller: UserController = user_controller_instance,
):
    token_user_info = await get_auth_token_user_info(request)
    user_obj = await user_controller.get_user_info(**token_user_info)
    if user_obj is None:
        raise UnauthorizedException("Unauthorized session")
    return {
        "id": user_obj.id,
        "username": user_obj.username,
        "roles": ["OWNER"] if user_obj.is_tenant_owner else ["USER"],
        "email": user_obj.email
    }

async def get_auth_token_user_info(request: Request):
    if constants.SINGLE_USER_MODE:
        return {
            "id": constants.DEFAULT_USER_ID,
            "username": constants.DEFAULT_USER_NAME
        }
    cookies = request.cookies
    session = cookies.get("PRIVACERAPAIGSESSION")
    if session is None:
        raise UnauthorizedException("Unauthorized session")
    session_user = jwt_handler.decode(session)
    if session_user is None:
        raise UnauthorizedException("Unauthorized session")
    user = {
        "id": session_user['id'],
        "username": session_user['username']
    }
    return user
