import asyncio
import os
import builtins
import json
from unittest.mock import AsyncMock

import pytest

from api.shield.services.tenant_data_encryptor_service import EncryptionKeyRefresher, ShieldDataEncryptor
from api.shield.utils import config_utils
from api.shield.model.encryption_key_info import EncryptionKeyInfo
from paig_common.encryption import RSAKeyUtil, RSAKeyInfo


class TestEncryptionKeyRefresher:

    #  refreshes context with key info
    def test_refreshes_context_with_key_info(self, mocker):
        # Mock the necessary dependencies
        mocker.patch.object(EncryptionKeyRefresher, 'refresh_context_with_key_info')

        # Create an instance of EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        encryption_key_refresher = EncryptionKeyRefresher(data_encryptor)

        # Call the method being tested
        encryption_key_info = EncryptionKeyInfo({})
        encryption_key_refresher.refresh_context_with_key_info(encryption_key_info)

        # Assert that the necessary method was called
        EncryptionKeyRefresher.refresh_context_with_key_info.assert_called_with(encryption_key_info)

    #  encryption keys cache dir is not enabled
    def test_encryption_keys_cache_dir_is_not_enabled(self, mocker):
        # Mock the necessary dependencies
        mocker.patch.object(config_utils, 'get_property_value_boolean').return_value = False

        # Create an instance of EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        encryption_key_refresher = EncryptionKeyRefresher(data_encryptor)

        # Call the method being tested
        result = encryption_key_refresher.get_key_from_cache()

        # Assert that the result is an empty list
        assert result == []

    #  encryption keys cache dir is enabled but file does not exist
    def test_encryption_keys_cache_dir_is_enabled_but_file_does_not_exist(self, mocker):
        from api.shield.client.http_account_service_client import HttpAccountServiceClient

        # Mock the necessary dependencies
        mocker.patch.object(HttpAccountServiceClient, 'get_all_encryption_keys', return_value=[])
        mocker.patch.object(os.path, 'exists', return_value=False)
        mocker.patch.object(os.path, 'getsize', return_value=0)
        mocker.patch.object(config_utils, 'get_property_value_boolean', return_value=True)

        # Initialize the EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        key_refresher = EncryptionKeyRefresher(data_encryptor)

        # Call the method to test
        key_info_list = key_refresher.get_key_from_cache()

        # Assert that the returned list is empty
        assert len(key_info_list) == 0

    # encryption keys cache dir is enabled but the file is empty
    def test_get_key_from_cache(self, mocker):
        # Mock the necessary dependencies
        # mocker.patch.object(HttpAccountServiceClient, 'get_all_encryption_keys', return_value=[])
        mocker.patch.object(os.path, 'exists', return_value=True)
        mocker.patch.object(os.path, 'getsize', return_value=100)
        mocker.patch.object(builtins, 'open')
        mocker.patch.object(json, 'loads')

        # Initialize the EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        key_refresher = EncryptionKeyRefresher(data_encryptor)

        # Call the method to test
        key_refresher.get_key_from_cache()

        # Assert
        json.loads.assert_called_once()

    def test_get_key_from_cache_with_error(self, mocker):
        # Mock the necessary dependencies
        # mocker.patch.object(HttpAccountServiceClient, 'get_all_encryption_keys', return_value=[])
        mocker.patch.object(os.path, 'exists', return_value=True)
        mocker.patch.object(os.path, 'getsize', return_value=100)
        mocker.patch.object(builtins, 'open', side_effect=Exception('test exception'))
        mocker.patch.object(json, 'loads')

        # Initialize the EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        key_refresher = EncryptionKeyRefresher(data_encryptor)

        # Call the method to test
        key_refresher.get_key_from_cache()

        # Assert
        json.loads.assert_not_called()

    # test store key cache
    def test_store_key_to_cache(self, mocker):
        # Mock the necessary dependencies
        mocker.patch.object(builtins, 'open')
        mocker.patch.object(json, 'dump')

        # Initialize the EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        key_refresher = EncryptionKeyRefresher(data_encryptor)

        # Call the method to test
        key_refresher.store_key_to_cache([])

        # Assert
        json.dump.assert_called_once()

    # test refresh_context_with_key_info
    def test_refresh_context_with_key_info_keytype_plugin(self):
        # Mock the necessary dependencies
        encryption_key_info = {"id": 1, "publicKeyValue": "publicKeyValue", "privateKeyValue": "privateKeyValue",
                               "keyStatus": "keyStatus", "keyType": "MSG_PROTECT_PLUGIN", "tenantId": "tenantId"}
        encrypt_key_obj = EncryptionKeyInfo(encryption_key_info)

        # Initialize the EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        key_refresher = EncryptionKeyRefresher(data_encryptor)

        assert data_encryptor.shield_plugin_public_key_map.__len__() == 0
        assert data_encryptor.shield_server_public_key_map.__len__() == 0
        assert data_encryptor.shield_server_private_key_map.__len__() == 0
        # Call the method to test
        key_refresher.refresh_context_with_key_info(encrypt_key_obj)

        # Assert
        assert data_encryptor.shield_plugin_public_key_map.__len__() > 0
        assert data_encryptor.shield_server_public_key_map.__len__() == 0
        assert data_encryptor.shield_server_private_key_map.__len__() == 0

    def test_refresh_context_with_key_info_keytype_shield(self):
        # Mock the necessary dependencies
        encryption_key_info = {"id": 1, "publicKeyValue": "publicKeyValue", "privateKeyValue": "privateKeyValue",
                               "keyStatus": "keyStatus", "keyType": "MSG_PROTECT_SHIELD", "tenantId": "tenantId"}
        encrypt_key_obj = EncryptionKeyInfo(encryption_key_info)

        assert encrypt_key_obj.to_dict() == encryption_key_info

        # Initialize the EncryptionKeyRefresher
        data_encryptor = ShieldDataEncryptor(tenant_id="example_tenant", enable_background_key_refresh=True)
        key_refresher = EncryptionKeyRefresher(data_encryptor)

        assert data_encryptor.shield_plugin_public_key_map.__len__() == 0
        assert data_encryptor.shield_server_public_key_map.__len__() == 0
        assert data_encryptor.shield_server_private_key_map.__len__() == 0
        # Call the method to test
        key_refresher.refresh_context_with_key_info(encrypt_key_obj)

        # Assert
        assert data_encryptor.shield_plugin_public_key_map.__len__() == 0
        assert data_encryptor.shield_server_public_key_map.__len__() > 0
        assert data_encryptor.shield_server_private_key_map.__len__() > 0

    # test rsa key util generate_key_pair
    def test_generate_key_pair(self):
        # Call the method to test
        rsa_key_info = RSAKeyUtil.generate_key_pair()

        # Assert
        assert isinstance(rsa_key_info, RSAKeyInfo)
        assert rsa_key_info.private_key_encoded_str is not None
        assert rsa_key_info.public_key_encoded_str is not None
        assert rsa_key_info.__str__() is not None


