from unittest.mock import patch, MagicMock
import pytest

from api.shield.scanners.BaseScanner import Scanner
from api.shield.services.application_manager_service import ApplicationManager, scan_with_scanner
from api.shield.utils.custom_exceptions import ShieldException


@pytest.fixture
def mock_scanners():
    scanner1 = Scanner('scanner1', ['prompt'], True, 'model_path', 0.5, 'entity_type', True)
    scanner2 = Scanner('scanner2', ['prompt'], False, 'model_path', 0.5, 'entity_type', True)
    return [scanner1, scanner2]


@pytest.fixture
def app_manager(mock_scanners):
    manager = ApplicationManager()
    manager.max_workers = 4  # Set max_workers for ThreadPoolExecutor
    with patch.object(manager, 'get_scanners', return_value=mock_scanners):
        yield manager


class TestApplicationManager:

    @patch('api.shield.services.application_manager_service.parse_properties')
    @patch.object(ApplicationManager, 'load_scanners')
    def test_get_scanners_with_cache_miss(self, mock_load_scanners, mock_parse_properties):
        mock_parse_properties.return_value = ['scanner1', 'scanner2']
        manager = ApplicationManager()
        manager.get_scanners('app_key')
        mock_load_scanners.assert_called_once_with('app_key')

    @patch('api.shield.services.application_manager_service.parse_properties')
    @patch.object(ApplicationManager, 'load_scanners')
    def test_get_scanners_with_cache_hit(self, mock_load_scanners, mock_parse_properties):
        mock_parse_properties.return_value = ['scanner1', 'scanner2']
        manager = ApplicationManager()
        manager.application_key_scanners.put('app_key', ['scanner1', 'scanner2'])
        manager.get_scanners('app_key')
        mock_load_scanners.assert_not_called()

    @patch('api.shield.services.application_manager_service.parse_properties')
    def test_load_scanners(self, mock_parse_properties):
        mock_parse_properties.return_value = ['scanner1', 'scanner2']
        manager = ApplicationManager()
        manager.load_scanners('app_key')
        assert manager.get_scanners('app_key') == ['scanner1', 'scanner2']

    @patch('api.shield.services.application_manager_service.parse_properties')
    def test_scan_messages(self, mock_parse_properties):
        scanner1 = MagicMock(name='scanner1', enforce_access_control=True)
        scanner1.scan.return_value = {'traits': ['trait1', 'trait2']}
        scanner2 = MagicMock(name='scanner2', enforce_access_control=False)
        scanner2.scan.return_value = {'traits': ['trait3', 'trait4']}
        mock_parse_properties.return_value = [scanner1, scanner2]
        manager = ApplicationManager()
        manager.load_scanners('app_key')
        scan_results, access_control_traits, scan_timing = manager.scan_messages('app_key', 'message')
        assert len(scan_results) == 2
        assert access_control_traits == ['trait1', 'trait2']

    def test_scan_with_scanner(self):
        scanner = Scanner('scanner1', ['prompt'], True, 'model_path', 0.5, 'entity_type', True)
        message = "test message"

        # Mock the scan method of the scanner
        with patch.object(scanner, 'scan', return_value={"traits": ["trait1"], "analyzer_result": ["result1"]}):
            scanner_name, result, scan_timings = scan_with_scanner(scanner, message)

            # Verify the results
            assert scanner_name == "scanner1"
            assert result == {"traits": ["trait1"], "analyzer_result": ["result1"]}


def test_scan_messages_success(app_manager, mock_scanners):
    message = "test message"
    application_key = "test_app_key"

    # Mock the scan method of each scanner to return specific results
    with patch.object(mock_scanners[0], 'scan', return_value={
        "traits": ["trait1"],
        "analyzer_result": ["result1"]
    }), patch.object(mock_scanners[1], 'scan', return_value={
        "traits": [],
        "analyzer_result": ["result2"]
    }):
        scan_results, access_control_traits, scan_timings = app_manager.scan_messages(application_key, message)

    # Verify the results
    assert len(scan_results) == 2
    assert "scanner1" in scan_results
    assert "scanner2" in scan_results
    assert access_control_traits == ["trait1"]


def test_scan_messages_with_exception(app_manager, mock_scanners):
    message = "test message"
    application_key = "test_app_key"

    with patch.object(mock_scanners[0], 'scan', side_effect=Exception("Scanner failed")):
        with patch.object(mock_scanners[1], 'scan', return_value={"traits": [], "analyzer_result": ["result1"]}):
            with pytest.raises(ShieldException) as e:
                scan_results, access_control_traits = app_manager.scan_messages(application_key, message)

                # Verify the results
                assert len(scan_results) == 1  # scanner1 failed, so only one result
                assert "scanner2" in scan_results
                assert access_control_traits == []
