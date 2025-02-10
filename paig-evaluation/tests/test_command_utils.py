import pytest
import subprocess
from paig_evaluation.command_utils import (
    run_command_in_foreground,
    run_command_in_background,
    check_process_status,
    wait_for_process_complete
)


@pytest.mark.parametrize("command, expected_output", [
    ("echo Hello", "Hello"),
    ("echo pytest", "pytest"),
])
def test_run_command_in_foreground(command, expected_output):
    stdout, stderr = run_command_in_foreground(command)
    assert stderr == "", f"Expected no stderr, got: {stderr}"
    assert expected_output in stdout, f"Expected output '{expected_output}' not found in stdout: {stdout}"

def test_run_command_in_foreground_exception():
    with pytest.raises(RuntimeError) as exc_info:
        run_command_in_foreground("invalid_command")
    assert "Error running command" in str(exc_info.value)


def test_run_command_in_background():
    command = "echo Hello"
    process = run_command_in_background(command)
    assert isinstance(process, subprocess.Popen), "Expected process to be an instance of subprocess.Popen"
    assert check_process_status(process) in {0, 1}, "Process should be running or completed state"


def test_run_command_in_background_exception():
    with pytest.raises(FileNotFoundError) as exc_info:
        run_command_in_background("invalid_command")
    assert "No such file or directory" in str(exc_info.value)


def test_check_process_status():
    process = subprocess.Popen(["echo", "Hello"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert check_process_status(process) in {0, 1}, "Process should be running or completed state"


def test_check_process_status_exception():
    with pytest.raises(RuntimeError) as exc_info:
        check_process_status(None)  # Passing invalid process
    assert "Error checking process status" in str(exc_info.value)


def test_wait_for_process_complete():
    process = subprocess.Popen(["echo", "WaitCompleteTest"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    wait_for_process_complete(process)
    stdout, _ = process.communicate()
    assert "WaitCompleteTest" in stdout.strip(), f"Expected output not found in stdout: {stdout.strip()}"


def test_wait_for_process_complete_exception():
    with pytest.raises(RuntimeError) as exc_info:
        wait_for_process_complete(None)  # Passing invalid process
    assert "Error checking process status" in str(exc_info.value)
