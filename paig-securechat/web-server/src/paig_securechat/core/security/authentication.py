from app.controllers.user import UserController
from core.factory.controller_initiator import ControllerInitiator
from core.exceptions import UnauthorizedException
from fastapi import Depends, Request
from core.security.jwt import JWTHandler
from core import constants
from core import config
import base64

jwt_handler = JWTHandler()
conf = config.load_config_file()

async def get_auth_user(
    request: Request,
    user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
):
    if constants.SINGLE_USER_MODE:
        return await user_controller.get_user_by_user_name({"user_name": constants.DEFAULT_USER_NAME})

    if hasattr(request, "headers") and "Authorization" in request.headers:
        user_name = await __validate_token(request)
        user = await user_controller.get_user_by_user_name({"user_name": user_name})
        if user is None:
            raise UnauthorizedException("Unauthorized user")
        return user

    return await __validate_session(request, user_controller)

async def __validate_token(request):
    authorization = request.headers["Authorization"]
    if "Bearer" not in authorization:
        raise UnauthorizedException("Invalid token")
    api_token = authorization.split("Bearer ")[1]
    payload = jwt_handler.decode(api_token)
    user_name = payload.get("username")
    return user_name

async def __validate_session(request, user_controller):
    session = request.cookies.get("session")
    if session is None:
        raise UnauthorizedException("Unauthorized session")
    session_user = jwt_handler.decode(session)
    if session_user is None:
        raise UnauthorizedException("Unauthorized session")
    user = {
        "user_id": session_user['user_id'],
        "user_name": session_user['user_name']
    }
    user_obj = await user_controller.get_user(user)
    if user_obj is None:
        raise UnauthorizedException("Unauthorized session")
    return user_obj
