import json
from pathlib import Path
from unittest.mock import patch
from api.shield.logfile.audit_loggers import FluentdAuditLogger, S3AuditLogger, LocalAuditLogger
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.shield_audit import ShieldAudit
from core.utils import format_to_root_path


def authorize_req_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return AuthorizeRequest(tenant_id='test_tenant', req_data=req_json, user_role='OWNER')


def authz_res_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authz_response.json"
    with open(json_file_path, 'r') as json_file:
        res_json = json.load(json_file)

    return AuthzServiceResponse(res_data=res_json)


def get_shield_audit_obj():
    auth_req = authorize_req_data()
    authz_res = authz_res_data()
    traits = ['TOXIC', 'PERSON', 'EMAIL_ADDRESS']
    authz_res.masked_traits = {}
    original_masked_text_list = [{"originalMessage": "Hello", "maskedMessage": "Hello"}]
    shield_audit = ShieldAudit(auth_req, authz_res, traits, original_masked_text_list)
    return shield_audit


@patch('api.shield.client.http_fluentd_client.FluentdRestHttpClient')
def test_fluentd_audit_logger(mock_fluentd_http_client):
    fluentd_audit_logger = FluentdAuditLogger(mock_fluentd_http_client, format_to_root_path('tests/api/shield/audit_spool_dir'), 0, 5)
    shield_audit = get_shield_audit_obj()
    fluentd_audit_logger.push_audit_event_to_server(shield_audit)
    mock_fluentd_http_client.log_message.assert_called_once()


@patch('api.shield.logfile.log_message_in_s3.LogMessageInS3File')
def test_s3_audit_logger(mock_log_message_in_s3):
    s3_audit_logger = S3AuditLogger(mock_log_message_in_s3, format_to_root_path('tests/api/shield/audit_spool_dir'), 0, 0)
    mock_log_message_in_s3.create_file_structure.return_value = 'test_file_structure'
    mock_log_message_in_s3.bucket_prefix = 'test_bucket_prefix'
    shield_audit = get_shield_audit_obj()
    s3_audit_logger.push_audit_event_to_server(shield_audit)
    mock_log_message_in_s3.write_log_to_s3.assert_called_once()


@patch('api.shield.logfile.log_message_in_local.LogMessageInLocal')
def test_local_audit_logger(mock_log_message_in_local):
    mock_log_message_in_local.directory_path = 'tests/api/shield/test_directory_path'
    local_audit_logger = LocalAuditLogger(mock_log_message_in_local, format_to_root_path('tests/api/shield/audit_spool_dir'), 0, 0)
    shield_audit = get_shield_audit_obj()
    local_audit_logger.push_audit_event_to_server(shield_audit)
    mock_log_message_in_local.write_log_to_local_file.assert_called_once()
