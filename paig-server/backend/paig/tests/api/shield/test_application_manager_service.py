from unittest.mock import patch, MagicMock
import pytest
import json
from pathlib import Path

from api.shield.model.scanner_result import ScannerResult
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.scanners.BaseScanner import Scanner
from api.shield.services.application_manager_service import ApplicationManager, scan_with_scanner
from api.shield.utils.custom_exceptions import ShieldException

def authorize_req_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return AuthorizeRequest(tenant_id='test_tenant', req_data=req_json, user_role='OWNER')

auth_req = authorize_req_data()

class TestScanner1(Scanner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def scan(self, message: str) -> ScannerResult:
        return ScannerResult(["trait1"], analyzer_result=["result1"])


class TestScanner2(Scanner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def scan(self, message: str) -> ScannerResult:
        return ScannerResult(["trait2"])


@pytest.fixture
def mock_scanners():
    scanner1 = TestScanner1(name='scanner1', request_types=['prompt'], enforce_access_control=True,
                            model_path='model_path',
                            model_score_threshold=0.5, entity_type='entity_type', enable=True)
    scanner2 = TestScanner2(name='scanner2', request_types=['prompt'], enforce_access_control=False,
                            model_path='model_path',
                            model_score_threshold=0.5, entity_type='entity_type', enable=True)
    return [scanner1, scanner2]


@pytest.fixture
def app_manager(mock_scanners):
    manager = ApplicationManager()
    manager.max_workers = 4  # Set max_workers for ThreadPoolExecutor
    with patch.object(manager, 'get_scanners', return_value=mock_scanners):
        yield manager


class TestApplicationManager:

    @patch.object(ApplicationManager, 'load_scanners')
    def test_get_scanners_with_cache_hit(self, mock_load_scanners):
        manager = ApplicationManager()
        manager.application_key_scanners.put('app_key', ['scanner1', 'scanner2'])
        manager.get_scanners('app_key', 'prompt', True, auth_req)
        mock_load_scanners.assert_not_called()

    @patch('api.shield.services.application_manager_service.parse_properties')
    def test_load_scanners(self, mock_parse_properties, mock_scanners):
        mock_parse_properties.return_value = mock_scanners
        manager = ApplicationManager()
        manager.load_scanners('app_key')
        assert manager.get_scanners('app_key', 'prompt', True, auth_req)[0] == mock_scanners[0]
        assert manager.get_scanners('app_key', 'prompt', False, auth_req)[0] == mock_scanners[1]

    @patch('api.shield.services.application_manager_service.parse_properties')
    def test_scan_messages(self, mock_parse_properties):
        scanner1 = MagicMock(name='scanner1', request_types=['prompt'], enforce_access_control=True)
        scanner1.scan.return_value = {'traits': ['trait1', 'trait2']}
        scanner2 = MagicMock(name='scanner2', request_types=['prompt', 'reply'], enforce_access_control=False)
        scanner2.scan.return_value = {'traits': ['trait3', 'trait4']}
        mock_parse_properties.return_value = [scanner1, scanner2]
        manager = ApplicationManager()
        manager.load_scanners('app_key')
        scan_results, scan_timing = manager.scan_messages('message', auth_req, True)
        assert len(scan_results) == 1
        for key, value in scan_results.items():
            assert value == {'traits': ['trait1', 'trait2']}

    def test_scan_with_scanner(self):
        scanner = TestScanner1(name='scanner1', request_types=['prompt'], enforce_access_control=True,
                               model_path='model_path', model_score_threshold=0.5, entity_type='entity_type',
                               enable=True)
        message = "test message"

        # Mock the scan method of the scanner
        with patch.object(scanner, 'scan', return_value={"traits": ["trait1"], "analyzer_result": ["result1"]}):
            scanner_name, result, scan_timings = scan_with_scanner(scanner, message, "tenant_id")

            # Verify the results
            assert scanner_name == "scanner1"
            assert result == {"traits": ["trait1"], "analyzer_result": ["result1"]}


def test_scan_messages_success(app_manager, mock_scanners):
    message = "test message"
    application_key = "test_app_key"

    # Mock the scan method of each scanner to return specific results
    with patch.object(mock_scanners[0], 'scan', return_value=ScannerResult(
            traits=["trait1"],
            analyzer_result=["result1"]
    )), patch.object(mock_scanners[1], 'scan', return_value=ScannerResult(
        traits=[],
        analyzer_result=["result2"]
    )):
        scan_results, scan_timings = app_manager.scan_messages(message, auth_req, True)

    # Verify the results
    assert len(scan_results) == 2
    assert "scanner1" in scan_results
    assert "scanner2" in scan_results
    assert scan_results["scanner1"].get('traits') == ["trait1"]
    assert scan_results["scanner1"].get('analyzer_result') == ["result1"]


def test_scan_messages_with_exception(app_manager, mock_scanners):
    message = "test message"
    application_key = "test_app_key"

    with patch.object(mock_scanners[0], 'scan', side_effect=Exception("Scanner failed")):
        with patch.object(mock_scanners[1], 'scan',
                          return_value=ScannerResult(traits=["trait1"], analyzer_result=["result1"])):
            with pytest.raises(ShieldException) as e:
                scan_results, access_control_traits = app_manager.scan_messages(message, auth_req, True)

                # Verify the results
                assert len(scan_results) == 1  # scanner1 failed, so only one result
                assert "scanner2" in scan_results
                assert access_control_traits == []

    @patch.object(ApplicationManager, 'load_scanners')
    def test_get_scanners_with_cache_miss(self, mock_load_scanners):
        manager = ApplicationManager()  # Create an instance of ApplicationManager
        # Patch the instance attribute after the object has been created
        manager.application_key_scanners = MagicMock()
        manager.application_key_scanners.get.return_value = ['scanner1', 'scanner2']
        manager.get_scanners('app_key', True)
        mock_load_scanners.assert_called_once_with('app_key')
