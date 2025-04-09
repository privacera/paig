import json
import threading

import pytest
from unittest.mock import Mock, patch

import paig_client.client
from paig_client.backend import ShieldRestHttpClient, ShieldAccessRequest, VectorDBAccessRequest, StreamAccessAuditRequest
from paig_client.core import PAIGPlugin, PAIGApplication
from paig_client.model import ConversationType

SHIELD_SERVER_URL = "http://localhost:8000"


def do_post(client):
    request = ShieldAccessRequest(
        application_key="application_key",
        client_application_key="client_application_key",
        conversation_thread_id="conversation_thread_id",
        request_id="request_id",
        user_name="user1",
        request_text=["request_text"],
        conversation_type=ConversationType.PROMPT)

    response = client.is_access_allowed(request)
    assert response is not None


def load_app_config_file(app_config_file):
    with open(app_config_file, "r") as f:
        app_config = json.load(f)
    return (app_config, {"shield_server_key_id": app_config['shieldServerKeyId'],
                         "shield_plugin_key_id": app_config['shieldPluginKeyId'],
                         "shield_server_public_key": app_config['shieldServerPublicKey'],
                         "shield_plugin_private_key": app_config['shieldPluginPrivateKey']})


#@pytest.mark.e2e_test
def test_post2(setup_paig_plugin_with_app_config_file_name):
    app_config_file, encryption_keys_info = load_app_config_file(setup_paig_plugin_with_app_config_file_name)
    client = ShieldRestHttpClient(base_url=SHIELD_SERVER_URL, tenant_id=app_config_file['tenantId'],
                                  api_key=app_config_file['apiKey'],
                                  encryption_keys_info=encryption_keys_info)
    thread = threading.Thread(target=do_post, args=(client,))
    thread.start()
    thread.join()


@pytest.mark.e2e_test
def test_post3(setup_paig_plugin_with_app_config_file_name):
    app_config_file, encryption_keys_info = load_app_config_file(setup_paig_plugin_with_app_config_file_name)
    client = ShieldRestHttpClient(base_url=SHIELD_SERVER_URL, tenant_id=app_config_file['tenantId'],
                                  api_key=app_config_file['apiKey'],
                                  encryption_keys_info=encryption_keys_info)
    thread_list = []
    for i in range(100):
        thread_list.append(threading.Thread(target=do_post, args=(client,)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


def test_shield_access_request_with_user_groups():
    """
    Test that ShieldAccessRequest properly handles user groups and external groups.
    """
    # Create a ShieldAccessRequest with user groups
    request = ShieldAccessRequest(
        application_key="test_app_key",
        client_application_key="test_client_key",
        conversation_thread_id="test_thread",
        request_id="test_request",
        user_name="test_user",
        use_external_groups=True,
        user_groups=["group1", "group2"]
    )

    # Verify the fields are set correctly
    assert request.use_external_groups is True
    assert request.user_groups == ["group1", "group2"]

    # Verify they are included in the payload dictionary
    payload = request.to_payload_dict()
    assert payload["useExternalGroups"] is True
    assert payload["externalGroups"] == ["group1", "group2"]

    # Test default values
    request = ShieldAccessRequest(
        application_key="test_app_key",
        client_application_key="test_client_key",
        conversation_thread_id="test_thread",
        request_id="test_request",
        user_name="test_user"
    )
    assert request.use_external_groups is True  # Default value
    assert request.user_groups == []  # Default value


def test_vector_db_access_request_with_user_groups():
    """
    Test that VectorDBAccessRequest properly handles user groups and external groups.
    """
    # Create a VectorDBAccessRequest with user groups
    request = VectorDBAccessRequest(
        application_key="test_app_key",
        client_application_key="test_client_key",
        conversation_thread_id="test_thread",
        request_id="test_request",
        user_name="test_user",
        use_external_groups=True,
        user_groups=["group1", "group2"]
    )

    # Verify the fields are set correctly
    assert request.use_external_groups is True
    assert request.user_groups == ["group1", "group2"]

    # Verify they are included in the payload dictionary
    payload = request.to_payload_dict()
    assert payload["useExternalGroups"] is True
    assert payload["externalGroups"] == ["group1", "group2"]

    # Test default values
    request = VectorDBAccessRequest(
        application_key="test_app_key",
        client_application_key="test_client_key",
        conversation_thread_id="test_thread",
        request_id="test_request",
        user_name="test_user"
    )
    assert request.use_external_groups is True  # Default value
    assert request.user_groups == []  # Default value


def test_stream_access_audit_request_with_user_groups():
    """
    Test that StreamAccessAuditRequest properly handles user groups and external groups.
    """
    # Create a StreamAccessAuditRequest with user groups
    request = StreamAccessAuditRequest(
        event_time=1234567890,
        tenant_id="test_tenant",
        user_id="test_user",
        use_external_groups=True,
        user_groups=["group1", "group2"]
    )

    # Verify the fields are set correctly
    assert request.use_external_groups is True
    assert request.user_groups == ["group1", "group2"]

    # Verify they are included in the payload dictionary
    payload = request.to_payload_dict()
    assert payload["useExternalGroups"] is True
    assert payload["externalGroups"] == ["group1", "group2"]

    # Test default values
    request = StreamAccessAuditRequest(
        event_time=1234567890,
        tenant_id="test_tenant",
        user_id="test_user"
    )
    assert request.use_external_groups is True  # Default value
    assert request.user_groups == []  # Default value