@pytest.mark.asyncio
async def test_init_refresher(mocker):
    # Mocking the necessary methods
    mocker.patch.object(EncryptionKeyRefresher, 'get_key_from_cache', return_value=[
        {'id': 1, 'publicKeyValue': 'public', 'privateKeyValue': 'private', 'keyType': 'MSG_PROTECT_PLUGIN'}])
    mocker.patch.object(EncryptionKeyRefresher, 'refresh_context_with_key_info')
    mocker.patch.object(EncryptionKeyRefresher, 'download_and_refresh_key', new_callable=AsyncMock)

    # Create an instance of EncryptionKeyRefresher
    refresher = EncryptionKeyRefresher(data_encryptor=AsyncMock())
    refresher.enable_encryption_keys_cache_dir = True

    # Call the method to test
    await refresher.init_refresher()

    # Assert that the mocked methods were called
    EncryptionKeyRefresher.get_key_from_cache.assert_called_once()
    EncryptionKeyRefresher.refresh_context_with_key_info.assert_called_once()
    EncryptionKeyRefresher.download_and_refresh_key.assert_called_once()


@pytest.mark.asyncio
async def test_download_and_refresh_key_local_client(mocker):
    # Mocking the necessary methods
    # Mock the necessary dependencies
    mocker.patch.object(EncryptionKeyRefresher, 'load_self_managed_encrypt_keys', return_value=(None, None, None))
    mocker.patch.object(EncryptionKeyRefresher, 'store_key_to_cache')
    mocker.patch.object(EncryptionKeyRefresher, 'refresh_context_with_key_info')
    mocker.patch('api.shield.services.tenant_data_encryptor_service.config_utils.get_property_value_boolean',
                 return_value=False)
    mocker.patch('api.shield.services.tenant_data_encryptor_service.EncryptionKeyInfo', return_value="mocked_key_info")
    mock_account_service_client = mocker.patch(
        'api.shield.client.local_account_service_client.LocalAccountServiceClient',
        new_callable=AsyncMock, return_value=AsyncMock())
    mocker.patch.object(mock_account_service_client, 'get_all_encryption_keys',
                        return_value=[
                            {"id": 1, "publicKeyValue": "publicKeyValue", "privateKeyValue": "privateKeyValue",
                             "keyStatus": "keyStatus", "keyType": "MSG_PROTECT_PLUGIN",
                             "tenantId": "tenantId"}])

    # Create an instance of EncryptionKeyRefresher
    refresher = EncryptionKeyRefresher(data_encryptor=AsyncMock(), account_service_client=mock_account_service_client)
    refresher.enable_encryption_keys_cache_dir = True

    # Call the method to test
    await refresher.download_and_refresh_key()

    # Assert that the mocked methods were called
    EncryptionKeyRefresher.load_self_managed_encrypt_keys.assert_called_once()
    EncryptionKeyRefresher.store_key_to_cache.assert_called_once()
    EncryptionKeyRefresher.refresh_context_with_key_info.assert_called_once()

