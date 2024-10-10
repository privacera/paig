from fastapi import APIRouter, Request, Depends
from app.api_schemas import InternalErrorResponse
from core.config import load_config_file
from app.controllers.health_check import HealthController
from core.factory.controller_initiator import ControllerInitiator
import logging
from core import constants
logger = logging.getLogger(__name__)
server_router = APIRouter()

Config = load_config_file()
security_conf = Config['security']


@server_router.get("/config", responses=InternalErrorResponse)
async def get_server_configs(
        request: Request,
        ) -> dict:
    try:
        server_config = dict()
        basic_auth_conf = security_conf.get('basic_auth', dict())
        resp_basic_auth_config = dict()
        resp_basic_auth_config['enabled'] = basic_auth_conf.get('enabled', "false") == "true"
        server_config['basic_auth'] = resp_basic_auth_config
        okta_conf = security_conf.get('okta', dict())
        resp_okta_config = dict()
        resp_okta_config['enabled'] = okta_conf.get('enabled', "false") == "true"
        resp_okta_config['client_id'] = okta_conf.get('client_id', "")
        resp_okta_config['audience'] = okta_conf.get('audience', "")
        resp_okta_config['issuer'] = okta_conf.get('issuer', "")
        server_config['okta'] = resp_okta_config
        server_config['single_user_mode'] = constants.SINGLE_USER_MODE
        server_config['default_user'] = constants.DEFAULT_USER_NAME
    except Exception as e:
        logger.error(f"Error in get_server_configs: {e}")
        raise InternalErrorResponse(detail=str(e))
    return server_config


@server_router.get("/health", responses=InternalErrorResponse)
async def get_server_health(
        request: Request,
        health_controller: HealthController = Depends(ControllerInitiator().get_health_controller)
        ) -> dict:
    try:
        return await health_controller.get_health_check()
    except Exception as e:
        logger.error(f"Error in get_server_health: {e}")
        raise InternalErrorResponse(detail=str(e))
