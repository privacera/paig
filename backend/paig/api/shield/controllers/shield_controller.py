from api.shield.services.shield_service import ShieldService
from fastapi import Request, Response
from api.shield.utils.custom_exceptions import BadRequestException
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.utils import json_utils
import json
import logging

from core.utils import SingletonDepends

logger = logging.getLogger(__name__)


class ShieldController:
    """
    ShieldController handles the API endpoints for initializing the application,
    authorizing requests, authorizing VectorDB requests, and auditing data.
    """
    def __init__(self, shield_service: ShieldService = SingletonDepends(ShieldService)):
        """
        Initializes the ShieldController with a ShieldService dependency.

        Args:
            shield_service (ShieldService): The service used for handling shield operations.
        """
        self.shield_service = shield_service

    async def init_app(self, request: Request):
        """
        Initializes the application for a specific tenant and user role.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A response indicating successful initialization.

        Raises:
            BadRequestException: If required keys are missing from the request payload.
        """
        x_tenant_id = request.headers.get("x-tenant-id")
        x_user_role = request.headers.get("x-user-role")

        req_obj = await request.json()
        try:
            shield_server_key_id = req_obj.get("shieldServerKeyId")
        except Exception as ex:
            logger.debug(f"Exception while fetching shield server key id from request: {str(ex)}. "
                         f"This maybe due to payload format from plugin. Now re-trying...")
            req_obj = json.loads(req_obj)
            shield_server_key_id = req_obj.get("shieldServerKeyId")

        if not shield_server_key_id:
            raise BadRequestException("Missing shieldServerKeyId in request")

        shield_plugin_key_id = req_obj.get("shieldPluginKeyId")
        if not shield_plugin_key_id:
            raise BadRequestException("Missing shieldPluginKeyId in request")

        application_key = req_obj.get("applicationKey")

        await self.shield_service.initialize_tenant(x_tenant_id, x_user_role, shield_server_key_id,
                                                    shield_plugin_key_id,
                                                    application_key)

        return Response(content=f"Initialization completed successfully for tenant {x_tenant_id}",
                        media_type="text/plain")

    async def authorize(self, request, x_tenant_id, x_user_role):
        """
        Authorizes a request for a specific tenant and user role.

        Args:
            request (Request): The incoming HTTP request.
            x_tenant_id (str): The tenant ID.
            x_user_role (str): The user role.

        Returns:
            Response: A JSON response containing the authorization result.
        """
        logger.debug(f"Authorization started for tenant: {x_tenant_id}")
        masked_req_obj = json_utils.mask_json_fields(json.dumps(request), ['messages'])
        logger.debug(f"Incoming request: {masked_req_obj}")

        auth_request = AuthorizeRequest(request, x_tenant_id, x_user_role)
        auth_response = await self.shield_service.authorize(auth_req=auth_request)

        response = json.dumps(auth_response.__dict__)
        masked_res_obj = json_utils.mask_json_fields(response, ['responseText'])
        logger.debug(f"Outgoing response: {masked_res_obj}")

        return Response(content=response, media_type="application/json")

    async def authorize_vectordb(self, request, x_tenant_id, x_user_role):
        """
        Authorizes a VectorDB request for a specific tenant and user role.

        Args:
            request (Request): The incoming HTTP request.
            x_tenant_id (str): The tenant ID.
            x_user_role (str): The user role.

        Returns:
            Response: A JSON response containing the VectorDB authorization result.
        """
        masked_req_obj = json_utils.mask_json_fields(json.dumps(request), ['messages'])
        logger.debug(f"Incoming request {masked_req_obj}")
        vectordb_auth_res = await self.shield_service.authorize_vectordb(x_tenant_id, x_user_role, request)
        response = json.dumps(vectordb_auth_res.__dict__)
        return Response(content=response, media_type="application/json")

    async def audit(self, request):
        """
        Audits a request and logs the data.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A JSON response indicating the success of the audit operation.
        """
        masked_req_obj = json_utils.mask_json_fields(json.dumps(request), ['messages'])
        logger.debug(f"Incoming request: {masked_req_obj}")

        audit_response = await self.shield_service.audit(request)
        response_data = {
            "message": f"Audited the Data Successfully for the tenant: {audit_response.tenantId}",
            "status": 200,
        }
        return Response(content=json.dumps(response_data), media_type="application/json")
