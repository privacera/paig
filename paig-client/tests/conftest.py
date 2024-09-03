import json
from pathlib import Path
import pytest
import privacera_shield.core

application_config_file = f"{Path(__file__).parent}/plugin_config.json"
curr_dir = f"{Path(__file__).parent}"


@pytest.fixture
def setup_paig_plugin_with_app_config_file_name():
    privacera_shield.core._paig_plugin = None
    yield application_config_file
    if privacera_shield.core._paig_plugin:
        privacera_shield.core._paig_plugin.undo_setup()
        privacera_shield.core._paig_plugin = None


@pytest.fixture
def setup_paig_plugin_with_app_config_file_contents():
    privacera_shield.core._paig_plugin = None
    with open(application_config_file, "r") as f:
        app_config = f.read()
    yield app_config
    if privacera_shield.core._paig_plugin:
        privacera_shield.core._paig_plugin.undo_setup()
        privacera_shield.core._paig_plugin = None


@pytest.fixture
def setup_paig_plugin_with_app_config_dict():
    privacera_shield.core._paig_plugin = None
    with open(application_config_file, "r") as f:
        app_config = json.load(f)
    yield app_config
    if privacera_shield.core._paig_plugin:
        privacera_shield.core._paig_plugin.undo_setup()
        privacera_shield.core._paig_plugin = None


@pytest.fixture
def setup_curr_dir():
    yield curr_dir
