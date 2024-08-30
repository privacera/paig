import pytest
from api.audit.opensearch_service.opensearch_client import OpenSearchClient, get_opensearch_client
from api.audit.opensearch_service import opensearch_client
from unittest.mock import patch, MagicMock, mock_open
import json, os

@pytest.fixture
def modify_global_variable():
    original_value = opensearch_client.Config
    opensearch_client.Config = {
        'opensearch': {
            'endpoint': 'localhost:port',
            'username': 'user',
            'secret': 'password',
            'access_audit_index': 'test_access_audit',
            'admin_audit_index': 'test_admin_audit',
        }
    }  # Change the global variable for the test
    yield
    opensearch_client.Config = original_value

@pytest.fixture
def mock_opensearch_client():
    with patch('api.audit.opensearch_service.opensearch_client.OpenSearch') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


def test_opensearch_client_initialization(modify_global_variable, mock_opensearch_client):
    client = OpenSearchClient()

    # Use assert instead of assertEqual and assertIsNotNone
    assert client.access_audit_index == 'test_access_audit'
    assert client.admin_audit_index == 'test_admin_audit'
    assert client.opensearch_client is not None


def test_get_index_name(modify_global_variable, mock_opensearch_client):
    client = OpenSearchClient()
    client.admin_audit_index = 'test_admin_audit'
    client.access_audit_index = 'test_access_audit'

    # Use assert instead of assertEqual
    assert client.get_index_name(True) == 'test_admin_audit'
    assert client.get_index_name(False) == 'test_access_audit'



def test_create_index(modify_global_variable, mock_opensearch_client):
    client = OpenSearchClient()
    client.create_index('test_index')

    # Ensure that the create index method was called with the correct parameters
    mock_opensearch_client.indices.create.assert_called_with(index='test_index', ignore=400)


def test_delete_index(modify_global_variable, mock_opensearch_client):
    client = OpenSearchClient()
    client.delete_index('test_index')

    # Ensure that the delete index method was called with the correct parameters
    mock_opensearch_client.indices.delete.assert_called_with(index='test_index', ignore=[400, 404])


def test_check_and_create_template(modify_global_variable, mock_opensearch_client, monkeypatch):
    mock_template_body = {
        "index_patterns": ["test_access_audit"],
        "settings": {
            "number_of_shards": 1
        }
    }

    monkeypatch.setattr("builtins.open", mock_open(read_data=json.dumps(mock_template_body)))
    monkeypatch.setattr(os.path, "exists", lambda x: True)

    client = OpenSearchClient()
    mock_opensearch_client.indices.get_index_template.return_value = None
    client.check_and_create_template('test_template', 'test_template.json', 'test_access_audit')


    # Verify that create_template was called
    mock_opensearch_client.indices.put_index_template.assert_called_once()
    assert mock_opensearch_client.indices.put_index_template.call_args[1]['name'] == 'test_template'




def test_check_and_create_template_when_template_exists(modify_global_variable, mock_opensearch_client, monkeypatch):
    mock_template_body = {
        "index_patterns": ["test_access_audit"],
        "settings": {
            "number_of_shards": 1
        }
    }
    client = OpenSearchClient()
    monkeypatch.setattr("builtins.open", mock_open(read_data=json.dumps(mock_template_body)))
    monkeypatch.setattr(os.path, "exists", lambda x: True)
    # Mock get_template to return a non-None value, simulating that the template exists
    mock_opensearch_client.indices.get_index_template.return_value = {'index_templates': [{'name': 'access_template'}]}

    # Call the method to test
    client.check_and_create_template('access_template', 'test_template.json', 'test_access_audit')

    # Verify that create_template was not called
    mock_opensearch_client.indices.put_index_template.assert_not_called()