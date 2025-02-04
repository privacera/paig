import pytest
from unittest.mock import patch, MagicMock
import subprocess
from paig_evaluation.command_utils import (
    run_command_in_foreground,
    run_command_in_background,
    check_process_status,
    wait_for_process_complete,
)

@pytest.fixture
def mock_popen():
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
        mock_process.stderr.readline.side_effect = ["error1\n", "error2\n", ""]
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.communicate.return_value = ("remaining_stdout", "remaining_stderr")
        mock_popen.return_value = mock_process
        yield mock_popen

def test_run_command_in_foreground(mock_popen):
    command = "echo test"
    stdout, stderr = run_command_in_foreground(command, verbose=True)

    assert stdout == "line1\nline2\nremaining_stdout"
    assert stderr == "error1\nerror2\nremaining_stderr"


def test_run_command_in_background(mock_popen):
    command = "echo background"
    process = run_command_in_background(command)

    assert process == mock_popen.return_value


def test_check_process_status(mock_popen):
    process = run_command_in_background("dummy command")
    status = check_process_status(process)
    assert status == 1
    process.poll.assert_called()

def test_wait_for_process_complete(mock_popen):
    process = run_command_in_background("dummy command")
    wait_for_process_complete(process, verbose=True)

    process.poll.assert_called()
    process.stdout.readline.assert_called()
