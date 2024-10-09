from vectordb.opensearch import (
    check_opensearch_index, create_index, create_index_mapping, delete_opensearch_index,
    put_bulk_in_opensearch, get_opensearch_cluster_client, locate_secret_arn, get_secret, get_opensearch_endpoint
)
from opensearchpy import OpenSearch


def test_check_opensearch_index(mocker):
    mock_opensearch_client = mocker.MagicMock()
    mock_opensearch_client.indices.exists.return_value = True
    assert check_opensearch_index(mock_opensearch_client, "test_index")
    mock_opensearch_client.indices.exists.assert_called_once_with(index="test_index")


def test_create_index(mocker):
    mock_opensearch_client = mocker.MagicMock()
    mock_opensearch_client.indices.create.return_value = {"acknowledged": True}
    assert create_index(mock_opensearch_client, "test_index")
    mock_opensearch_client.indices.create.assert_called_once_with(index="test_index", body={
        "settings": {
            "index": {
                "knn": True,
                "knn.space_type": "cosinesimil"
            }
        }
    })


def test_create_index_mapping(mocker):
    mock_opensearch_client = mocker.MagicMock()
    mock_opensearch_client.indices.put_mapping.return_value = {"acknowledged": True}
    assert create_index_mapping(mock_opensearch_client, "test_index")
    mock_opensearch_client.indices.put_mapping.assert_called_once_with(index="test_index", body={
        "properties": {
            "vector_field": {
                "type": "knn_vector",
                "dimension": 1536
            },
            "text": {
                "type": "keyword"
            }
        }
    })


def test_delete_opensearch_index(mocker):
    mock_opensearch_client = mocker.MagicMock()
    mock_opensearch_client.indices.delete.return_value = {"acknowledged": True}
    assert delete_opensearch_index(mock_opensearch_client, "test_index")
    mock_opensearch_client.indices.delete.assert_called_once_with(index="test_index")


def test_put_bulk_in_opensearch(mocker):
    mock_opensearch_client = mocker.MagicMock()
    mock_bulk = mocker.patch('vectordb.opensearch.bulk')
    mock_bulk.return_value = (True, True)
    assert put_bulk_in_opensearch([], mock_opensearch_client) == (True, True)
    mock_bulk.assert_called_once()


def test_get_opensearch_cluster_client(mocker):
    client = get_opensearch_cluster_client("localhost", "user", "password", "test_index")
    assert isinstance(client, OpenSearch)

import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_client():
    return Mock()


def test_locate_secret_arn(mock_client):
    mock_response = {
        'SecretList': [
            {'ARN': 'arn:aws:secretsmanager:region:account-id:secret:secret-name-1'},
            {'ARN': 'arn:aws:secretsmanager:region:account-id:secret:secret-name-2'}
        ]
    }
    mock_client.list_secrets.return_value = mock_response
    secret_tag_value = "localhost:9200"
    result = locate_secret_arn(secret_tag_value, mock_client)
    assert result == 'arn:aws:secretsmanager:region:account-id:secret:secret-name-1'

    mock_client.list_secrets.assert_called_once_with(
        Filters=[
            {'Key': 'tag-key', 'Values': ['Name']},
            {'Key': 'tag-value', 'Values': [secret_tag_value]}
        ]
    )



@pytest.fixture
def mock_boto3_client():
    with patch('vectordb.opensearch.boto3.client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_locate_secret_arn():
    with patch('vectordb.opensearch.locate_secret_arn') as mock_locate_secret_arn:
        yield mock_locate_secret_arn


def test_get_secret(mock_boto3_client, mock_locate_secret_arn):
    mock_locate_secret_arn.return_value = 'mocked_secret_arn'
    mock_secret_value = {'SecretString': '{"ARN": "arn:aws:secretsmanager:region:account-id:secret:secret-name-1"}'}
    mock_boto3_client.return_value.get_secret_value.return_value = mock_secret_value
    result = get_secret('opensearch', 'us-west-2')

    assert result == '{"ARN": "arn:aws:secretsmanager:region:account-id:secret:secret-name-1"}'

    mock_boto3_client.assert_called_once_with('secretsmanager', region_name='us-west-2')
    mock_locate_secret_arn.assert_called_once_with('opensearch', mock_boto3_client.return_value)
    mock_boto3_client.return_value.get_secret_value.assert_called_once_with(SecretId='mocked_secret_arn')


def test_get_opensearch_endpoint(mock_boto3_client):
    mock_response = {
        'DomainStatus': {
            'Endpoints': {'vpc': 'mocked_endpoint'}
        }
    }
    mock_boto3_client.return_value.describe_elasticsearch_domain.return_value = mock_response
    result = get_opensearch_endpoint('opensearch-domain', 'us-west-2')

    assert result == 'mocked_endpoint'

    mock_boto3_client.assert_called_once_with('es', region_name='us-west-2')
    mock_boto3_client.return_value.describe_elasticsearch_domain.assert_called_once_with(
        DomainName='opensearch-domain'
    )