@pytest.mark.asyncio
async def test_download_and_refresh_key_http_client(mocker):
    # Mocking the necessary methods
    # Mock the necessary dependencies
    mocker.patch.object(EncryptionKeyRefresher, 'load_self_managed_encrypt_keys', return_value=(None, None, None))
    mocker.patch.object(EncryptionKeyRefresher, 'store_key_to_cache')
    mocker.patch.object(EncryptionKeyRefresher, 'refresh_context_with_key_info')
    mocker.patch('api.shield.services.tenant_data_encryptor_service.config_utils.get_property_value_boolean',
                 return_value=False)
    mocker.patch('api.shield.services.tenant_data_encryptor_service.EncryptionKeyInfo', return_value="mocked_key_info")
    mock_account_service_client = mocker.patch(
        'api.shield.client.http_account_service_client.HttpAccountServiceClient',
        new_callable=AsyncMock, return_value=AsyncMock())
    mocker.patch.object(mock_account_service_client, 'get_all_encryption_keys',
                        return_value=[
                            {"id": 1, "publicKeyValue": "publicKeyValue", "privateKeyValue": "privateKeyValue",
                             "keyStatus": "keyStatus", "keyType": "MSG_PROTECT_PLUGIN",
                             "tenantId": "tenantId"}])

    # Create an instance of EncryptionKeyRefresher
    refresher = EncryptionKeyRefresher(data_encryptor=AsyncMock(), account_service_client=mock_account_service_client)
    refresher.enable_encryption_keys_cache_dir = True

    # Call the method to test
    await refresher.download_and_refresh_key()

    # Assert that the mocked methods were called
    EncryptionKeyRefresher.load_self_managed_encrypt_keys.assert_called_once()
    EncryptionKeyRefresher.store_key_to_cache.assert_called_once()
    EncryptionKeyRefresher.refresh_context_with_key_info.assert_called_once()


@pytest.mark.asyncio
async def test_async_run():
    data_encryptor = ShieldDataEncryptor(tenant_id="test_tenant")
    refresher = EncryptionKeyRefresher(data_encryptor)
    refresher.download_and_refresh_key = AsyncMock()
    refresher.poll_interval_sec = 1  # reduce the interval for testing

    async def set_exit_event():
        await asyncio.sleep(2)
        refresher.exit_event.set()

    await asyncio.gather(refresher.async_run(), set_exit_event())
    refresher.download_and_refresh_key.assert_awaited()


@pytest.mark.asyncio
async def test_start():
    data_encryptor = ShieldDataEncryptor(tenant_id="test_tenant")
    refresher = EncryptionKeyRefresher(data_encryptor)
    refresher.start()
    await asyncio.sleep(0.1)  # Give some time for the task to start
    assert refresher.task is not None
