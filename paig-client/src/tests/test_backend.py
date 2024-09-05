import json
import threading

import pytest

from paig_client.backend import ShieldRestHttpClient, ShieldAccessRequest
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
