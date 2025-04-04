import logging
import os
import sys
import pandas as pd
from fastapi import APIRouter, Request, Depends, Response
from app.api_schemas.user import PostUserLoginRequest, UserLoginResponse
from core.factory.controller_initiator import ControllerInitiator
from app.controllers import UserController
from app.api_schemas import CommonErrorResponse
from core.exceptions import UnauthorizedException
from core.config import load_config_file
from core.security.jwt import JWTHandler
from core.security.okta_verifier import PaigOktaVerifier
from services.user_data_service import UserDataService  

logger = logging.getLogger(__name__)
user_router = APIRouter()

Config = load_config_file()
security_conf = Config.get('security')
okta_conf = security_conf.get('okta', dict())
basic_auth_config = security_conf.get("basic_auth", dict())

okta_enabled = okta_conf.get('enabled', "false").lower() == "true"
ui_auth_enabled = basic_auth_config.get("ui_auth_enabled", "false").lower() == "true"
basic_auth_enabled = basic_auth_config.get('enabled', "false").lower() == "true"

if okta_enabled:
    paig_okta_verifier = PaigOktaVerifier(okta_conf)

jwt_handler = JWTHandler()
user_data_service = UserDataService()  # Singleton for auth


@user_router.post("/login", responses=CommonErrorResponse)
async def user_login(
    request: Request,
    response: Response,  # fixed typo from "resonse"
    body_params: PostUserLoginRequest,
    user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
) -> UserLoginResponse:
    access_token = request.headers.get("authorization", None)

    # Okta validation
    if okta_enabled and access_token is not None:
        try:
            access_token = access_token.split(" ")[1]
            await paig_okta_verifier.verify(access_token)
        except Exception as e:
            logger.error(f"Okta access token validation failed: {e}")
            raise UnauthorizedException("Invalid access token")

    # Basic Auth fallback
    elif basic_auth_enabled and ui_auth_enabled:
        user_name = body_params.user_name.strip()
        user_secret = body_params.password.strip()
        user_data_service.verify_user_credentials(user_name, user_secret)

    # User retrieval
    user_name = body_params.user_name.strip()
    user_object = await user_controller.login_user(user_name)

    response.set_cookie(
        key="session",
        value=jwt_handler.encode({
            "user_id": user_object["user_id"],
            "user_name": user_object["user_name"]
        }),
        httponly=True
    )

    return user_object


@user_router.post("/logout")
async def user_logout(request: Request, response: Response):
    response.delete_cookie("session")
    return {"message": "Logout successful"}
