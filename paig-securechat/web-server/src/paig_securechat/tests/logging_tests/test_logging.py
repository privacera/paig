import pytest
from core.logging_init import get_logs_directory


@pytest.fixture
def log_directory(tmpdir):
    empty_dir = tmpdir.mkdir("test/logs")
    return empty_dir


def test_get_log_path_without_env_variable():
    result = get_logs_directory()
    assert "securechat/logs" == result  # add assertion here


def test_get_log_path_with_env_variable(monkeypatch, tmpdir):
    monkeypatch.setenv('LOG_PATH', tmpdir)
    result = get_logs_directory()
    monkeypatch.delenv('LOG_PATH', raising=False)
    assert tmpdir == result
