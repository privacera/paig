import pytest
from unittest.mock import patch, MagicMock

from paig_common.paig_exception import PAIGException
from paig_common.rbac_manager import RBACManager, check_user_role_permission


@patch('paig_common.rbac_manager.FileUtils.read_json_file')
def test_rbac_manager(mock_load_from_file):
    mock_load_from_file.return_value = [
        {
            "url_endpoint_pattern": "/api/test",
            "is_exclude": False,
            "roles": ["OWNER"],
            "methods": ["GET"]
        }
    ]
    rbac_manager = RBACManager(True)
    assert rbac_manager.rbac_enabled == True
    assert rbac_manager.rbac_permission_mapping_file_path == "rbac_permission_mapping_file_path.json"
    assert rbac_manager.default_url_patterns == ['/api/.*']
    assert rbac_manager.default_roles == ['OWNER']


@patch('paig_common.rbac_manager.RBACManager.get_instance')
def test_check_user_role_permission(mock_get_instance):
    mock_instance = MagicMock()
    mock_instance.rbac_enabled = True
    mock_instance.get_roles_with_permission.return_value = ['OWNER']
    mock_get_instance.return_value = mock_instance

    headers = {'x-user-role': 'OWNER'}
    response = check_user_role_permission('/api/test', 'GET', headers)
    assert response.status_code == 200
    assert 'is authorized' in response.content

    headers = {'x-user-role': 'USER'}
    response = check_user_role_permission('/api/test', 'GET', headers)
    assert response.status_code == 403
    assert 'is not authorized' in response.content

    response = check_user_role_permission('/api/test', 'GET', {})
    assert response.status_code == 400
    assert "Missing 'x-user-role' header" in response.content


@patch('paig_common.rbac_manager.FileUtils.read_json_file')
def test_get_roles_with_permission(mock_load_from_file):
    mock_load_from_file.return_value = [
        {
            "url_endpoint_pattern": "/api/test",
            "is_exclude": False,
            "roles": ["OWNER"],
            "method": ["GET"]
        }
    ]
    rbac_manager = RBACManager(True)
    roles = rbac_manager.get_roles_with_permission('/api/test', 'GET')
    assert roles == ['OWNER']

    roles = rbac_manager.get_roles_with_permission('/api/other', 'GET')
    assert roles == ['OWNER']

    roles = rbac_manager.get_roles_with_permission('/test', 'POST')
    assert roles == []


@patch('paig_common.rbac_manager.FileUtils.read_json_file')
def test_load_permissions_exception(mock_load_from_file):
    mock_load_from_file.side_effect = Exception("File not found")

    with pytest.raises(PAIGException) as e:
        RBACManager(True).load_permissions()
    assert str(e.value) == "Failed to load the permissions json file"

