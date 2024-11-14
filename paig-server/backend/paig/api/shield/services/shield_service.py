import logging
import json

from api.shield.services.auth_service import AuthService
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.shield_audit import ShieldAuditViaApi

from api.shield.utils import config_utils
from core.utils import SingletonDepends

logger = logging.getLogger(__name__)


class ShieldService:
    """
    ShieldService provides methods to initialize tenant data encryptors, authorize requests,
    and handle audit logging for a multi-tenant environment.
    """

    def __init__(self, auth_service: AuthService = SingletonDepends(AuthService)):
        """
        Initializes the ShieldService with the given AuthService dependency.

        """
        self.auth_service = auth_service

    async def initialize_tenant(self, x_tenant_id, x_user_role, shield_server_key_id, shield_plugin_key_id,
                                application_key):
        """
        Initializes the tenant's data encryptor, application scanners, and optionally the Ranger plugin.
        """
        # Initialize data encryptor
        logger.debug(f"Initializing encryptor for tenant: {x_tenant_id}")
        await self.auth_service.tenant_data_encryptor_service.get_data_encryptor(tenant_id=x_tenant_id,
                                                                           encryption_key_id=shield_server_key_id)
        logger.debug(
            f"Shield server encryptor with id {shield_server_key_id} initialization completed successfully for tenant: "
            f"{x_tenant_id}")

        await self.auth_service.tenant_data_encryptor_service.get_data_encryptor(tenant_id=x_tenant_id,
                                                                           encryption_key_id=shield_plugin_key_id)
        logger.debug(
            f"Shield Plugin encryptor with id {shield_plugin_key_id} initialization completed successfully for tenant: "
            f"{x_tenant_id}")

        # Initialize scanners for the given application key
        if application_key:
            self.auth_service.application_manager.load_scanners(application_key=application_key)
        else:
            logger.debug(
                f"Application key is not provided in the request for tenant {x_tenant_id}"
                f". This might be probably because plugin is on older version. So skipping the scanner loading.")

        authz_client_type = config_utils.get_property_value("authz_client", "local")
        if authz_client_type == "http":
            # Initialize ranger plugin
            from api.shield.client.http_authz_service_client import HttpAuthzClient
            authz_rest_client = SingletonDepends(HttpAuthzClient)
            await authz_rest_client.post_init_authz(tenant_id=x_tenant_id, user_role=x_user_role, application_key=application_key)

            logger.info(f"Ranger plugin initialization completed for tenant: {x_tenant_id}")
        else:
            logger.info(f"Skipping Ranger plugin initialization for tenant {x_tenant_id} since shield running in local mode")

    async def authorize(self, auth_req: AuthorizeRequest):
        logger.debug(f"Processing authorization request for tenant: {auth_req.tenant_id}")

        # Process the authorization request
        auth_response = await self.auth_service.authorize(auth_req)

        logger.debug(f"Authorization response: {auth_response}")
        return auth_response

    async def authorize_vectordb(self, x_tenant_id, x_user_role, request):
        vectordb_auth_req = AuthorizeVectorDBRequest(request, x_user_role)
        vectordb_auth_res = await self.auth_service.authorize_vectordb(vectordb_auth_req, x_tenant_id)

        response = json.dumps(vectordb_auth_res.__dict__)
        logger.debug(f"Outgoing response: {response}")
        return vectordb_auth_res

    async def audit(self, request):
        stream_shield_audit = ShieldAuditViaApi(request)
        await self.auth_service.audit_stream_data(stream_shield_audit)

        return stream_shield_audit
