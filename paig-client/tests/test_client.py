import os

import pytest

import privacera_shield.client
import privacera_shield.core
import privacera_shield.exception
import privacera_shield.message
import privacera_shield.model
import privacera_shield.encryption


def test_setup(setup_paig_plugin_with_app_config_file_name):
    app = privacera_shield.client.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                            frameworks=[])
    assert app.tenant_id
    assert app.api_key


def test_setup_with_contents(setup_paig_plugin_with_app_config_file_contents):
    app = privacera_shield.client.setup_app(application_config=setup_paig_plugin_with_app_config_file_contents,
                                            frameworks=[])
    assert app.tenant_id
    assert app.api_key


def test_setup_with_dict(setup_paig_plugin_with_app_config_dict):
    app = privacera_shield.client.setup_app(application_config=setup_paig_plugin_with_app_config_dict, frameworks=[])
    assert app.tenant_id
    assert app.api_key


def test_setup2(setup_paig_plugin_with_app_config_file_name):
    with pytest.raises(Exception) as exception_info:
        privacera_shield.client.setup_app()
    assert exception_info.type == privacera_shield.exception.PAIGException
    assert exception_info.value.args[
               0] == privacera_shield.message.ErrorMessage.PARAMETERS_FOR_APP_CONFIG_NOT_PROVIDED.format()


def test_setup3(setup_paig_plugin_with_app_config_file_name):
    privacera_shield.client.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                      frameworks=[])
    # with pytest.raises(Exception) as exception_info:
    privacera_shield.client.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                      frameworks=[])
    # assert exception_info.type == privacera_shield.exception.PAIGException
    # assert exception_info.value.args[0] == privacera_shield.message.ErrorMessage.PAIG_IS_ALREADY_INITIALIZED.format(
    #     tenant_id="tenant_id", api_key="api_key")


@pytest.mark.e2e_test
def test_check_access(setup_paig_plugin_with_app_config_file_name):
    privacera_shield.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name, frameworks=[])
    with privacera_shield.client.create_shield_context(username="user1"):
        response_text = privacera_shield.client.check_access(text="hello world",
                                                             conversation_type=privacera_shield.model.ConversationType.PROMPT)
    assert response_text[0].get_response_text() == "response: hello world"


def test_app_config_as_parameter_exists(setup_paig_plugin_with_app_config_file_name):
    app = privacera_shield.core.setup_app(application_config_file=setup_paig_plugin_with_app_config_file_name)
    assert app.tenant_id


def test_app_config_as_parameter_does_not_exist():
    with pytest.raises(Exception):
        app = privacera_shield.core.setup_app(application_config_file="./plugin_config_does_not_exit.json")


def test_app_config_as_env_var_exists(setup_paig_plugin_with_app_config_file_name):
    os.environ["PRIVACERA_SHIELD_CONF_FILE"] = setup_paig_plugin_with_app_config_file_name
    privacera_shield.core.setup(frameworks=['None'])
    assert privacera_shield.core._paig_plugin.get_current_application().tenant_id


def test_app_config_as_env_var_does_not_exist(setup_paig_plugin_with_app_config_file_name):
    os.environ["PRIVACERA_SHIELD_CONF_FILE"] = "./plugin_config_does_not_exit.json"
    with pytest.raises(Exception):
        app = privacera_shield.core.setup_app()


def test_access_exception():
    with pytest.raises(privacera_shield.exception.AccessControlException):
        privacera_shield.client.dummy_access_denied()
