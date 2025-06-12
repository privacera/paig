import json
import uuid
from unittest.mock import Mock, MagicMock, AsyncMock

import pytest

from pathlib import Path

from api.shield.enum.ShieldEnums import Guardrail
from api.shield.model.shield_audit import ShieldAudit, ShieldAuditViaApi
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.scanner_result import ScannerResult
from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse
from api.shield.scanners.AWSBedrockGuardrailScanner import AWSBedrockGuardrailScanner
from api.shield.services.auth_service import AuthService
from api.shield.utils.custom_exceptions import BadRequestException, ShieldException
from paig_common.paig_exception import DiskFullException, AuditEventQueueFullException


def authorize_req_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return AuthorizeRequest(tenant_id='test_tenant', req_data=req_json, user_role='OWNER')


def authorize_req_data_with_streamid():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request_with_stream_id.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return AuthorizeRequest(tenant_id='test_tenant', req_data=req_json, user_role='OWNER')


def authz_res_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authz_response.json"
    with open(json_file_path, 'r') as json_file:
        res_json = json.load(json_file)

    return AuthzServiceResponse(res_data=res_json)


def authz_res_data_no_masking():
    json_file_path = f"{Path(__file__).parent}/json_data/authz_response_no_masking.json"
    with open(json_file_path, 'r') as json_file:
        res_json = json.load(json_file)

    return AuthzServiceResponse(res_data=res_json)


