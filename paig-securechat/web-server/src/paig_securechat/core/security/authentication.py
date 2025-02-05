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



def get_auth_user_and_token(api_key):
    try:
        decoded_key = base64.urlsafe_b64decode(api_key).decode()
        username, api_token = decoded_key.split(":", 1)  # Extract username and token
        return username, api_token
    except Exception:
        return None, None




async def get_auth_user(
    request: Request,
    user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
):
    if constants.SINGLE_USER_MODE:
        return await user_controller.get_user_by_user_name({"user_name": constants.DEFAULT_USER_NAME})
    if hasattr(request, "headers") and "Authorization" in request.headers:
        authorization = request.headers["Authorization"]
        if "Bearer" not in authorization:
            raise UnauthorizedException("Invalid authorization")
        api_key = authorization.split("Bearer ")[1]
        user_name, api_token = get_auth_user_and_token(api_key)
        if api_token != conf["PAIG_SECURECHAT_API_TOKEN"]:
            raise UnauthorizedException("Invalid authorization")
        return await user_controller.get_user_by_user_name({"user_name": user_name})

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
