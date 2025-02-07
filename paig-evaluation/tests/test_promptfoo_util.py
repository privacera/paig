import pytest
from unittest.mock import patch, MagicMock, mock_open
import os


from paig_evaluation.promptfoo_utils import (
    check_package_exists,
    check_npm_dependency,
    install_npm_dependency,
    check_and_install_npm_dependency,
    ensure_promptfoo_config
)

@pytest.mark.parametrize("package_name, expected_result", [
    ("node", True),
    ("nonexistent_package", False),
])
@patch("subprocess.run")
def test_check_package_exists(mock_run, package_name, expected_result):
    if expected_result:
        mock_run.return_value = MagicMock()
    else:
        mock_run.side_effect = FileNotFoundError

    result = check_package_exists(package_name)
    assert result == expected_result


@patch("subprocess.run")
def test_check_npm_dependency(mock_run):
    mock_run.return_value = MagicMock(stdout="example_package@1.0.0")

    result = check_npm_dependency("example_package", "1.0.0")
    assert result is True

    mock_run.return_value = MagicMock(stdout="")
    result = check_npm_dependency("example_package", "1.0.0")
    assert result is False


@patch("subprocess.run")
def test_check_npm_dependency_npm_not_installed(mock_run):
    mock_run.side_effect = FileNotFoundError

    with pytest.raises(SystemExit) as excinfo:
        check_npm_dependency("example_package", "1.0.0")
    assert str(excinfo.value) == "npm is not installed. Please install Node.js first."


@patch("paig_evaluation.promptfoo_utils.run_command_in_background")
@patch("paig_evaluation.promptfoo_utils.wait_for_process_complete")
def test_install_npm_dependency_success(mock_wait, mock_run_command):
    process_mock = MagicMock(returncode=0)
    mock_run_command.return_value = process_mock

    install_npm_dependency("example_package", "1.0.0")
    mock_run_command.assert_called_with("npm install -g example_package@1.0.0")
    mock_wait.assert_called_with(process_mock, verbose=True)


@patch("paig_evaluation.promptfoo_utils.run_command_in_background")
@patch("paig_evaluation.promptfoo_utils.wait_for_process_complete")
def test_install_npm_dependency_failure(mock_wait, mock_run_command):
    process_mock = MagicMock(returncode=1)
    mock_run_command.return_value = process_mock

    with pytest.raises(SystemExit) as excinfo:
        install_npm_dependency("example_package", "1.0.0")

    assert str(excinfo.value) == "Failed to install npm package."


@patch("paig_evaluation.promptfoo_utils.run_command_in_background", side_effect=Exception("Command failed"))
def test_install_npm_dependency_runtime_error(mock_run_command):
    process_mock = MagicMock(returncode=1)
    mock_run_command.return_value = process_mock

    with pytest.raises(RuntimeError) as excinfo:
        install_npm_dependency("example_package", "1.0.0")

    assert "Error installing npm package" in str(excinfo.value)


@patch("paig_evaluation.promptfoo_utils.check_package_exists")
@patch("paig_evaluation.promptfoo_utils.check_npm_dependency")
@patch("paig_evaluation.promptfoo_utils.install_npm_dependency")
def test_check_and_install_npm_dependency(mock_install, mock_check_dep, mock_check_package):
    # Node and npm are installed, dependency not installed
    mock_check_package.side_effect = [True, True]
    mock_check_dep.return_value = False

    check_and_install_npm_dependency("example_package", "1.0.0")

    mock_check_package.assert_any_call("node")
    mock_check_package.assert_any_call("npm")
    mock_check_dep.assert_called_with("example_package", "1.0.0")
    mock_install.assert_called_with("example_package", "1.0.0")


@patch("paig_evaluation.promptfoo_utils.check_package_exists")
@patch("paig_evaluation.promptfoo_utils.check_npm_dependency")
def test_check_and_install_npm_dependency_already_installed(mock_check_dep, mock_check_package):
    # Node, npm, and dependency already installed
    mock_check_package.side_effect = [True, True]
    mock_check_dep.return_value = True

    check_and_install_npm_dependency("example_package", "1.0.0")

    mock_check_package.assert_any_call("node")
    mock_check_package.assert_any_call("npm")
    mock_check_dep.assert_called_with("example_package", "1.0.0")


@patch("paig_evaluation.promptfoo_utils.check_package_exists")
def test_check_and_install_npm_dependency_node_not_installed(mock_check_package):
    mock_check_package.side_effect = [False]

    with pytest.raises(RuntimeError) as excinfo:
        check_and_install_npm_dependency("example_package", "1.0.0")

    assert str(excinfo.value) == "Node.js is not installed. Please install it first."


@patch("paig_evaluation.promptfoo_utils.check_package_exists")
def test_check_and_install_npm_dependency_npm_not_installed(mock_check_package):
    mock_check_package.side_effect = [True, False]

    with pytest.raises(RuntimeError) as excinfo:
        check_and_install_npm_dependency("example_package", "1.0.0")

    assert str(excinfo.value) == "npm is not installed. Please install Node.js, which includes npm."


@pytest.fixture
def mock_os_functions():
    with patch("os.makedirs") as makedirs_mock, \
         patch("os.path.exists") as exists_mock:
        yield makedirs_mock, exists_mock

@pytest.fixture
def mock_file_handling():
    with patch("builtins.open", mock_open()) as file_mock:
        yield file_mock

@pytest.fixture
def mock_yaml_load_dump():
    with patch("yaml.safe_load", return_value={}) as yaml_load_mock, \
         patch("yaml.dump") as yaml_dump_mock:
        yield yaml_load_mock, yaml_dump_mock

@pytest.mark.parametrize("file_exists", [True, False])
def test_ensure_promptfoo_config_creation_or_update(mock_os_functions, mock_file_handling, mock_yaml_load_dump, file_exists):
    makedirs_mock, exists_mock = mock_os_functions
    file_mock = mock_file_handling
    yaml_load_mock, yaml_dump_mock = mock_yaml_load_dump

    # Mock behaviors
    exists_mock.side_effect = lambda path: file_exists if path.endswith("promptfoo.yaml") else False

    email = "test@example.com"

    # Call the function
    ensure_promptfoo_config(email)

    # Assert directory creation is ensured
    makedirs_mock.assert_called_once_with(os.path.expanduser("~/.promptfoo"), exist_ok=True)

    # Assert file operations
    if file_exists:
        file_mock.assert_any_call(os.path.join(os.path.expanduser("~/.promptfoo"), "promptfoo.yaml"), "r")
        yaml_load_mock.assert_called_once()

    file_mock.assert_any_call(os.path.join(os.path.expanduser("~/.promptfoo"), "promptfoo.yaml"), "w")
    yaml_dump_mock.assert_called_once()

    # Validate YAML content written
    written_data = yaml_dump_mock.call_args[0][0]
    assert written_data["account"]["email"] == email
