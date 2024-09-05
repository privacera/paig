import os

import pytest

import paig_client.client
import paig_client.core
import paig_client.exception
import paig_client.message
import paig_client.model
import paig_client.encryption
from paig_client.backend import ShieldAccessResult
from unittest.mock import patch


def test_setup(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        app = paig_client.client.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                                frameworks=[])
        assert app.tenant_id
        assert app.api_key


def test_setup_with_contents(setup_paig_plugin_with_app_config_file_contents):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        app = paig_client.client.setup_app(application_config=setup_paig_plugin_with_app_config_file_contents,
                                                frameworks=[])
        assert app.tenant_id
        assert app.api_key


def test_setup_with_dict(setup_paig_plugin_with_app_config_dict):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        app = paig_client.client.setup_app(application_config=setup_paig_plugin_with_app_config_dict, frameworks=[])
        assert app.tenant_id
        assert app.api_key


def test_setup2(setup_paig_plugin_with_app_config_file_name):
    with pytest.raises(Exception) as exception_info:
        paig_client.client.setup_app()
    assert exception_info.type == paig_client.exception.PAIGException
    assert exception_info.value.args[
               0] == paig_client.message.ErrorMessage.PARAMETERS_FOR_APP_CONFIG_NOT_PROVIDED.format()


def test_setup3(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        paig_client.client.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                          frameworks=[])
        # with pytest.raises(Exception) as exception_info:
        paig_client.client.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                          frameworks=[])
        # assert exception_info.type == paig_client.exception.PAIGException
        # assert exception_info.value.args[0] == paig_client.message.ErrorMessage.PAIG_IS_ALREADY_INITIALIZED.format(
        #     tenant_id="tenant_id", api_key="api_key")


@pytest.mark.e2e_test
def test_check_access(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        paig_client.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name, frameworks=[])
        with paig_client.client.create_shield_context(username="user1"):
            with patch("paig_client.backend.ShieldRestHttpClient.is_access_allowed",
                       return_value=ShieldAccessResult(
                           **{"isAllowed": True, "responseMessages": [{"responseText": "hello world"}]})):
                response_text = paig_client.client.check_access(text="hello world",
                                                                 conversation_type=paig_client.model.ConversationType.PROMPT)
        assert "hello world" in response_text[0].get_response_text()


def test_app_config_as_parameter_exists(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        app = paig_client.core.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name)
        assert app.tenant_id


def test_app_config_as_parameter_does_not_exist():
    with pytest.raises(Exception):
        app = paig_client.core.setup_app(application_config_file="./plugin_config_does_not_exit.json")


def test_app_config_as_env_var_exists(setup_paig_plugin_with_app_config_file_name):
    os.environ["PRIVACERA_SHIELD_CONF_FILE"] = setup_paig_plugin_with_app_config_file_name
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        paig_client.core.setup(frameworks=['None'])
        assert paig_client.core._paig_plugin.get_current_application().tenant_id


def test_app_config_as_env_var_does_not_exist(setup_paig_plugin_with_app_config_file_name):
    os.environ["PRIVACERA_SHIELD_CONF_FILE"] = "./plugin_config_does_not_exit.json"
    with pytest.raises(Exception):
        app = paig_client.core.setup_app()


def test_access_exception():
    with pytest.raises(paig_client.exception.AccessControlException):
        paig_client.client.dummy_access_denied()
