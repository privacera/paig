import json
from pathlib import Path
import pytest
import paig_client.core
import os

os.environ["PAIG_CLIENT_DEPLOYMENT"] = "test"

application_config_file = f"{Path(__file__).parent}/plugin_config.json"
curr_dir = f"{Path(__file__).parent}"


@pytest.fixture
def setup_paig_plugin_with_app_config_file_name():
    paig_client.core._paig_plugin = None
    yield application_config_file
    if paig_client.core._paig_plugin:
        paig_client.core._paig_plugin.undo_setup()
        paig_client.core._paig_plugin = None


@pytest.fixture
def setup_paig_plugin_with_app_config_file_contents():
    paig_client.core._paig_plugin = None
    with open(application_config_file, "r") as f:
        app_config = f.read()
    yield app_config
    if paig_client.core._paig_plugin:
        paig_client.core._paig_plugin.undo_setup()
        paig_client.core._paig_plugin = None


@pytest.fixture
def setup_paig_plugin_with_app_config_dict():
    paig_client.core._paig_plugin = None
    with open(application_config_file, "r") as f:
        app_config = json.load(f)
    yield app_config
    if paig_client.core._paig_plugin:
        paig_client.core._paig_plugin.undo_setup()
        paig_client.core._paig_plugin = None


@pytest.fixture
def setup_curr_dir():
    yield curr_dir
