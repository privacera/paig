import builtins
import errno
import json
import os
from pathlib import Path
from time import sleep

import pytest

from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.shield_audit import ShieldAudit
from api.shield.logfile.log_message_in_local import LogMessageInLocal
from api.shield.utils.custom_exceptions import ShieldException


@pytest.fixture
def log_data():
    req_data = {
        "threadId": "12345",
        "requestId": "456",
        "sequenceNumber": 1,
        "requestType": "enriched_prompt",
        "requestDateTime": 1640997244000,
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

    # Create a mock FileSystemAudit object
    return ShieldAudit(AuthorizeRequest(req_data, "123", "OWNER"), AuthzServiceResponse(res_data),
                       ["PERSON", "LOCATION"],
                       [{"originalMessage": "test_message", "maskedMessage": "test_message"}])


class TestLogMessageInLocal:

    #  Logs are successfully written to the local directory path specified in the configuration file
    @pytest.mark.asyncio
    async def test_logs_written_to_local_directory(self, mocker, log_data):
        # Given
        local_log_path = f"{Path(__file__).parent}/workdir/shield/audit_logs"
        audit_spool_dir = f"{Path(__file__).parent}/workdir/shield/audit-spool"

        side_effect = lambda prop, default: {
            "local_directory_path": local_log_path,
            "audit_spool_dir": audit_spool_dir
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # When
        log_message_in_local = LogMessageInLocal()
        await log_message_in_local.log_audit_event(log_data)
        # Since the thread is running hence added the sleep to wait for the thread to complete
        sleep(10 / 1000)

        # Then
        assert os.path.exists(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12345_1.json")
        assert os.path.isfile(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12345_1.json")
        assert os.path.exists(f"{audit_spool_dir}")
        assert os.path.getsize(
            f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12345_1.json") > 0

    #  The log file is successfully written to the local directory path even if the directory already exists
    @pytest.mark.asyncio
    async def test_log_file_written_to_existing_directory(self, mocker, log_data):
        # Given
        local_log_path = f"{Path(__file__).parent}/workdir/shield/audit_logs"
        assert os.path.exists(local_log_path)
        audit_spool_dir = f"{Path(__file__).parent}/workdir/shield/audit-spool"
        side_effect = lambda prop, default: {
            "local_directory_path": local_log_path,
            "audit_spool_dir": audit_spool_dir
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # When
        log_data.threadId = '12346'
        log_message_in_local = LogMessageInLocal()
        await log_message_in_local.log_audit_event(log_data)
        # Since the thread is running hence added the sleep to wait for the thread to complete
        sleep(10 / 1000)

        # Then
        assert os.path.exists(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12346_1.json")
        assert os.path.isfile(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12346_1.json")
        assert os.path.exists(f"{audit_spool_dir}")
        assert os.path.getsize(
            f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12346_1.json") > 0

    #  The local directory path specified in the configuration file is invalid or does not exist
    @pytest.mark.asyncio
    async def test_invalid_or_nonexistent_directory_path(self, mocker, log_data):
        # Given
        side_effect = lambda prop, default: {
            "local_directory_path": "/invalid_directory_path"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch.object(os, 'makedirs', side_effect=OSError)

        log_message_in_local = LogMessageInLocal()

        # When/Then
        with pytest.raises(ShieldException) as e:
            await log_message_in_local.log_audit_event(log_data)

        print(f"\nGot exception: {e.value}")

    #  The log file cannot be created due to insufficient permissions
    @pytest.mark.asyncio
    async def test_log_file_cannot_be_created_due_to_insufficient_permissions(self, mocker, log_data):
        # Given
        local_log_path = f"{Path(__file__).parent}/workdir/shield/audit_logs"
        assert os.path.exists(local_log_path)

        side_effect = lambda prop, default: {
            "local_directory_path": local_log_path
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch.object(os, 'makedirs', side_effect=PermissionError)
        log_message_in_local = LogMessageInLocal()

        # When/Then
        with pytest.raises(ShieldException) as e:
            await log_message_in_local.log_audit_event(log_data)

        print(f"\nGot exception: {e.value}")

    #  The log file cannot be written due to insufficient permissions
    @pytest.mark.asyncio
    async def test_log_file_cannot_be_written_due_to_insufficient_permissions(self, mocker, log_data):
        # Given
        local_log_path = f"{Path(__file__).parent}/workdir/shield/audit_logs"
        assert os.path.exists(local_log_path)
        audit_spool_dir = f"{Path(__file__).parent}/workdir/shield/audit-spool"

        side_effect = lambda prop, default: {
            "local_directory_path": local_log_path,
            "audit_spool_dir": audit_spool_dir
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch.object(builtins, 'open', side_effect=PermissionError)
        log_message_in_local = LogMessageInLocal()
        log_data.threadId = '12347'

        # When/Then
        with pytest.raises(ShieldException) as e:
            await log_message_in_local.log_audit_event(log_data)

        print(f"\nGot exception: {e.value}")

        assert os.path.isdir(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01")
        assert not os.path.exists(
            f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12347_1.json")

    #  The log file cannot be written due to a disk space issue
    @pytest.mark.asyncio
    async def test_log_file_cannot_be_written_due_to_disk_space_issue(self, mocker, log_data):
        # Given
        local_log_path = f"{Path(__file__).parent}/workdir/shield/audit_logs"
        assert os.path.exists(local_log_path)
        audit_spool_dir = f"{Path(__file__).parent}/workdir/shield/audit-spool"

        side_effect = lambda prop, default: {
            "local_directory_path": local_log_path,
            "audit_spool_dir": audit_spool_dir
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        full_log_path = f"{Path(__file__).parent}/workdir/shield/audit_logs/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12348_1.json"
        # Custom side effect for json.dump to raise OSError only in write_log_to_local_file
        original_json_dump = json.dump

        def json_dump_side_effect(data, fp, *args, **kwargs):
            if full_log_path in str(fp.name):
                raise OSError(errno.ENOSPC, "No space left on device")
            return original_json_dump(data, fp, *args, **kwargs)

        mocker.patch('json.dump', side_effect=json_dump_side_effect)
        log_message_in_local = LogMessageInLocal()
        log_data.threadId = '12348'
        await log_message_in_local.log_audit_event(log_data)
        # When/Then
        with pytest.raises(ShieldException) as e:
            log_message_in_local.write_log_to_local_file(full_log_path, log_data)

        print(f"\nGot exception: {e.value}")

        assert os.path.isdir(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01")
        assert os.path.exists(f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12348_1.json")
        assert os.path.getsize(
            f"{local_log_path}/tenant_id=123/year=2022/month=01/day=01/123_2022_01_01_12348_1.json") == 0
