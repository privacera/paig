import logging
import base64
import pandas as pd
from werkzeug.security import check_password_hash
from fastapi import Depends, Request
from app.controllers.user import UserController
from core.factory.controller_initiator import ControllerInitiator
from core.exceptions import UnauthorizedException
from core.security.jwt import JWTHandler
from core import constants, config

logger = logging.getLogger(__name__)
jwt_handler = JWTHandler()
conf = config.load_config_file()

async def get_auth_user(
    request: Request,
    user_controller: UserController = Depends(ControllerInitiator().get_user_controller),
):
    if constants.SINGLE_USER_MODE:
        logging.info("Single user mode enabled")
        return await user_controller.get_user_by_user_name({"user_name": constants.DEFAULT_USER_NAME})
    
    if hasattr(request, "headers") and "Authorization" in request.headers:
        authorization = request.headers["Authorization"]
        
        if authorization.startswith("Basic "):
            return await __validate_basic_auth(authorization)
        
        elif authorization.startswith("Bearer "):
            user_name = await __validate_token(authorization)
            user = await user_controller.get_user_by_user_name({"user_name": user_name})
            if user is None:
                raise UnauthorizedException("Unauthorized user")
            return user

    logging.info("No valid authorization found, checking session")
    return await __validate_session(request, user_controller)


async def __validate_basic_auth(authorization):
    """Validate Basic Authentication using credentials stored in USER_SECRETS_DF."""

    logger.info("Validating Basic Authentication...")

    # Step 1: Check if Basic Auth is enabled in config
    if not conf.get("security", {}).get("basic_auth", {}).get("enabled", False):
        logger.warning("Basic authentication is disabled")
        raise UnauthorizedException("Basic authentication is disabled")

    try:
        # Step 2: Extract and decode credentials
        api_token = authorization.split("Basic ")[1] 
        payload = base64.b64decode(api_token).decode("utf-8")  # "username:password"
        username, password = payload.split(":", 1)

        logger.info(f"Extracted Basic Auth credentials: Username={username}")

    except (IndexError, ValueError, base64.binascii.Error):
        logger.error("Invalid Basic Authentication header format")
        raise UnauthorizedException("Invalid Basic Authentication header")

    # Step 3: Validate Against `constants.USER_SECRETS_DF`
    df: pd.DataFrame = constants.USER_SECRETS_DF

    # Check if DataFrame is empty or not loaded
    if df is None or df.empty:
        logger.error("User secrets DataFrame is empty or not loaded")
        raise UnauthorizedException("User authentication data not available")

    # Ensure column names match the CSV format
    if "Username" not in df.columns or "Secrets" not in df.columns:
        logger.error("Missing required columns in USER_SECRETS_DF (Expected: 'Username', 'Secrets')")
        raise UnauthorizedException("User authentication data format error")

    # Find user record
    user_record = df[df["Username"] == username]

    if user_record.empty:
        logger.warning(f"User '{username}' not found in credentials")
        raise UnauthorizedException("Invalid username or password")

    stored_hashed_password = user_record.iloc[0]["Secrets"]

    # Step 4: Check if Password Matches
    if not check_password_hash(stored_hashed_password, password):
        logger.warning(f"Invalid password for user: {username}")
        raise UnauthorizedException("Invalid username or password")

    logger.info(f"Basic Authentication successful for user: {username}")
    return username

async def __validate_token(authorization):
    """Validate JWT Token Authentication."""
    
    logger.info("Validating JWT Token...")
    
    api_token = authorization.split("Bearer ")[1]
    payload = jwt_handler.decode(api_token)

    if payload is None:
        logger.error("JWT decoding failed. Invalid token.")
        raise UnauthorizedException("Invalid token")

    user_name = payload.get("username")
    if not user_name:
        logger.error("JWT payload missing 'username' field.")
        raise UnauthorizedException("Invalid token")

    logger.info(f"Token validated. User: {user_name}")
    return user_name

async def __validate_session(request, user_controller):
    """Validate session-based authentication using cookies."""
    
    session = request.cookies.get("session")

    if session is None:
        logger.error("Session cookie not found.")
        raise UnauthorizedException("Unauthorized session")

    logger.info(f"Extracted session token: {session}")

    session_user = jwt_handler.decode(session)
    if session_user is None:
        logger.error("Session token decoding failed.")
        raise UnauthorizedException("Unauthorized session")

    logger.info(f"Decoded session user: {session_user}")

    user = {
        "user_id": session_user.get("user_id"),
        "user_name": session_user.get("user_name")
    }

    if not user["user_id"] or not user["user_name"]:
        logger.error("Session payload missing user_id or user_name.")
        raise UnauthorizedException("Unauthorized session")

    user_obj = await user_controller.get_user(user)
    if user_obj is None:
        logger.error(f"User '{user['user_name']}' not found in database.")
        raise UnauthorizedException("Unauthorized session")

    logger.info(f"Authenticated session user: {user['user_name']}")
    return user_obj
