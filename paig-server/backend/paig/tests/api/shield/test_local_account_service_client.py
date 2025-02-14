import pytest
from unittest.mock import AsyncMock, MagicMock


class TestLocalAccountServiceClient:
    @pytest.fixture
    def mock_encryption_key_service(self):
        from api.encryption.services.encryption_key_service import EncryptionKeyService
        return MagicMock(spec=EncryptionKeyService)

    @pytest.fixture
    def client(self, mock_encryption_key_service):
        from api.shield.client.local_account_service_client import LocalAccountServiceClient
        return LocalAccountServiceClient(mock_encryption_key_service)

    @pytest.mark.asyncio
    async def test_get_all_encryption_keys(self, client, mock_encryption_key_service):
        # Arrange
        tenant_id = "test_tenant"
        mock_key = MagicMock()
        mock_key.id = "key_id"
        mock_key.key_status = "active"
        mock_key.key_type = "type"
        mock_key.public_key = "public_key"
        mock_key.private_key = "private_key"
        mock_encryption_key_service.list_encryption_keys = AsyncMock(return_value=MagicMock(content=[mock_key]))

        # Act
        result = await client.get_all_encryption_keys(tenant_id)

        # Assert
        from api.encryption.api_schemas.encryption_key import EncryptionKeyFilter
        mock_encryption_key_service.list_encryption_keys.assert_awaited_once_with(EncryptionKeyFilter(), 0, 10, [])
        assert len(result) == 1
        assert result[0]["id"] == "key_id"
        assert result[0]["keyStatus"] == "active"
        assert result[0]["keyType"] == "type"
        assert result[0]["publicKeyValue"] == "public_key"
        assert result[0]["privateKeyValue"] == "private_key"
        assert result[0]["tenantId"] == tenant_id
