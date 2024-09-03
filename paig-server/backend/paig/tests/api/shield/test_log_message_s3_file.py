import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.shield_audit import ShieldAudit
from api.shield.logfile.log_message_in_s3 import LogMessageInS3File
from api.shield.utils.custom_exceptions import ShieldException
from paig_common.paig_exception import AuditEventQueueFullException, DiskFullException


class TestLogMessageInS3File:

    #  logs are uploaded successfully to S3
    def test_logs_uploaded_successfully_to_s3(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": 1601002345000,
            "applicationKey": "app_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1",
            "clientHostName": "localhost"
        }

        res_data = {
            "authorized": 'true',
            "enforce": 'true',
            "requestId": "55ee-91c2-9e05a1ebe151",
            "requestDateTime": "1970-01-01T00:02:03.455+00:00",
            "userId": "jai.patel",
            "applicationName": "saitama",
            "maskedTraits": {
                "PERSON": "<<PERSON>>",
                "LOCATION": "<<LOCATION>>"
            },
            "statusCode": 0,
            "statusMessage": "Access is allowed",
            "rangerAuditIds": ["d5821c40-1ead-4907-94d3-bb6337b746d3-3"],
            "rangerPolicyIds": [11],
            "paigPolicyIds": [3]
        }

        # Create a ShieldAudit object
        mock_audit = ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                                 ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])

        # Call the log method
        log_message.write_log_to_s3("object_key", mock_audit)

        # Assert that the put_object method of the s3_client is called with the correct arguments
        log_message.s3_client.put_object.assert_called_once_with(
            Body=json.dumps(mock_audit.__dict__),
            Bucket=log_message.bucket_name,
            Key=mocker.ANY
        )

    #  s3_connection_mode is set to default
    def test_s3_connection_mode_default(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        # Assert that the init_s3_client method is called with the correct arguments
        assert log_message.s3_client is not None
        assert log_message.bucket_name == "your_bucket_name"

    #  s3_connection_mode is set to keys
    def test_s3_connection_mode_keys(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "keys",
            "s3_access_key": "your_access_key",
            "s3_secret_key": "your_secret_key",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        # Assert that the init_s3_client method is called with the correct arguments
        assert log_message.s3_client is not None
        assert log_message.bucket_name == "your_bucket_name"

    #  s3_connection_mode is set to iam_role
    def test_s3_connection_mode_iam_role(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        mocker.patch('boto3.Session')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "iam_role",
            "s3_assume_role_arn": "your_assume_role_arn",
            "s3_bucket_name": "your_bucket_name",
            "boto3_log_level": "INFO"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        # Assert that the init_s3_client method is called with the correct arguments
        assert log_message.s3_client is not None
        assert log_message.bucket_name == "your_bucket_name"

    #  s3_connection_mode is set to iam_role but no arn provided
    def test_s3_iam_role_not_provided(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        mocker.patch('boto3.Session')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "iam_role",
            "s3_bucket_name": "your_bucket_name",
            "boto3_log_level": "INFO"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        # Create an instance of LogMessageInS3File
        with pytest.raises(ShieldException):
            LogMessageInS3File()

    #  s3_bucket_name is provided
    def test_s3_bucket_name_provided(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "keys",
            "s3_access_key": "your_access_key",
            "s3_secret_key": "your_secret_key",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        # Assert that the init_s3_client method is called with the correct arguments
        assert log_message.bucket_name == "your_bucket_name"

    #  s3_bucket_name is provided with prefix
    def test_s3_bucket_name_provided_with_prefix(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "keys",
            "s3_access_key": "your_access_key",
            "s3_secret_key": "your_secret_key",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name/folder"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        # Assert that the init_s3_client method is called with the correct arguments
        assert log_message.bucket_name == "your_bucket_name"
        assert log_message.bucket_prefix == "folder"

    def test_s3_bucket_name_provided_with_prefix_and_slash_at_end(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "keys",
            "s3_access_key": "your_access_key",
            "s3_secret_key": "your_secret_key",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name/folder/"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        # Assert that the init_s3_client method is called with the correct arguments
        assert log_message.bucket_name == "your_bucket_name"
        assert log_message.bucket_prefix == "folder"

    #  s3_connection_mode is not set to default, keys or iam_role
    def test_s3_connection_mode_invalid(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "YOLO",
            "boto3_log_level": "INFO"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        with pytest.raises(ShieldException) as e:
            print(e)
            LogMessageInS3File()

    #  s3_bucket_name is not provided
    def test_s3_bucket_name_not_provided(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "keys",
            "s3_access_key": "your_access_key",
            "s3_secret_key": "your_secret_key",
            "boto3_log_level": "INFO"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        with pytest.raises(ShieldException) as e:
            print(e)
            LogMessageInS3File()

    #  s3_access_key or s3_secret_key is not provided
    def test_s3_access_key_secret_key_not_provided(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "keys",
            "s3_access_key": "your_access_key",
            "boto3_log_level": "INFO"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        with pytest.raises(ShieldException):
            LogMessageInS3File()

    # s3 error when doing put_object
    def test_s3_error_put_object(self, mocker):
        # Mock the dependencies
        mocker.patch('boto3.client')
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()
        mocker.patch.object(log_message.s3_client, 'put_object', side_effect=Exception("S3 error"))

        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": 1601002345000,
            "applicationKey": "application_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1"
        }

        res_data = {
            "authorized": 'true',
            "enforce": 'true',
            "requestId": "55ee-91c2-9e05a1ebe151",
            "requestDateTime": "1970-01-01T00:02:03.455+00:00",
            "userId": "jai.patel",
            "applicationName": "saitama",
            "maskedTraits": {
                "PERSON": "<<PERSON>>",
                "LOCATION": "<<LOCATION>>"
            },
            "statusCode": 0,
            "statusMessage": "Access is allowed",
            "rangerAuditIds": ["d5821c40-1ead-4907-94d3-bb6337b746d3-3"],
            "rangerPolicyIds": [11],
            "paigPolicyIds": [3]
        }

        # Create a ShieldAudit object
        mock_audit = ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                                 ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])

        # Call the log method
        with pytest.raises(ShieldException):
            log_message.write_log_to_s3("object_key", mock_audit)

        # Assert that the put_object method of the s3_client is called with the correct arguments
        log_message.s3_client.put_object.assert_called_once_with(
            Body=json.dumps(mock_audit.__dict__),
            Bucket=log_message.bucket_name,
            Key=mocker.ANY
        )

    @pytest.mark.asyncio
    async def test_logs(self, mocker):
        mocker.patch('boto3.client')
        # Mock the dependencies
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mock_s3_audit_logger = MagicMock()
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.get_or_create_s3_audit_logger',
                     return_value=mock_s3_audit_logger)

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": 1601002345000,
            "applicationKey": "app_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1",
            "clientHostName": "localhost"
        }

        res_data = {
            "authorized": 'true',
            "enforce": 'true',
            "requestId": "55ee-91c2-9e05a1ebe151",
            "requestDateTime": "1970-01-01T00:02:03.455+00:00",
            "userId": "jai.patel",
            "applicationName": "saitama",
            "maskedTraits": {
                "PERSON": "<<PERSON>>",
                "LOCATION": "<<LOCATION>>"
            },
            "statusCode": 0,
            "statusMessage": "Access is allowed",
            "rangerAuditIds": ["d5821c40-1ead-4907-94d3-bb6337b746d3-3"],
            "rangerPolicyIds": [11],
            "paigPolicyIds": [3]
        }

        # Create a ShieldAudit object
        mock_audit = ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                                 ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])

        # Call the log method
        await log_message.log(mock_audit)
        mock_s3_audit_logger.log.assert_called_once_with(mock_audit)

    def test_get_or_create_s3_audit_logger(self, mocker):
        mocker.patch('boto3.client')
        # Mock the dependencies
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocked_s3_audit_logger = mocker.patch('api.shield.logfile.log_message_in_s3.S3AuditLogger')

        # Arrange
        log_message_in_s3_file = LogMessageInS3File()
        log_message_in_s3_file.audit_spool_dir = f"{Path(__file__).parent}/workdir/shield/audit-spool"
        log_message_in_s3_file.max_queue_size = 10
        log_message_in_s3_file.audit_event_queue_timeout_sec = 5
        s3_audit_logger_mock = MagicMock()
        mocked_s3_audit_logger.return_value = s3_audit_logger_mock

        # Act
        result = log_message_in_s3_file.get_or_create_s3_audit_logger()

        # Assert
        mocked_s3_audit_logger.assert_called_once_with(log_message_in_s3_file,
                                                       f"{Path(__file__).parent}/workdir/shield/audit-spool",
                                                       10,
                                                       5)
        assert s3_audit_logger_mock.daemon
        s3_audit_logger_mock.start.assert_called_once()
        assert result == s3_audit_logger_mock

    @pytest.mark.asyncio
    async def test_logs_with_audit_event_queue_full_exception(self, mocker):
        mocker.patch('boto3.client')
        # Mock the dependencies
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mock_s3_audit_logger = MagicMock()
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.get_or_create_s3_audit_logger',
                     return_value=mock_s3_audit_logger)
        mock_s3_audit_logger.log.side_effect = AuditEventQueueFullException()

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": 1601002345000,
            "applicationKey": "app_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1",
            "clientHostName": "localhost"
        }

        res_data = {
            "authorized": 'true',
            "enforce": 'true',
            "requestId": "55ee-91c2-9e05a1ebe151",
            "requestDateTime": "1970-01-01T00:02:03.455+00:00",
            "userId": "jai.patel",
            "applicationName": "saitama",
            "maskedTraits": {
                "PERSON": "<<PERSON>>",
                "LOCATION": "<<LOCATION>>"
            },
            "statusCode": 0,
            "statusMessage": "Access is allowed",
            "rangerAuditIds": ["d5821c40-1ead-4907-94d3-bb6337b746d3-3"],
            "rangerPolicyIds": [11],
            "paigPolicyIds": [3]
        }

        # Create a ShieldAudit object
        mock_audit = ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                                 ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])

        # Call the log method
        with pytest.raises(ShieldException):
            await log_message.log_audit_event(mock_audit)

    @pytest.mark.asyncio
    async def test_logs_with_exception(self, mocker):
        mocker.patch('boto3.client')
        # Mock the dependencies
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mock_s3_audit_logger = MagicMock()
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.get_or_create_s3_audit_logger',
                     return_value=mock_s3_audit_logger)
        mock_s3_audit_logger.log.side_effect = Exception()

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": 1601002345000,
            "applicationKey": "app_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1",
            "clientHostName": "localhost"
        }

        res_data = {
            "authorized": 'true',
            "enforce": 'true',
            "requestId": "55ee-91c2-9e05a1ebe151",
            "requestDateTime": "1970-01-01T00:02:03.455+00:00",
            "userId": "jai.patel",
            "applicationName": "saitama",
            "maskedTraits": {
                "PERSON": "<<PERSON>>",
                "LOCATION": "<<LOCATION>>"
            },
            "statusCode": 0,
            "statusMessage": "Access is allowed",
            "rangerAuditIds": ["d5821c40-1ead-4907-94d3-bb6337b746d3-3"],
            "rangerPolicyIds": [11],
            "paigPolicyIds": [3]
        }

        # Create a ShieldAudit object
        mock_audit = ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                                 ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])

        # Call the log method
        with pytest.raises(ShieldException):
            await log_message.log_audit_event(mock_audit)

    @pytest.mark.asyncio
    async def test_logs_with_disk_full_exception(self, mocker):
        mocker.patch('boto3.client')
        # Mock the dependencies
        side_effect = lambda prop, default: {
            "s3_connection_mode": "default",
            "boto3_log_level": "INFO",
            "s3_bucket_name": "your_bucket_name"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mock_s3_audit_logger = MagicMock()
        mocker.patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File.get_or_create_s3_audit_logger',
                     return_value=mock_s3_audit_logger)
        mock_s3_audit_logger.log.side_effect = DiskFullException()

        # Create an instance of LogMessageInS3File
        log_message = LogMessageInS3File()

        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": 1601002345000,
            "applicationKey": "app_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1",
            "clientHostName": "localhost"
        }

        res_data = {
            "authorized": 'true',
            "enforce": 'true',
            "requestId": "55ee-91c2-9e05a1ebe151",
            "requestDateTime": "1970-01-01T00:02:03.455+00:00",
            "userId": "jai.patel",
            "applicationName": "saitama",
            "maskedTraits": {
                "PERSON": "<<PERSON>>",
                "LOCATION": "<<LOCATION>>"
            },
            "statusCode": 0,
            "statusMessage": "Access is allowed",
            "rangerAuditIds": ["d5821c40-1ead-4907-94d3-bb6337b746d3-3"],
            "rangerPolicyIds": [11],
            "paigPolicyIds": [3]
        }

        # Create a ShieldAudit object
        mock_audit = ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                                 ["PERSON", "LOCATION"],
                                 [{"originalMessage": "test_message", "maskedMessage": "test_message"}])

        # Call the log method
        with pytest.raises(ShieldException):
            await log_message.log_audit_event(mock_audit)
