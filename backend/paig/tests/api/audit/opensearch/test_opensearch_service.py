import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from api.audit.api_schemas.access_audit_schema import IncludeQueryParams
from opensearchpy.exceptions import NotFoundError

@pytest.fixture
def mock_opensearch_client():
    with patch('api.audit.opensearch_service.opensearch_client.OpenSearchClient') as mock_client:
        mock_instance = mock_client.return_value
        yield mock_instance


@pytest.fixture
def opensearch_service(mock_opensearch_client):
    from api.audit.opensearch_service.opensearch_service import OpenSearchService
    return OpenSearchService(opensearch_client=mock_opensearch_client)


@pytest.mark.asyncio
async def test_create_access_audit(opensearch_service, mock_opensearch_client):
    access_audit_params = {"param1": "value1"}  # Replace with actual parameters
    with patch('api.audit.opensearch_service.opensearch_client.OpenSearchClient') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.get_client().index.return_value = {"result": "created"}
        mock_instance.get_client().get_index_name = 'your_index_name'
        await opensearch_service.create_access_audit(access_audit_params)

        mock_opensearch_client.get_client().index.assert_called_once()


@pytest.mark.asyncio
async def test_get_access_audits(opensearch_service, mock_opensearch_client):
    include_query = IncludeQueryParams()
    exclude_query = IncludeQueryParams()
    page = 0
    size = 10
    sort = []
    from_time = None
    to_time = None

    mock_opensearch_client.get_client().search.return_value={
        'hits': {
            'hits': [{'_source': {'param1': 'value1'}}],
            'total': {'value': 1}
        }
    }

    response = await opensearch_service.get_access_audits(include_query, exclude_query, page, size, sort, from_time,
                                                          to_time)

    response = response.model_dump()
    assert len(response['content']) == 1
    assert response['content'][0]['param1'] == 'value1'


@pytest.mark.asyncio
async def test_insert_access_audit(opensearch_service, mock_opensearch_client):
    access_audit_params = {"param1": "value1"}  # Replace with actual parameters
    mock_opensearch_client.get_client().index.return_value={"result": "created"}

    await opensearch_service.create_access_audit(access_audit_params)

    mock_opensearch_client.get_client().index.assert_called_once()


@pytest.mark.asyncio
async def test_get_counts(opensearch_service, mock_opensearch_client):
    group_by = "result"
    include_query = IncludeQueryParams()
    from_time = None
    to_time = None
    interval = None
    size = None
    cardinality = None

    mock_opensearch_client.get_client().search.return_value={
        'aggregations': {
            'count': {'value': 5}
        }
    }

    result = opensearch_service.get_counts(group_by, include_query, from_time, to_time, interval, size,
                                                 cardinality, False)
    assert result['count']['count'] == 5


@pytest.mark.asyncio
async def test_get_audits_raises_not_found(opensearch_service, mock_opensearch_client):
    include_query = IncludeQueryParams()
    exclude_query = IncludeQueryParams()
    page = 0
    size = 10
    sort = []
    from_time = None
    to_time = None

    mock_opensearch_client.get_client().search.side_effect=NotFoundError()

    resp = opensearch_service.get_audits(include_query, exclude_query, page, size, sort, from_time, to_time, None)

    assert resp.model_dump()['content'] == []
