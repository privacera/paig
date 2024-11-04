import json
import uuid
from unittest.mock import Mock, MagicMock, AsyncMock

import pytest

from pathlib import Path

from api.shield.model.shield_audit import ShieldAudit, ShieldAuditViaApi
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse
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

        # Create mock objects for the dependencies
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService in self-managed mode
        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "cloud"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        # Initialize AuthService in cloud mode
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        # Assertions
        assert auth_service._shield_run_mode == 'cloud'

    def get_auth_service(self, mock_account_service_factory, mock_authz_service_client_factory,
                         mock_data_store_controller):
        auth_service = AuthService(authz_service_client_factory=mock_authz_service_client_factory,
                                   data_store_controller=mock_data_store_controller,
                                   account_service_factory=mock_account_service_factory)
        return auth_service

    def get_required_auth_service_mock_dependencies(self, mocker):
        mock_authz_service_client_factory = mocker.Mock()
        mock_authz_service_client_factory.get_authz_service_client = mocker.Mock()
        mock_data_store_controller = mocker.Mock()
        mock_account_service_factory = mocker.Mock()
        mock_account_service_factory.get_account_service_client = mocker.Mock()
        return mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller

    #  AuthService can be initialized in self-managed mode
    def test_initialize_self_managed_mode(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocker.patch('api.shield.services.auth_service.AuthService.init_log_message_in_file')

        # Create mock objects for the dependencies
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)

        # Initialize AuthService in self-managed mode
        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "self_managed"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        # Assertions
        assert auth_service._shield_run_mode == 'self_managed'

    #  AuthService can decrypt an authorize request
    @pytest.mark.asyncio
    async def test_decrypt_authorize_request(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mock_tenant_data_encryptor_service = mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mock_tenant_data_encryptor_service.decrypt_authorize_request = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_shield_audit = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_authorize_response = AsyncMock()
        mocker.patch('api.shield.services.auth_service.ApplicationManager')

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        # Mock the decrypt_authorize_request method
        auth_service.tenant_data_encryptor_service = mock_tenant_data_encryptor_service
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize', new_callable=AsyncMock,
                            return_value=authz_res_data_no_masking())
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_aws_bedrock_guardrail_info', new_callable=AsyncMock, return_value={})

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
        mock_tenant_data_encryptor_service = mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mock_tenant_data_encryptor_service.decrypt_authorize_request = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_shield_audit = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_authorize_response = AsyncMock()

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)
        auth_service.tenant_data_encryptor_service = mock_tenant_data_encryptor_service
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize', new_callable=AsyncMock,
                            return_value=authz_res_data_no_masking())
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_aws_bedrock_guardrail_info', new_callable=AsyncMock, return_value={})

        # Create a mock AuthorizeRequest object
        mock_auth_req = authorize_req_data()

        # Call the authorize method
        await auth_service.authorize(mock_auth_req)

        # Assertions
        assert auth_service.application_manager.scan_messages.call_count == mock_auth_req.messages.__len__()*2

    def test_init_log_message_in_file(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')

        side_effect = lambda prop, default_value=None: {
            "shield_run_mode": "self_managed",
            "audit_msg_content_to_self_managed_storage": "True",
            "audit_msg_content_storage_system": "s3,local",
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.__init__', return_value=None)
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.__init__', return_value=None)

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        assert auth_service.message_log_objs.__len__() == 2

    def test_init_log_message_in_file_with_invalid_storage(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')

        side_effect = lambda prop, default: {
            "shield_run_mode": "self_managed",
            "audit_msg_content_to_self_managed_storage": "True",
            "audit_msg_content_storage_system": "gcp",
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.__init__')
        mocker.patch('api.shield.logfile.log_message_in_local.LogMessageInLocal.__init__')

        with pytest.raises(Exception) as e:
            mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
                mocker)
            # Initialize AuthService
            self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                  mock_data_store_controller)

        print(f"\nGot Exception=> {e.type}:{e.value}")

    @pytest.mark.asyncio
    async def test_authorize_authorize_vectordb(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)
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
    async def test_log_audit_message(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')

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
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)
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
        mock_tenant_data_encryptor_service = mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mock_tenant_data_encryptor_service.decrypt_authorize_request = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_shield_audit = AsyncMock()
        mock_tenant_data_encryptor_service.encrypt_authorize_response = AsyncMock()
        mocker.patch('api.shield.services.auth_service.ApplicationManager')

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)
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

        mocker.patch.object(auth_service.governance_service_client, 'get_aws_bedrock_guardrail_info', new_callable=AsyncMock, return_value={})

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
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

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
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log.side_effect = DiskFullException
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

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
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log.side_effect = AuditEventQueueFullException
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

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
        mocker_logger = Mock()
        mocker.patch('api.shield.services.auth_service.AuthService.get_or_create_fluentd_audit_logger',
                     return_value=mocker_logger)
        mocker_logger.log.side_effect = Exception
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

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
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)
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
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

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

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'decrypt_authorize_request', new_callable=AsyncMock)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'encrypt_shield_audit', new_callable=AsyncMock)
        mocker.patch.object(auth_service.tenant_data_encryptor_service, 'encrypt_authorize_response', new_callable=AsyncMock)
        mocker.patch.object(auth_service.authz_service_client, 'post_authorize', new_callable=AsyncMock, return_value=authz_res_data())

        # Mock the analysis method
        mocker.patch.object(auth_service.application_manager, 'scan_messages', return_value=({}, {}))
        mocker.patch('api.shield.services.auth_service.AuthService.audit', return_value=(0, 0))

        mocker.patch.object(auth_service.governance_service_client, 'get_aws_bedrock_guardrail_info', new_callable=AsyncMock, return_value={})

        # Create a mock AuthorizeRequest object
        mock_auth_req = authorize_req_data_with_streamid()

        # Call the authorize method
        auth_response = await auth_service.authorize(mock_auth_req)

        assert auth_response is not None

    def test_get_or_create_fluentd_audit_logger(self, mocker):
        # Mock dependencies
        mocker.patch('api.shield.services.auth_service.FluentdRestHttpClient')
        mocker.patch('api.shield.services.auth_service.TenantDataEncryptorService')
        mocked_fluentd_audit_logger = mocker.patch(
            'api.shield.services.auth_service.FluentdAuditLogger')
        fluentd_audit_logger_mock = MagicMock()
        mocked_fluentd_audit_logger.return_value = fluentd_audit_logger_mock

        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

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

    def generate_access_denied_message_default(self, mocker):
        
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        side_effect = lambda prop, default: {
            "default_access_denied_message": "Sorry, you are not allowed to ask this question.",
            "default_access_denied_message_multi_trait": "Sorry, you are not allowed to ask this question as it is against policy to discuss",
            "OFF_TOPIC-WEATHER": "off-topic (weather)",
            "OFF_TOPIC-SPORTS": "off-topic (sports)",
            "OFF_TOPIC-SHOPPING": "off-topic (shopping)",
            "OFF_TOPIC-RESTRICTEDLANGUAGE": "using unauthorized languages",
            "OFF_TOPIC-RECIPE": "off-topic (recipe)",
            "OFF_TOPIC-NONPROFESSIONAL": "off-topic (personal)",
            "OFF_TOPIC-LYRICS": "off-topic (lyrics)",
            "OFF_TOPIC-JOKE": "off-topic (jokes)",
            "OFF_TOPIC-INVESTMENT": "off-topic (investment advice)",
            "OFF_TOPIC-HISTORY": "off-topic (history)",
            "OFF_TOPIC-FASHIONADVICE": "off-topic (fashion advice)",
            "OFF_TOPIC-COMPETITIONCOMPARISION": "off-topic (competitors)",
            "MISCONDUCT": "inappropriate topics",
            "SEXUAL": "sexual topics",
            "VIOLENCE": "violent topics",
            "CRIMINAL": "criminal topics",
            "PASSWORD": "personal sensitive information"
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        
        message = auth_service.generate_access_denied_message(['PERSON'])
        
        assert message == "Sorry, you are not allowed to ask this question as it is against policy to discuss PERSON"
        
    def generate_access_denied_message_single_trait(self, mocker):
        
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)
        
        side_effect = lambda prop, default: {
            "default_access_denied_message": "Sorry, you are not allowed to ask this question.",
            "default_access_denied_message_multi_trait": "Sorry, you are not allowed to ask this question as it is against policy to discuss",
            "OFF_TOPIC-WEATHER": "off-topic (weather)",
            "OFF_TOPIC-SPORTS": "off-topic (sports)",
            "OFF_TOPIC-SHOPPING": "off-topic (shopping)",
            "OFF_TOPIC-RESTRICTEDLANGUAGE": "using unauthorized languages",
            "OFF_TOPIC-RECIPE": "off-topic (recipe)",
            "OFF_TOPIC-NONPROFESSIONAL": "off-topic (personal)",
            "OFF_TOPIC-LYRICS": "off-topic (lyrics)",
            "OFF_TOPIC-JOKE": "off-topic (jokes)",
            "OFF_TOPIC-INVESTMENT": "off-topic (investment advice)",
            "OFF_TOPIC-HISTORY": "off-topic (history)",
            "OFF_TOPIC-FASHIONADVICE": "off-topic (fashion advice)",
            "OFF_TOPIC-COMPETITIONCOMPARISION": "off-topic (competitors)",
            "MISCONDUCT": "inappropriate topics",
            "SEXUAL": "sexual topics",
            "VIOLENCE": "violent topics",
            "CRIMINAL": "criminal topics",
            "PASSWORD": "personal sensitive information"
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        
        message = auth_service.generate_access_denied_message(['MISCONDUCT'])
        
        assert message == "Sorry, you are not allowed to ask this question as it is against policy to discuss MISCONDUCT"
        
    def generate_access_denied_message_multiple_traits(self, mocker):
        
        mock_account_service_factory, mock_authz_service_client_factory, mock_data_store_controller = self.get_required_auth_service_mock_dependencies(
            mocker)
        
        # Initialize AuthService
        auth_service = self.get_auth_service(mock_account_service_factory, mock_authz_service_client_factory,
                                             mock_data_store_controller)

        side_effect = lambda prop, default: {
            "default_access_denied_message": "Sorry, you are not allowed to ask this question.",
            "default_access_denied_message_multi_trait": "Sorry, you are not allowed to ask this question as it is against policy to discuss",
            "OFF_TOPIC-WEATHER": "off-topic (weather)",
            "OFF_TOPIC-SPORTS": "off-topic (sports)",
            "OFF_TOPIC-SHOPPING": "off-topic (shopping)",
            "OFF_TOPIC-RESTRICTEDLANGUAGE": "using unauthorized languages",
            "OFF_TOPIC-RECIPE": "off-topic (recipe)",
            "OFF_TOPIC-NONPROFESSIONAL": "off-topic (personal)",
            "OFF_TOPIC-LYRICS": "off-topic (lyrics)",
            "OFF_TOPIC-JOKE": "off-topic (jokes)",
            "OFF_TOPIC-INVESTMENT": "off-topic (investment advice)",
            "OFF_TOPIC-HISTORY": "off-topic (history)",
            "OFF_TOPIC-FASHIONADVICE": "off-topic (fashion advice)",
            "OFF_TOPIC-COMPETITIONCOMPARISION": "off-topic (competitors)",
            "MISCONDUCT": "inappropriate topics",
            "SEXUAL": "sexual topics",
            "VIOLENCE": "violent topics",
            "CRIMINAL": "criminal topics",
            "PASSWORD": "personal sensitive information"
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        message = auth_service.generate_access_denied_message(['MISCONDUCT', 'OFF_TOPIC-INVESTMENT'])
        
        assert message == "Access is denied"
        
        message = auth_service.generate_access_denied_message(['MISCONDUCT', 'PERSON'])
        
        assert message == "Access is denied"