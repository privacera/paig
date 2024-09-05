from api.shield.model.shield_audit import ShieldAuditViaApi
from api.shield.services.tenant_data_encryptor_service import ShieldDataEncryptor, EncryptionKeyRefresher,TenantDataEncryptorService
from paig_common.encryption import DataEncryptor, RSAKeyUtil
from api.shield.utils.custom_exceptions import ShieldException
import pytest


class TestShieldDataEncryptor:

    #  ShieldDataEncryptor can be initialized with a tenant_id and enable_background_key_refresh set to True or False
    def test_initialization_with_tenant_id_and_enable_background_key_refresh(self):
        tenant_id = "example_tenant"
        enable_background_key_refresh = True

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)

        assert shield_data_encryptor.tenant_id == tenant_id
        assert shield_data_encryptor.enable_background_key_refresh == enable_background_key_refresh

    # When enable_background_key_refresh is True, EncryptionKeyRefresher is initialized and started in a separate thread
    def test_enable_background_key_refresh_true_initialization(self, mocker):
        mocker.patch.object(EncryptionKeyRefresher, 'init_refresher', return_value=None)
        mocker.patch.object(EncryptionKeyRefresher, 'start', return_value=None)

        tenant_id = "example_tenant"
        enable_background_key_refresh = True

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)
        assert shield_data_encryptor is not None, "The shield_data_encryptor should not be None"

    # When enable_background_key_refresh is False, EncryptionKeyRefresher is not started and encryption keys are
    # downloaded only once during initialization
    def test_enable_background_key_refresh_false_initialization(self, mocker):
        mocker.patch.object(EncryptionKeyRefresher, 'init_refresher', return_value=None)
        mocker.patch.object(EncryptionKeyRefresher, 'start', return_value=None)

        tenant_id = "example_tenant"
        enable_background_key_refresh = False

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)

        EncryptionKeyRefresher.init_refresher.assert_not_called()
        EncryptionKeyRefresher.start.assert_not_called()
        assert shield_data_encryptor is not None, "The shield_data_encryptor should not be None"

    #  EncryptionKeyRefresher periodically downloads and refreshes encryption keys for the tenant
    def test_enable_background_key_refresh_true_key_refresh(self, mocker):
        mocker.patch.object(EncryptionKeyRefresher, 'init_refresher', return_value=None)
        mocker.patch.object(EncryptionKeyRefresher, 'start', return_value=None)

        tenant_id = "example_tenant"
        enable_background_key_refresh = True

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)
        assert shield_data_encryptor is not None, "The shield_data_encryptor should not be None"

    #  create_data_encryptor method creates a DataEncryptor object with the specified encryption_key_id
    def test_create_data_encryptor(self):
        tenant_id = "example_tenant"
        enable_background_key_refresh = True

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)
        shield_data_encryptor.shield_plugin_public_key_map = {
            1: "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCC6oVLSigEbFWUBbqRP2t4wTE9F+UUWFS9zek4QNxCd8gNt4vc9kgrfmLhyHMmCQDsKSbd4hmH3n8b/YnE5ZHFJDrunaTgK4PJPMdqItbhbTlboaFkzEICKjQbaMY+tEiSUnj+caWKzFqhku4sOai5wllx9VOG41Xo8VoJZat50wIDAQAB"}
        shield_data_encryptor.shield_server_public_key_map = {
            1: "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCC6oVLSigEbFWUBbqRP2t4wTE9F+UUWFS9zek4QNxCd8gNt4vc9kgrfmLhyHMmCQDsKSbd4hmH3n8b/YnE5ZHFJDrunaTgK4PJPMdqItbhbTlboaFkzEICKjQbaMY+tEiSUnj+caWKzFqhku4sOai5wllx9VOG41Xo8VoJZat50wIDAQAB"}
        shield_data_encryptor.shield_server_private_key_map = {
            1: "MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBANQ5F5pq6iY0xiMn+OXjTL0vIphTCKWNRerEzPmwlPDhvDy3fpprPsGeh8snobS67ILW7JnwY7WZQfc6tTKbjEb/rpKT2OdRYEMlt9K0WeocJEx/dc4+9I2t2tZDxeT+l2aCYSZ4mq2YY1rRstZX4RfVrs7yShrYScKEeI0Efy4pAgMBAAECgYA+1ZiTc8xX+5AeoJslFaOG8AnCJ/OLcMSeuh4mX435tBxTrdCiT9aI5TM3h0hthlq4coIjIfWjsvjBBnTXww5I/MtZuThSUuXVocLzNnskhbd4v27FllvSN3chnL7i5lgWvW0gLXKs1/zKUDndTRNq9nzm3wKktwmzHHZWEdnQMQJBANht1RHMAsjgMBw8xYz+yfpUTIloQTmggoCBIKZrV8udNSKd8OCrn1spUw3bg2h6w8BebpQ5SmsjiyXk6jzmBsMCQQD7BmSvJNuE9mIziGPXHElWDrbHrBD9f9ZcdWadnGqd6HJsN/lYkautc9a5z9zlkxRBign61UpPFv1KgQbIBaCjAkAKb4FOkl+v/99R/TwpSD/E6jumhHhgpvSj7ZX9cD+TeckOGj97FcthQeTXTjZP21uE8wix7PFBqT0UXq1MsmqxAkEAzEqvtjpwzQ0XbokZd/91T6w55NaMHULk2epR0QNzYX/DX39OVl53MXqMzjv0soG4gn4tEQ50o1k6WmAXfMHXsQJBAJNDOXyxohQep85PZQ6ezs+5TvDvP51O25hdqA/fQvdTa/vZL5qwvL75DnFk6CRuxpJEacrRpE/O/J81r2OFveg="}

        shield_data_encryptor.create_data_encryptor(encryption_key_id=1)
        assert shield_data_encryptor.data_encryptor is not None, "The shield_data_encryptor should not be None"

    #  encrypt method encrypts the given data using the DataEncryptor object
    def test_encrypt(self, mocker):
        mocker.patch.object(DataEncryptor, 'encrypt_data', return_value="encrypted_data")
        mocker.patch.object(EncryptionKeyRefresher, 'init_refresher', return_value=None)
        mocker.patch.object(EncryptionKeyRefresher, 'start', return_value=None)
        mocker.patch.object(RSAKeyUtil, 'str_to_public_key', return_value="public_key")
        mocker.patch.object(RSAKeyUtil, 'str_to_private_key', return_value="private_key")

        tenant_id = "example_tenant"
        enable_background_key_refresh = True

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)
        shield_data_encryptor.data_encryptor = DataEncryptor("public_keyss", "private_keys")

        data_to_encrypt = "Hello, World!"
        encrypted_data = shield_data_encryptor.encrypt(data_to_encrypt)

        DataEncryptor.encrypt_data.assert_called_once_with(data_to_encrypt)
        assert encrypted_data == "encrypted_data"

    #  decrypt method decrypts the given data using the DataEncryptor object
    def test_decrypt(self, mocker):
        mocker.patch.object(DataEncryptor, 'decrypt_data', return_value="decrypted_data")
        mocker.patch.object(EncryptionKeyRefresher, 'init_refresher', return_value=None)
        mocker.patch.object(EncryptionKeyRefresher, 'start', return_value=None)
        mocker.patch.object(RSAKeyUtil, 'str_to_public_key', return_value="public_key")
        mocker.patch.object(RSAKeyUtil, 'str_to_private_key', return_value="private_key")

        tenant_id = "example_tenant"
        enable_background_key_refresh = True

        shield_data_encryptor = ShieldDataEncryptor(tenant_id, enable_background_key_refresh)
        shield_data_encryptor.data_encryptor = DataEncryptor("public_keyss", "private_keys")

        data_to_decrypt = "encrypted_data"
        decrypted_data = shield_data_encryptor.decrypt(data_to_decrypt)

        DataEncryptor.decrypt_data.assert_called_once_with(data_to_decrypt)
        assert decrypted_data == "decrypted_data"

    # Decrypts all non-null values in the 'messages' list of the given 'shield_audit' object using the 'decrypt'
    # method of the 'TenantDataEncryptorService' class, and updates the corresponding values in the 'message_object'
    # dictionary.
    @pytest.mark.asyncio
    async def test_decrypts_shield_audit_non_null_values(self, mocker):
        shield_audit = ShieldAuditViaApi({
            "eventTime": "2022-01-01T12:00:00Z",
            "tenantId": "test_tenant",
            "threadId": "12345",
            "threadSequenceNumber": 1,
            "requestType": "example",
            "encryptionKeyId": "server_key_id",
            "messages": [
                {
                    "key1": "encrypted_value1"
                },
                {
                    "key2": "encrypted_value4"
                }
            ],
            "requestId": "67890",
            "userId": "example_user_id",
            "clientApplicationKey": "client_app_key",
            "applicationKey": "app_key",
            "result": "success",
            "traits": ["trait1", "trait2"],
            "clientIp": "127.0.0.1",
            "clientHostname": "localhost",
            "rangerAuditIds": [
                "cb35230e-9cca-4d9c-9b76-73a484545bb0-374",
                "cb35230e-9cca-4d9c-9b76-73a484545bb0-373",
            ],
            "rangerPolicyIds": [
                23,
                11,
            ],
            "paigPolicyIds": [
                9858,
                43,
            ]
        })

        mocker.patch.object(TenantDataEncryptorService, 'decrypt')
        tenant_data_encryptor_service = TenantDataEncryptorService()
        await tenant_data_encryptor_service.decrypt_shield_audit(shield_audit)

        assert TenantDataEncryptorService.decrypt.call_count == 2

    #  Raises a 'ShieldException' if the 'decrypt' method of the 'TenantDataEncryptorService' class raises an exception.
    @pytest.mark.asyncio
    async def test_raises_shield_exception(self, mocker):
        shield_audit = ShieldAuditViaApi({
            "eventTime": "2022-01-01T12:00:00Z",
            "tenantId": "test_tenant",
            "threadId": "12345",
            "threadSequenceNumber": 1,
            "requestType": "example",
            "encryptionKeyId": "server_key_id",
            "messages": [
                {
                    "key1": "encrypted_value1",
                    "key2": "encrypted_value2",
                    "key3": "encrypted_value3"
                },
                {
                    "key1": "encrypted_value4",
                    "key2": "encrypted_value5",
                    "key3": "encrypted_value6"
                }
            ],
            "requestId": "67890",
            "userId": "example_user_id",
            "clientApplicationKey": "client_app_key",
            "applicationKey": "app_key",
            "result": "success",
            "traits": ["trait1", "trait2"],
            "clientIp": "127.0.0.1",
            "clientHostname": "localhost",
            "rangerAuditIds": [
                "cb35230e-9cca-4d9c-9b76-73a484545bb0-374",
                "cb35230e-9cca-4d9c-9b76-73a484545bb0-373",
            ],
            "rangerPolicyIds": [
                23,
                11,
            ],
            "paigPolicyIds": [
                9858,
                43,
            ]
        })

        tenant_data_encryptor_service = TenantDataEncryptorService()
        mocker.patch.object(TenantDataEncryptorService, 'decrypt', side_effect=ShieldException)

        with pytest.raises(ShieldException):
            await tenant_data_encryptor_service.decrypt_shield_audit(shield_audit)