class TestAuthService:

    #  AuthService can be initialized in cloud mode
    def test_initialize_cloud_mode(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.NLPHandler')
        mocker.patch('api.shield.services.auth_service.ApplicationManager')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        # Initialize AuthService in cloud mode
        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "cloud"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        # Initialize AuthService in cloud mode
        auth_service = self.get_auth_service()

        # Assertions
        assert auth_service._shield_run_mode == 'cloud'

    def get_auth_service(self):
        auth_service = AuthService()
        return auth_service

    #  AuthService can be initialized in self-managed mode
    def test_initialize_self_managed_mode(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthService.init_log_message_in_file')
        mocker.patch('api.shield.services.auth_service.NLPHandler')
        mocker.patch('api.shield.services.auth_service.ApplicationManager')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        # Initialize AuthService in self-managed mode
        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "self_managed"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        auth_service = self.get_auth_service()

        # Assertions
        assert auth_service._shield_run_mode == 'self_managed'

    #  AuthService can decrypt an authorize request
    @pytest.mark.asyncio
    async def test_decrypt_authorize_request(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mock_tenant_data_encryptor_service = mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mock_tenant_data_encryptor_service.decrypt_authorize_request = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_shield_audit = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_authorize_response = AsyncMock()
        mocker.patch('api.shield.services.auth_service.ApplicationManager')

        # Initialize AuthService
        auth_service = self.get_auth_service()

        # Mock the decrypt_authorize_request method
        auth_service.tenant_data_encryptor_service = mock_tenant_data_encryptor_service
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize', new_callable=AsyncMock,
                            return_value=authz_res_data_no_masking())
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name', new_callable=AsyncMock, return_value={})

        # Create a mock AuthorizeRequest object
        mock_auth_req = authorize_req_data()

        # Call the authorize method
        await auth_service.authorize(mock_auth_req)

        # Assertions
        auth_service.tenant_data_encryptor_service.decrypt_authorize_request.assert_called_once_with(mock_auth_req)

    #  AuthService can analyze messages in an authorize request
    @pytest.mark.asyncio
    async def test_analyze_messages(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mock_tenant_data_encryptor_service = mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mock_tenant_data_encryptor_service.decrypt_authorize_request = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_shield_audit = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_authorize_response = AsyncMock()

        # Initialize AuthService
        auth_service = self.get_auth_service()

        auth_service.tenant_data_encryptor_service = mock_tenant_data_encryptor_service
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize', new_callable=AsyncMock,
                            return_value=authz_res_data_no_masking())
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name', new_callable=AsyncMock, return_value={})

        # Create a mock AuthorizeRequest object
        mock_auth_req = authorize_req_data()

        # Call the authorize method
        await auth_service.authorize(mock_auth_req)

        # Assertions
        assert auth_service.application_manager.scan_messages.call_count == mock_auth_req.messages.__len__()

    def test_init_log_message_in_file(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "self_managed",
            "audit_msg_content_to_self_managed_storage": "True",
            "audit_msg_content_storage_system": "s3,local",
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.__init__', return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.__init__', return_value=None)

        # Initialize AuthService
        auth_service = self.get_auth_service()

        assert auth_service.message_log_objs.__len__() == 2

    def test_init_log_message_in_file_with_invalid_storage(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        side_effect = lambda prop, default: {
            "shield_run_mode": "self_managed",
            "audit_msg_content_to_self_managed_storage": "True",
            "audit_msg_content_storage_system": "gcp",
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.__init__')
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.__init__')

        with pytest.raises(Exception) as e:
            # Initialize AuthService
            self.get_auth_service()

        print(f"\nGot Exception=> {e.type}:{e.value}")

    @pytest.mark.asyncio
    async def test_authorize_authorize_vectordb(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        # Initialize AuthService
        auth_service = self.get_auth_service()
        authz_vectordb_res = AuthorizeVectorDBResponse({"filterExpression": "example_filter_expression"})
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize_vectordb', new_callable=AsyncMock,
                            return_value=authz_vectordb_res)

        # Call the authorize method
        vector_db_request = AuthorizeVectorDBRequest({"userId": "example_user_id", "applicationKey": "example_app_key"},
                                                     user_role='OWNER')
        await auth_service.authorize_vectordb(vector_db_request, "test_tenant")

        # Assertions
        auth_service.authz_service_client.post_authorize_vectordb.assert_called_once_with(vector_db_request,
                                                                                          "test_tenant")

    @pytest.mark.asyncio
    async def test_log_audit_message_s3_local_storage_type(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "self_managed",
            "audit_msg_content_to_self_managed_storage": "True",
            "audit_msg_content_storage_system": "s3,local",
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.__init__', return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.__init__', return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.log', new_callable=AsyncMock)
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.log', new_callable=AsyncMock)

        # Initialize AuthService
        auth_service = self.get_auth_service()
        auth_req = authorize_req_data()
        authz_res = authz_res_data()

        audit_data = ShieldAudit(auth_req, authz_res, ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])
        # Call the authorize method
        await auth_service.log_audit_message(audit_data)

        # Assertions
        assert auth_service.message_log_objs.__len__() == 2
        for message_log_obj in auth_service.message_log_objs:
            message_log_obj.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_audit_message_for_data_service_storage_type(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "self_managed",
            "audit_msg_content_to_self_managed_storage": "True",
            "audit_msg_content_storage_system": "s3,local,data-service",
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.__init__', return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.__init__', return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_data_service.LogMessageInDataService.__init__',
                     return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.log', new_callable=AsyncMock)
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.log', new_callable=AsyncMock)
        mocker.patch('api.shield.logfile.log_message_in_data_service.LogMessageInDataService.log',
                     new_callable=AsyncMock)

        # Initialize AuthService
        auth_service = self.get_auth_service()
        auth_req = authorize_req_data()
        authz_res = authz_res_data()

        audit_data = ShieldAudit(auth_req, authz_res, ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])
        # Call the authorize method
        await auth_service.log_audit_message(audit_data)

        # Assertions
        assert auth_service.message_log_objs.__len__() == 3
        for message_log_obj in auth_service.message_log_objs:
            message_log_obj.log.assert_called_once()

    # test when the authz response is not allowed
    @pytest.mark.asyncio
    async def test_not_allowed_authz_response(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mock_tenant_data_encryptor_service = mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mock_tenant_data_encryptor_service.decrypt_authorize_request = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_shield_audit = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_authorize_response = AsyncMock()
        mocker.patch('api.shield.services.auth_service.ApplicationManager')

        # Initialize AuthService
        auth_service = self.get_auth_service()
        auth_req = authorize_req_data()

        authz_res = authz_res_data()
        authz_res.__dict__['authorized'] = False
        authz_res.__dict__['status_message'] = "Access is denied"

        auth_service.tenant_data_encryptor_service = mock_tenant_data_encryptor_service
        mocker.patch.object(auth_service, 'do_authz_authorize', new_callable=AsyncMock, return_value=authz_res)
        # mocker.patch.object(auth_service, 'log_audit_fluentd')
        mocker.patch.object(auth_service, 'log_audit_message', new_callable=AsyncMock)
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name', new_callable=AsyncMock, return_value={})

        # Call the authorize method
        auth_res = await auth_service.authorize(auth_req)
        # Assertions
        assert auth_res.isAllowed == False
        assert auth_res.responseMessages[0].get('responseText') == "Access is denied"

    # test when the auth request is missing required fields
    def test_missing_required_fields_auth_request(self):
        req_data = {
            "conversationId": "06091999",
            "threadId": "1066df1e-6da6-11ee-91c2-9e05a1ebe141",
            "requestId": "55ee-91c2-9e05a1ebe154",
            "sequenceNumber": "1",
            "requestType": "prompt",
            "requestDateTime": 1703078179002,
            "clientApplicationKey": "*",
            "userId": "Gojeeta",
            "clientIp": "10.129.88.22",
            "clientHostName": "Akhileshs-MacBook-Pro.local",
            "context": {},
            "messages": ["Hello"],
            "shieldServerKeyId": 93,
            "shieldPluginKeyId": 1
        }

        with pytest.raises(BadRequestException):
            AuthorizeRequest(tenant_id='test_tenant', req_data=req_data, user_role='OWNER')

    def test_extract_data_key_missing(self):
        req_data = {}
        with pytest.raises(BadRequestException):
            ShieldAuditViaApi.extract_data(req_data, "key")

    def test_extract_data_key_value_missing(self):
        req_data = {
            "traits": []
        }
        with pytest.raises(BadRequestException):
            ShieldAuditViaApi.extract_data(req_data, "traits")

    def test_log_audit_fluentd(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)

        # Initialize AuthService
        auth_service = self.get_auth_service()

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        traits = ['TOXIC', 'PERSON', 'EMAIL_ADDRESS']
        authz_res.masked_traits = {}
        original_masked_text_list = [{"originalMessage": "Hello", "maskedMessage": "Hello"}]

        side_effect = lambda prop, default: {
            "audit_msg_content_to_paig_cloud": False,
            "audit_failure_error_enabled": True
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value_boolean', side_effect=side_effect)

        audit_data = ShieldAudit(auth_req, authz_res, traits, original_masked_text_list)
        auth_service.log_audit_fluentd(audit_data)
        mocker_logger.log.assert_called_once_with(audit_data)

    # test log_audit_fluentd when audit spool file size is full
    def test_log_audit_fluentd_disk_full_exception(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log.side_effect = DiskFullException

        # Initialize AuthService
        auth_service = self.get_auth_service()

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        traits = ['TOXIC', 'PERSON', 'EMAIL_ADDRESS']
        original_masked_text_list = [{"originalMessage": "Hello", "maskedMessage": "Hello"}]

        side_effect = lambda prop, default: {
            "audit_msg_content_to_paig_cloud": False,
            "audit_failure_error_enabled": True
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value_boolean', side_effect=side_effect)

        audit_data = ShieldAudit(auth_req, authz_res, traits, original_masked_text_list)
        with pytest.raises(ShieldException):
            auth_service.log_audit_fluentd(audit_data)

    def test_log_audit_fluentd_audit_event_queue_full_exception(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log.side_effect = AuditEventQueueFullException

        # Initialize AuthService
        auth_service = self.get_auth_service()

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        traits = ['TOXIC', 'PERSON', 'EMAIL_ADDRESS']
        original_masked_text_list = [{"originalMessage": "Hello", "maskedMessage": "Hello"}]

        side_effect = lambda prop, default: {
            "audit_msg_content_to_paig_cloud": False,
            "audit_failure_error_enabled": True
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value_boolean', side_effect=side_effect)

        audit_data = ShieldAudit(auth_req, authz_res, traits, original_masked_text_list)
        with pytest.raises(ShieldException):
            auth_service.log_audit_fluentd(audit_data)

    def test_log_audit_fluentd_exception(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log.side_effect = Exception
        # Initialize AuthService
        auth_service = self.get_auth_service()

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        traits = ['TOXIC', 'PERSON', 'EMAIL_ADDRESS']
        original_masked_text_list = [{"originalMessage": "Hello", "maskedMessage": "Hello"}]

        side_effect = lambda prop, default: {
            "audit_msg_content_to_paig_cloud": False,
            "audit_failure_error_enabled": True
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value_boolean', side_effect=side_effect)

        audit_data = ShieldAudit(auth_req, authz_res, traits, original_masked_text_list)
        with pytest.raises(ShieldException):
            auth_service.log_audit_fluentd(audit_data)

    def get_stream_shield_obj(self):
        req_obj = {
            "eventTime": "2022-01-01T12:00:00Z",
            "tenantId": "test_tenant",
            "threadId": "12345",
            "threadSequenceNumber": 1,
            "requestType": "example",
            "encryptionKeyId": "server_key_id",
            "messages": ["message1", "message2"],
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
        }
        return ShieldAuditViaApi(req_obj)

    #  Decrypts and encrypts shield audit data successfully.
    @pytest.mark.asyncio
    async def test_decrypts_and_encrypts_successfully(self, mocker):
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        # Initialize AuthService
        auth_service = self.get_auth_service()
        # Create a shield_audit object
        shield_audit = self.get_stream_shield_obj()

        # Mock the decrypt_shield_audit method of TenantDataEncryptorService
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_shield_audit', new_callable=AsyncMock)

        # Mock the encrypt_shield_audit method of TenantDataEncryptorService
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'encrypt_shield_audit', new_callable=AsyncMock)
        auth_service.log_audit_message = AsyncMock()
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log = Mock()
        side_effect = lambda prop, default: {
            "audit_msg_content_storage_system": "fluentd"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Call the audit_stream_data method
        await auth_service.audit_stream_data(shield_audit)

        # Assert that the decrypt_shield_audit method was called once
        auth_service.tenant_data_encryptor_service.decrypt_shield_audit.assert_called_once_with(shield_audit)

        # Assert that the encrypt_shield_audit method was called once with the correct arguments
        auth_service.tenant_data_encryptor_service.encrypt_shield_audit.assert_called_once_with(
            shield_audit.messages, tenant_id=shield_audit.tenantId, encryption_key_id=shield_audit.encryptionKeyId)

        mocker_logger.log.assert_called_once()

    #  Shield audit data decryption fails.
    @pytest.mark.asyncio
    async def test_decryption_fails(self, mocker):
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        # Initialize AuthService
        auth_service = self.get_auth_service()

        # Create a shield_audit object
        shield_audit = self.get_stream_shield_obj()

        # Mock the decrypt_shield_audit method of TenantDataEncryptorService to raise an exception
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_shield_audit',
                            side_effect=ShieldException, new_callable=AsyncMock)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'encrypt_shield_audit', new_callable=AsyncMock)

        with pytest.raises(ShieldException):
            await auth_service.audit_stream_data(shield_audit)

        # Assert that the decrypt_shield_audit method was called once
        auth_service.tenant_data_encryptor_service.decrypt_shield_audit.assert_awaited_once()

        # Assert that the encrypt_shield_audit method was not called
        auth_service.tenant_data_encryptor_service.encrypt_shield_audit.assert_not_awaited()

    #  Authorize request with valid input returns expected output
    @pytest.mark.asyncio
    async def test_authorize_authreq_with_stream_id(self, mocker):
        # mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')

        # Initialize AuthService
        auth_service = self.get_auth_service()

        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_authorize_request', new_callable=AsyncMock)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'encrypt_shield_audit', new_callable=AsyncMock)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'encrypt_authorize_response', new_callable=AsyncMock)
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize', new_callable=AsyncMock, return_value=authz_res_data())

        # Mock the analysis method
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name', new_callable=AsyncMock, return_value={})

        # Create a mock AuthorizeRequest object
        mock_auth_req = authorize_req_data_with_streamid()

        # Call the authorize method
        auth_response = await auth_service.authorize(mock_auth_req)

        assert auth_response is not None

    def test_get_or_create_fluentd_audit_logger(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocked_fluentd_audit_logger = mocker.patch(
            'api.shield.services.auth_service.FluentdAuditLogger')
        fluentd_audit_logger_mock = MagicMock()
        mocked_fluentd_audit_logger.return_value = fluentd_audit_logger_mock

        # Initialize AuthService
        auth_service = self.get_auth_service()

        side_effect = lambda prop, default: {
            "audit_msg_content_to_paig_cloud": False,
            "audit_failure_error_enabled": True
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value_boolean', side_effect=side_effect)
        # Act
        result = auth_service.get_or_create_fluentd_audit_logger()

        # Assert
        mocked_fluentd_audit_logger.assert_called_once()
        assert mocked_fluentd_audit_logger.daemon
        fluentd_audit_logger_mock.start.assert_called_once()
        assert result == fluentd_audit_logger_mock

    def test_from_payload_dict(self):
        payload = {
            "eventId": str(uuid.uuid4()),
            "eventTime": "2022-01-01T00:00:00Z",
            "tenantId": "tenant1",
            "threadId": "thread1",
            "threadSequenceNumber": 1,
            "requestType": "type1",
            "encryptionKeyId": "key1",
            "messages": ["message1", "message2"],
            "conversationId": "conversation1",
            "requestId": "request1",
            "userId": "user1",
            "clientApplicationKey": "clientAppKey1",
            "clientApplicationName": "clientAppName1",
            "applicationKey": "appKey1",
            "applicationName": "appName1",
            "result": "result1",
            "traits": ["trait1", "trait2"],
            "maskedTraits": {"trait1": "masked1", "trait2": "masked2"},
            "context": {"contextKey1": "contextValue1"},
            "rangerAuditIds": ["rangerAuditId1", "rangerAuditId2"],
            "rangerPolicyIds": ["rangerPolicyId1", "rangerPolicyId2"],
            "paigPolicyIds": ["paigPolicyId1", "paigPolicyId2"],
            "clientIp": "192.168.1.1",
            "clientHostname": "hostname1",
            "numberOfTokens": 2
        }

        instance = ShieldAudit.from_payload_dict(payload)

        assert instance.eventTime == payload["eventTime"]
        assert instance.tenantId == payload["tenantId"]
        assert instance.threadId == payload["threadId"]
        assert instance.threadSequenceNumber == payload["threadSequenceNumber"]
        assert instance.requestType == payload["requestType"]
        assert instance.encryptionKeyId == payload["encryptionKeyId"]
        assert instance.messages == payload["messages"]
        assert instance.conversationId == payload["conversationId"]
        assert instance.requestId == payload["requestId"]
        assert instance.userId == payload["userId"]
        assert instance.clientApplicationKey == payload["clientApplicationKey"]
        assert instance.clientApplicationName == payload["clientApplicationName"]
        assert instance.applicationKey == payload["applicationKey"]
        assert instance.applicationName == payload["applicationName"]
        assert instance.result == payload["result"]
        assert instance.traits == payload["traits"]
        assert instance.maskedTraits == payload["maskedTraits"]
        assert instance.context == payload["context"]
        assert instance.rangerAuditIds == payload["rangerAuditIds"]
        assert instance.rangerPolicyIds == payload["rangerPolicyIds"]
        assert instance.paigPolicyIds == payload["paigPolicyIds"]
        assert instance.clientIp == payload["clientIp"]
        assert instance.clientHostname == payload["clientHostname"]
        assert instance.numberOfTokens == payload["numberOfTokens"]


    @pytest.mark.asyncio
    async def test_do_guardrail_scan_blocked(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')

        auth_service = self.get_auth_service()

        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name', new_callable=AsyncMock, return_value='test_guardrail')

        guardrail_info = {"guardrail_connection_details": {}, "config_type": {"SENSITIVE_DATA": {"configs": {"PERSON": "DENY"}, "response_message": "Access Denied"}}}
        mocker.patch.object(auth_service.guardrail_service_client, 'get_guardrail_info_by_name', new_callable=AsyncMock, return_value=guardrail_info)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_guardrail_connection_details', new_callable=AsyncMock)
        mocker.patch.object(auth_service, 'analyze_scan_messages', return_value=10)
        mocker.patch.object(auth_service, 'generate_access_denied_message', return_value="Access Denied")

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        access_control_traits = {Guardrail.BLOCKED.value}
        all_result_traits = ['PERSON']
        analyzer_result_map = {}

        is_allowed, scan_timings = await auth_service.do_guardrail_scan(access_control_traits, all_result_traits, analyzer_result_map, auth_req, authz_res)

        assert is_allowed is False
        assert authz_res.authorized is False
        assert authz_res.status_message == "Access Denied"
        assert scan_timings == 10

    @pytest.mark.asyncio
    async def test_do_guardrail_scan_no_guardrail(self, mocker):
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')

        auth_service = AuthService()
        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name',
                            new_callable=AsyncMock, return_value=None)

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        access_control_traits = set()
        all_result_traits = []
        analyzer_result_map = {}

        is_allowed, scan_timings = await auth_service.do_guardrail_scan(access_control_traits, all_result_traits,
                                                                        analyzer_result_map, auth_req, authz_res)

        assert is_allowed is True
        assert scan_timings == 0

    @pytest.mark.asyncio
    async def test_do_guardrail_scan_allowed(self, mocker):
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')

        auth_service = AuthService()
        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name',
                            new_callable=AsyncMock, return_value='test_guardrail')

        guardrail_info = {"guardrail_connection_details": {}}
        mocker.patch.object(auth_service.guardrail_service_client, 'get_guardrail_info_by_name', new_callable=AsyncMock,
                            return_value=guardrail_info)

        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_guardrail_connection_details',
                            new_callable=AsyncMock)
        mocker.patch.object(auth_service, 'analyze_scan_messages', return_value=5)

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        access_control_traits = {Guardrail.ANONYMIZED.value}
        all_result_traits = ['EMAIL']
        analyzer_result_map = {}

        is_allowed, scan_timings = await auth_service.do_guardrail_scan(access_control_traits, all_result_traits,
                                                                        analyzer_result_map, auth_req, authz_res)

        assert is_allowed is True
        assert authz_res.authorized is True
        assert scan_timings == 5

    @pytest.mark.asyncio
    async def test_do_guardrail_scan_guardrail_exists_but_no_config(self, mocker):
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')

        auth_service = AuthService()
        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name',
                            new_callable=AsyncMock, return_value='test_guardrail')
        mocker.patch.object(auth_service.guardrail_service_client, 'get_guardrail_info_by_name', new_callable=AsyncMock,
                            return_value=None)

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        access_control_traits = set()
        all_result_traits = []
        analyzer_result_map = {}

        is_allowed, scan_timings = await auth_service.do_guardrail_scan(access_control_traits, all_result_traits,
                                                                        analyzer_result_map, auth_req, authz_res)

        assert is_allowed is True
        assert scan_timings == 0

    @pytest.mark.asyncio
    async def test_do_guardrail_scan_exception_handling(self, mocker):
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')

        auth_service = AuthService()
        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name',
                            new_callable=AsyncMock, side_effect=Exception("Service Failure"))

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        access_control_traits = set()
        all_result_traits = []
        analyzer_result_map = {}

        with pytest.raises(Exception) as exc_info:
            await auth_service.do_guardrail_scan(access_control_traits, all_result_traits, analyzer_result_map,
                                                 auth_req, authz_res)

        assert str(exc_info.value) == "Service Failure"

    @pytest.mark.asyncio
    async def test_do_guardrail_scan_context_update(self, mocker):
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')

        auth_service = AuthService()
        mocker.patch.object(auth_service.governance_service_client, 'get_application_guardrail_name',
                            new_callable=AsyncMock, return_value=['test_guardrail'])
        guardrail_info = {"guardrail_connection_details": {}}
        mocker.patch.object(auth_service.guardrail_service_client, 'get_guardrail_info_by_name',
                            new_callable=AsyncMock, return_value=guardrail_info)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_guardrail_connection_details',
                            new_callable=AsyncMock)
        mocker.patch.object(auth_service, 'analyze_scan_messages', return_value=None)

        auth_req = authorize_req_data()
        authz_res = authz_res_data()
        original_context = {}
        context_mock = MagicMock(wraps=original_context)
        auth_req.context = context_mock

        access_control_traits = {Guardrail.ANONYMIZED.value}
        all_result_traits = ['EMAIL']
        analyzer_result_map = {}
        await auth_service.do_guardrail_scan(access_control_traits, all_result_traits,
                                             analyzer_result_map, auth_req, authz_res)

        context_mock.update.assert_any_call({'guardrail_details': {'name': 'test_guardrail', 'policies': [], 'traits': ['EMAIL']}})
        assert auth_req.context.get("guardrail_details") == {'name': 'test_guardrail', 'policies': [], 'traits': ['EMAIL']}

    @pytest.fixture
    def scanner(self):
        return AWSBedrockGuardrailScanner(
            name='TestScanner',
            guardrail_id='guardrail_id',
            guardrail_version='guardrail_version',
            region='us-west-2'
        )

    def test_basic_anonymization_detection(self, scanner):
        message = "My email is user@example.com"
        tag_set = {'EMAIL'}
        scanner_result = ScannerResult(traits=list(tag_set))
        bedrock_response = {
            "assessments": [
                {
                    "sensitiveInformationPolicy": {
                        "regexes": [
                            {
                                "name": "Email Address",
                                "match": "user@example.com"
                            }
                        ]
                    }
                }
            ]
        }

        scanner._extract_and_process_anonymization_info(
            message, tag_set, scanner_result, bedrock_response
        )

        assert scanner_result.masked_traits == {'EMAIL': '<<EMAIL>>'}
        assert len(scanner_result.analyzer_result) == 1
        analyzer_result = scanner_result.analyzer_result[0]
        assert analyzer_result.entity_type == "EMAIL_ADDRESS"
        assert analyzer_result.start == 12
        assert analyzer_result.end == 28

    def test_multiple_detections(self, scanner):
        message = "Contact me at user@example.com or 555-1234"
        tag_set = {'EMAIL', 'PHONE'}
        scanner_result = ScannerResult(traits=list(tag_set))
        bedrock_response = {
            "assessments": [
                {
                    "sensitiveInformationPolicy": {
                        "regexes": [
                            {"name": "Email", "match": "user@example.com"},
                            {"name": "Phone", "match": "555-1234"}
                        ]
                    }
                }
            ]
        }

        scanner._extract_and_process_anonymization_info(
            message, tag_set, scanner_result, bedrock_response
        )

        assert len(scanner_result.analyzer_result) == 2
        email_result = scanner_result.analyzer_result[0]
        phone_result = scanner_result.analyzer_result[1]
        assert email_result.entity_type == "EMAIL"
        assert email_result.start == 14
        assert email_result.end == 30
        assert phone_result.entity_type == "PHONE"
        assert phone_result.start == 34
        assert phone_result.end == 42

    def test_no_sensitive_information_detected(self, scanner):
        message = "Hello World"
        tag_set = set()
        scanner_result = ScannerResult(traits=[])
        bedrock_response = {"assessments": []}

        scanner._extract_and_process_anonymization_info(
            message, tag_set, scanner_result, bedrock_response
        )

        assert scanner_result.analyzer_result == []

    def test_detected_word_not_found_in_message(self, scanner):
        message = "No sensitive info here"
        tag_set = {'SSN'}
        scanner_result = ScannerResult(traits=list(tag_set))
        bedrock_response = {
            "assessments": [
                {
                    "sensitiveInformationPolicy": {
                        "regexes": [
                            {"name": "SSN", "match": "123-45-6789"}
                        ]
                    }
                }
            ]
        }

        scanner._extract_and_process_anonymization_info(
            message, tag_set, scanner_result, bedrock_response
        )

        assert scanner_result.analyzer_result == []

    def test_partial_matches_in_message(self, scanner):
        message = "Partial match: user@example.comuser@example.com"
        tag_set = {'EMAIL'}
        scanner_result = ScannerResult(traits=list(tag_set))
        bedrock_response = {
            "assessments": [
                {
                    "sensitiveInformationPolicy": {
                        "regexes": [
                            {"name": "Email", "match": "user@example.com"}
                        ]
                    }
                }
            ]
        }

        scanner._extract_and_process_anonymization_info(
            message, tag_set, scanner_result, bedrock_response
        )

        assert len(scanner_result.analyzer_result) == 1
        first_match = scanner_result.analyzer_result[0]
        assert first_match.start == 15
        assert first_match.end == 31

    def test_no_assessments_data(self, scanner):
        message = "Test message"
        tag_set = set()
        scanner_result = ScannerResult(traits=[])
        bedrock_response = {"assessments": []}

        scanner._extract_and_process_anonymization_info(
            message, tag_set, scanner_result, bedrock_response
        )
        assert scanner_result.analyzer_result == []

    def test_encrich_context_with_guardrail_info_basic(self, mocker):
        """Test basic functionality of encrich_context_with_guardrail_info"""
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')
        
        auth_service = self.get_auth_service()
        
        # Mock the process_guardrail_response function
        mock_process_guardrail_response = mocker.patch('api.shield.services.auth_service.process_guardrail_response')
        mock_process_guardrail_response.return_value = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {
                        "PERSON": "DENY",
                        "EMAIL": "REDACT"
                    }
                },
                "CONTENT_MODERATION": {
                    "configs": {
                        "TOXIC": "DENY"
                    }
                }
            }
        }
        
        # Create test data
        guardrail_name = "test-guardrail"
        guardrail_info = {"test": "data"}
        guardrail_traits = ["PERSON", "TOXIC"]
        auth_req = authorize_req_data()
        auth_req.context = {}
        
        # Call the method
        auth_service.encrich_context_with_guardrail_info(
            guardrail_name, guardrail_info, guardrail_traits, auth_req
        )
        
        # Verify the context was updated correctly
        expected_context = {
            "guardrail_details": {
                "name": "test-guardrail",
                "policies": ["CONTENT_MODERATION", "SENSITIVE_DATA"],  # sorted set
                "traits": ["PERSON", "TOXIC"]
            }
        }
        
        assert auth_req.context == expected_context
        mock_process_guardrail_response.assert_called_once_with(guardrail_info)

    def test_encrich_context_with_guardrail_info_no_matching_traits(self, mocker):
        """Test when no traits match the guardrail configs"""
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')
        
        auth_service = self.get_auth_service()
        
        # Mock the process_guardrail_response function
        mock_process_guardrail_response = mocker.patch('api.shield.services.auth_service.process_guardrail_response')
        mock_process_guardrail_response.return_value = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {
                        "PERSON": "DENY",
                        "EMAIL": "REDACT"
                    }
                }
            }
        }
        
        # Create test data with traits that don't match
        guardrail_name = "test-guardrail"
        guardrail_info = {"test": "data"}
        guardrail_traits = ["PHONE", "CREDIT_CARD"]  # These don't match configs
        auth_req = authorize_req_data()
        auth_req.context = {}
        
        # Call the method
        auth_service.encrich_context_with_guardrail_info(
            guardrail_name, guardrail_info, guardrail_traits, auth_req
        )
        
        # Verify the context was updated with empty policies
        expected_context = {
            "guardrail_details": {
                "name": "test-guardrail",
                "policies": [],  # No matching policies
                "traits": ["PHONE", "CREDIT_CARD"]
            }
        }
        
        assert auth_req.context == expected_context

    def test_encrich_context_with_guardrail_info_empty_config_types(self, mocker):
        """Test when guardrail has no config_type"""
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')
        
        auth_service = self.get_auth_service()
        
        # Mock the process_guardrail_response function
        mock_process_guardrail_response = mocker.patch('api.shield.services.auth_service.process_guardrail_response')
        mock_process_guardrail_response.return_value = {
            "config_type": {}  # Empty config types
        }
        
        # Create test data
        guardrail_name = "test-guardrail"
        guardrail_info = {"test": "data"}
        guardrail_traits = ["PERSON", "EMAIL"]
        auth_req = authorize_req_data()
        auth_req.context = {}
        
        # Call the method
        auth_service.encrich_context_with_guardrail_info(
            guardrail_name, guardrail_info, guardrail_traits, auth_req
        )
        
        # Verify the context was updated with empty policies
        expected_context = {
            "guardrail_details": {
                "name": "test-guardrail",
                "policies": [],
                "traits": ["PERSON", "EMAIL"]
            }
        }
        
        assert auth_req.context == expected_context

    def test_encrich_context_with_guardrail_info_with_space_in_category(self, mocker):
        """Test handling of categories with spaces that need to be converted to underscores"""
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')
        
        auth_service = self.get_auth_service()
        
        # Mock the process_guardrail_response function
        mock_process_guardrail_response = mocker.patch('api.shield.services.auth_service.process_guardrail_response')
        mock_process_guardrail_response.return_value = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {
                        "Credit Card": "DENY",  # Has space
                        "Social Security": "REDACT"  # Has space
                    }
                }
            }
        }
        
        # Create test data with traits that match after space->underscore conversion
        guardrail_name = "test-guardrail"
        guardrail_info = {"test": "data"}
        guardrail_traits = ["CREDIT_CARD", "SOCIAL_SECURITY"]  # Underscore versions
        auth_req = authorize_req_data()
        auth_req.context = {}
        
        # Call the method
        auth_service.encrich_context_with_guardrail_info(
            guardrail_name, guardrail_info, guardrail_traits, auth_req
        )
        
        # Verify the context was updated correctly
        expected_context = {
            "guardrail_details": {
                "name": "test-guardrail",
                "policies": ["SENSITIVE_DATA"],
                "traits": ["CREDIT_CARD", "SOCIAL_SECURITY"]
            }
        }
        
        assert auth_req.context == expected_context

    def test_encrich_context_with_guardrail_info_deduplicates_policies(self, mocker):
        """Test that duplicate policies are removed and sorted"""
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthzServiceClientFactory')
        mocker.patch('api.shield.services.auth_service.AccountServiceFactory')
        mocker.patch('api.shield.services.auth_service.GovernanceServiceFactory')
        mocker.patch('api.shield.services.auth_service.GuardrailServiceFactory')
        
        auth_service = self.get_auth_service()
        
        # Mock the process_guardrail_response function
        mock_process_guardrail_response = mocker.patch('api.shield.services.auth_service.process_guardrail_response')
        mock_process_guardrail_response.return_value = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {
                        "PERSON": "DENY",
                        "EMAIL": "REDACT"
                    }
                },
                "CONTENT_MODERATION": {
                    "configs": {
                        "PERSON": "DENY"  # Same trait, different policy
                    }
                }
            }
        }
        
        # Create test data
        guardrail_name = "test-guardrail"
        guardrail_info = {"test": "data"}
        guardrail_traits = ["PERSON", "EMAIL"]  # PERSON matches both policies
        auth_req = authorize_req_data()
        auth_req.context = {}
        
        # Call the method
        auth_service.encrich_context_with_guardrail_info(
            guardrail_name, guardrail_info, guardrail_traits, auth_req
        )
        
        # Verify the context was updated correctly with deduped and sorted policies
        expected_context = {
            "guardrail_details": {
                "name": "test-guardrail",
                "policies": ["CONTENT_MODERATION", "SENSITIVE_DATA"],  # sorted and deduped
                "traits": ["PERSON", "EMAIL"]
            }
        }
        
        assert auth_req.context == expected_context