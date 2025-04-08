import base64
from fastapi import Depends, Request
from app.controllers.user import UserController
from core.factory.controller_initiator import ControllerInitiator
from core.exceptions import UnauthorizedException
from core.security.jwt import JWTHandler
from core import constants, config
from services.user_data_service import UserDataService

jwt_handler = JWTHandler()
conf = config.load_config_file()

basic_auth_enabled = conf.get("security", {}).get("basic_auth", {}).get("enabled", "false").lower() == "true"

user_details_service = UserDataService()

async def get_auth_user(
    request: Request,
    user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
):
    """Handles user authentication using Basic Auth, Bearer token, or session cookies."""

    if constants.SINGLE_USER_MODE:
        return await user_controller.get_user_by_user_name({"user_name": constants.DEFAULT_USER_NAME})

    if hasattr(request, "headers") and "Authorization" in request.headers:
        authorization = request.headers["Authorization"]

        if basic_auth_enabled and authorization.startswith("Basic "):
            return await __validate_basic_auth(authorization, user_controller)

        elif authorization.startswith("Bearer "):
            user_name = await __validate_token(authorization)
            user = await user_controller.get_user_by_user_name({"user_name": user_name})
            if user is None:
                raise UnauthorizedException("Unauthorized user")
            return user

        else:
            raise UnauthorizedException("Invalid Authorization header")

    return await __validate_session(request, user_controller)


async def __validate_basic_auth(authorization: str, user_controller: UserController):
    """Validates Basic Authentication credentials."""

    try:
        api_token = authorization.split("Basic ")[1]
        payload = base64.b64decode(api_token).decode("utf-8") 
        username, password = payload.split(":", 1)
    except (IndexError, ValueError, base64.binascii.Error):
        raise UnauthorizedException("Invalid Basic Authentication header")

    if not user_details_service.verify_user_credentials(username, password):
        raise UnauthorizedException("Invalid credentials")

    user = await user_controller.get_user_by_user_name({"user_name": username})
    if user is None:
        raise UnauthorizedException("Unauthorized user")

    return user  

async def __validate_token(authorization: str):
    """Validates Bearer token authentication."""

    api_token = authorization.split("Bearer ")[1]
    payload = jwt_handler.decode(api_token)

    if payload is None:
        raise UnauthorizedException("Invalid token")

    user_name = payload.get("username")
    if not user_name:
        raise UnauthorizedException("Invalid token")

    return user_name

async def __validate_session(request: Request, user_controller: UserController):
    """Validates session-based authentication using cookies."""

    session = request.cookies.get("session")

    if session is None:
        raise UnauthorizedException("Unauthorized session")

    session_user = jwt_handler.decode(session)
    if session_user is None:
        raise UnauthorizedException("Unauthorized session")

    user = {
        "user_id": session_user.get("user_id"),
        "user_name": session_user.get("user_name")
    }

    if not user["user_id"] or not user["user_name"]:
        raise UnauthorizedException("Unauthorized session")

    user_obj = await user_controller.get_user(user)

    if user_obj is None:
        raise UnauthorizedException("Unauthorized session")

    return user_obj
