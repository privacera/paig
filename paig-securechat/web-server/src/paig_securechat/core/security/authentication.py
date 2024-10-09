from app.controllers.user import UserController
from core.factory.controller_initiator import ControllerInitiator
from core.exceptions import UnauthorizedException
from fastapi import Depends, Request
from core.security.jwt import JWTHandler
from core import constants
jwt_handler = JWTHandler()


async def get_auth_user(
    request: Request,
    user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
):
    if constants.SINGLE_USER_MODE:
        return await user_controller.get_user_by_user_name({"user_name": constants.DEFAULT_USER_NAME})
    cookies = request.cookies
    session = cookies.get("session")
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
