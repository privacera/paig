from unittest.mock import patch, MagicMock
from paig_securechat import launcher


def test_thread_session():
    with patch('paig_securechat.launcher.ThreadServer') as mock_thread_session:
        mock_thread_session.run_in_thread.return_value = MagicMock()
        session = launcher.ThreadSession(host="0.0.0.0", port="80001", root_path="/tests")
        assert session.server_thread != None
        mock_thread_session.assert_called_once()


def test_active_session_not_started_app():
    assert launcher.active_session() == None


def test_is_colab():
    assert isinstance(launcher._is_colab(), bool)


def test_get_url():
    assert launcher._get_url("0.0.0.0", 8000) == "http://localhost:8000/"
    assert launcher._get_url("127.1.1.1", 8000) == "http://127.1.1.1:8000/"


def test_launch_app():
    with patch('paig_securechat.launcher.set_up_standalone_mode') as mock_set_up_standalone_mode:
        mock_set_up_standalone_mode.return_value = MagicMock()
        with patch('paig_securechat.launcher.create_or_update_tables') as mock_create_or_update_tables:
            mock_create_or_update_tables.return_value = MagicMock()
            with patch('paig_securechat.launcher.ThreadSession') as mock_thread_session:
                mock_thread_session.return_value = MagicMock()
                session = launcher.launch_app()
                assert session == mock_thread_session.return_value
                assert launcher.active_session() == mock_thread_session.return_value
                mock_thread_session.assert_called_once()
                mock_set_up_standalone_mode.assert_called_once()
                mock_create_or_update_tables.assert_called_once()
                launcher.close_app()
                assert launcher.active_session() == None
