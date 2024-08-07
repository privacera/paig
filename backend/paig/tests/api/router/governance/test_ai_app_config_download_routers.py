from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from core.security.authentication import get_auth_user
from api.encryption.api_schemas.encryption_key import EncryptionKeyView
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyStatus, EncryptionKeyType
from api.encryption.services.encryption_key_service import EncryptionKeyService
from api.governance.api_schemas.ai_app import AIApplicationView
from api.governance.services.ai_app_service import AIAppService

governance_services_base_route = "http://localhost:9090/governance-service/api/ai"

mock_encrption_key = EncryptionKeyView(id=1, status=1, create_time="2021-01-01T00:00:00Z",
                                       update_time="2021-01-01T00:00:00Z", public_key="public_key",
                                       private_key="private_key", key_status=EncryptionKeyStatus.ACTIVE,
                                       key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)

ai_app = AIApplicationView(id=1, status=1, name="test_app1", description="test application1", vector_dbs=[],
                           application_key="app_key")


@pytest.fixture()
def mock_encryption_service():
    mock_encryption_service = AsyncMock(spec=EncryptionKeyService)
    mock_encryption_service.get_active_encryption_key_by_type.return_value = mock_encrption_key
    return mock_encryption_service


@pytest.fixture()
def mock_ai_app_service():
    mock_ai_app_service = AsyncMock(spec=AIAppService)
    mock_ai_app_service.get_ai_application_by_id.return_value = ai_app
    return mock_ai_app_service


async def test_ai_application_config_download_operation(mock_encryption_service, mock_ai_app_service):
    def get_mock_encryption_key_service():
        return mock_encryption_service

    def get_mock_ai_app_service():
        return mock_ai_app_service

    with patch("encryption.services.encryption_key_service.EncryptionKeyService", get_mock_encryption_key_service):
        with patch("api.governance.services.ai_app_service.AIAppService", get_mock_ai_app_service):
            from server import app

            def auth_user():
                return {
                    "id": 1,
                    "username": "test",
                    "roles": ["USER"]
                }

            client = TestClient(app)

            app.dependency_overrides[get_auth_user] = auth_user

            response = client.get(
                f"{governance_services_base_route}/application/1/config/json/download"
            )
            assert response.status_code == 200
            assert response.headers['content-disposition'] == f"attachment;filename=privacera-shield-test_app1-config.json"
            assert response.headers['content-type'] == 'application/json'
            assert response.content is not None
