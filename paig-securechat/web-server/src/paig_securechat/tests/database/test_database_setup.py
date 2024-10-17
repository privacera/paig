import pytest
from click.testing import CliRunner
from database_setup.database_standalone import db_setup
from unittest.mock import patch

@pytest.fixture
def runner():
    return CliRunner()

def test_db_setup_default_values(runner):
    with patch('database_setup.database_standalone.db_setup', exit_code=0) as mock_db_setup:
        result = runner.invoke(db_setup, [])
        assert result.exit_code == 0

def test_db_setup_custom_values(runner):
    with patch('database_setup.database_standalone.db_setup', exit_code=0) as mock_db_setup:
        result = runner.invoke(db_setup, ["--secure_chat_deployment", "test", "--config_path", "configs"])
        assert result.exit_code == 0