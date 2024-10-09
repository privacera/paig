import logging

from fastapi import APIRouter, Request, Depends, Response
from app.api_schemas.user import PostUserLoginRequest, UserLoginResponse
from core.factory.controller_initiator import ControllerInitiator
from app.controllers import UserController
from app.api_schemas import CommonErrorResponse
from core.exceptions import UnauthorizedException
from core.config import load_config_file
from core.security.jwt import JWTHandler
from core.security.okta_verifier import PaigOktaVerifier
from werkzeug.security import check_password_hash
import pandas as pd
import os
import sys

logger = logging.getLogger(__name__)
user_router = APIRouter()

Config = load_config_file()
security_conf = Config['security']
okta_conf = security_conf.get('okta', dict())
okta_enabled = okta_conf.get('enabled', "false") == "true"
basic_auth_config = security_conf.get('basic_auth', dict())
basic_auth_enabled = basic_auth_config.get('enabled', "false") == "true"

user_secrets_df = pd.DataFrame()

if basic_auth_enabled:
    user_secrets_path = basic_auth_config.get('credentials_path', None)
    # Check file exists
    if not user_secrets_path:
        logger.warning("User secrets csv file path not provided")
        sys.exit("User secrets csv file path not provided")
    if not os.path.exists(user_secrets_path):
        logger.error(f"User secrets csv file not found at {user_secrets_path}")
        sys.exit(f"User secrets csv file not found at {user_secrets_path}")
    try:
        user_secrets_df = pd.read_csv(user_secrets_path)
        if user_secrets_df.empty:
            logger.error(f"User secrets csv file is empty, File Path: {user_secrets_path}")
            sys.exit(f"User secrets csv file is empty, File Path: {user_secrets_path}")
    except Exception as e:
        logger.error(f"Error while reading user secrets csv file, File Path: {user_secrets_path}, Error: {e}")
        sys.exit(f"Error while reading user secrets csv file, File Path: {user_secrets_path}, Error: {e}")


if okta_enabled:
    paig_okta_verifier = PaigOktaVerifier(okta_conf)

jwt_handler = JWTHandler()


@user_router.post("/login", responses=CommonErrorResponse)
async def user_login(
        request: Request,
        resonse: Response,
        body_params: PostUserLoginRequest,
        user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
    ) -> UserLoginResponse:
    access_token = request.headers.get("authorization", None)

    if okta_enabled and access_token is not None:
        try:
            access_token = access_token.split(" ")[1]
            await paig_okta_verifier.verify(access_token)
        except Exception as e:
            logger.error(f"Okta access token validation failed: {e}")
            raise UnauthorizedException("Invalid access token")
    elif basic_auth_enabled:
        user_name = body_params.user_name.strip()
        user_secret = body_params.password.strip()
        if user_name not in user_secrets_df['Username'].values:
            raise UnauthorizedException("Invalid user name")
        user_secret_df = user_secrets_df.loc[user_secrets_df['Username'] == user_name, 'Secrets'].values[0]
        if not check_password_hash(user_secret_df, user_secret):
            raise UnauthorizedException("Invalid user password")

    user_name = body_params.user_name.strip()
    user_object = await user_controller.login_user(user_name)
    resonse.set_cookie(
        key="session",
        value=jwt_handler.encode({"user_id": user_object['user_id'], "user_name": user_object['user_name']}),
        httponly=True
    )
    return user_object


@user_router.post("/logout")
async def user_logout(
            request: Request,
            response: Response,
        ):
    response.delete_cookie("session")
    return {"message": "Logout successful"}