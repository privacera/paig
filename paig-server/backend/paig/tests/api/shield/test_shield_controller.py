import json
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request
from api.shield.model.authorize_response import AuthorizeResponse
from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse
from api.shield.utils.custom_exceptions import BadRequestException


def authorize_req_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return req_json


class TestShieldController:
    @pytest.fixture
    def mock_shield_service(self):
        from api.shield.services.shield_service import ShieldService
        return MagicMock(spec=ShieldService)

    @pytest.fixture
    def controller(self, mock_shield_service):
        from api.shield.controllers.shield_controller import ShieldController
        return ShieldController(mock_shield_service)

    @pytest.mark.asyncio
    async def test_init_app(self, controller, mock_shield_service):
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-tenant-id": "test_tenant", "x-user-role": "test_role"}
        mock_request.json = AsyncMock(return_value={
            "shieldServerKeyId": "test_server_key",
            "shieldPluginKeyId": "test_plugin_key",
            "applicationKey": "test_application_key"
        })
        mock_shield_service.initialize_tenant = AsyncMock()

        # Act
        response = await controller.init_app(mock_request)

        # Assert
        mock_shield_service.initialize_tenant.assert_awaited_once_with("test_tenant", "test_role", "test_server_key",
                                                                       "test_plugin_key", "test_application_key")
        assert response.status_code == 200
        assert response.body.decode() == "Initialization completed successfully for tenant test_tenant"

    @pytest.mark.asyncio
    async def test_authorize(self, controller, mock_shield_service):
        # Arrange
        mock_request = authorize_req_data()
        x_tenant_id = "test_tenant"
        x_user_role = "test_role"
        mock_auth_response = MagicMock(spec=AuthorizeResponse)
        mock_auth_response.__dict__ = {"key": "value"}
        mock_shield_service.authorize = AsyncMock(return_value=mock_auth_response)

        # Act
        response = await controller.authorize(mock_request, x_tenant_id, x_user_role)

        # Assert
        mock_shield_service.authorize.assert_awaited_once()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_authorize_vectordb(self, controller, mock_shield_service):
        # Arrange
        mock_request = {"userId": "test_user", "applicationKey": "test_key"}
        x_tenant_id = "test_tenant"
        x_user_role = "test_role"
        mock_vectordb_response = MagicMock(spec=AuthorizeVectorDBResponse)
        mock_vectordb_response.__dict__ = {"key": "value"}
        mock_shield_service.authorize_vectordb = AsyncMock(return_value=mock_vectordb_response)

        # Act
        response = await controller.authorize_vectordb(mock_request, x_tenant_id, x_user_role)

        # Assert
        mock_shield_service.authorize_vectordb.assert_awaited_once()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_audit(self, controller, mock_shield_service):
        # Arrange
        mock_request = {"key": "value"}
        mock_shield_service.audit = AsyncMock(return_value=MagicMock(tenantId="test_tenant"))

        # Act
        response = await controller.audit(mock_request)

        # Assert
        mock_shield_service.audit.assert_awaited_once()
        assert response.status_code == 200
        assert "Audited the Data Successfully for the tenant: test_tenant" in response.body.decode()

    @pytest.mark.asyncio
    async def test_init_app_with_exceptions(self, controller, mock_shield_service):
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-tenant-id": "test_tenant", "x-user-role": "test_role"}
        mock_request.json = AsyncMock(return_value={
            "applicationKey": "test_application_key"
            # shieldServerKeyId and shieldPluginKeyId are intentionally left out to trigger exceptions
        })

        # Act and Assert
        with pytest.raises(BadRequestException, match="Missing shieldServerKeyId in request"):
            await controller.init_app(mock_request)

        mock_request.json = AsyncMock(return_value={
            "shieldServerKeyId": "test_server_key",
            "applicationKey": "test_application_key"
            # shieldPluginKeyId is intentionally left out to trigger exception
        })

        with pytest.raises(BadRequestException, match="Missing shieldPluginKeyId in request"):
            await controller.init_app(mock_request)

    @pytest.mark.asyncio
    async def test_init_app_with_json_exception(self, controller, mock_shield_service):
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-tenant-id": "test_tenant", "x-user-role": "test_role"}
        mock_request.json = AsyncMock(return_value='{"shieldServerKeyId": 2 }')  # Non-JSON serializable object

        # Act and Assert
        with pytest.raises(Exception):
            await controller.init_app(mock_request)