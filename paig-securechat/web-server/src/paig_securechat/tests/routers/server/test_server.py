import pytest
from httpx import AsyncClient
from unittest.mock import patch

from core.constants import BASE_ROUTE

@pytest.mark.asyncio
async def test_get_server_info(client: AsyncClient):
    url = f"{BASE_ROUTE}/server/config"
    response = await client.get(url)
    assert response.status_code == 200
    assert len(response.json().keys()) > 0


@pytest.mark.asyncio
async def test_get_server_health(client: AsyncClient):
    mock_result = {
            "Server": "SecureChat",
            "Time": "2021-09-30 15:30:00",
            "Version": "1.0.0",
            "Status": "Healthy",
            "Reason": "",
            "Details": [{"Service": "Database", "Status": "Healthy", "Reason": ""}, {"Service": "OpenSearch", "Status": "Healthy", "Reason": ""}]
        }
    with patch('core.factory.controller_initiator.HealthController', autospec=True) as MockHealthController:
        health_controller_instance = MockHealthController.return_value
        health_controller_instance.get_health_check.return_value = mock_result
        url = f"{BASE_ROUTE}/server/health"
        response = await client.get(url)
        assert response.status_code == 200
        assert response.json() == mock_result



@pytest.mark.asyncio
async def test_get_server_health_db_down(client: AsyncClient):
    mock_result = {
            "Server": "SecureChat",
            "Time": "2021-09-30 15:30:00",
            "Version": "1.0.0",
            "Status": "Unhealthy",
            "Reason": "Database is Down",
            "Details": [{"Service": "Database", "Status": "Unhealthy", "Reason": "Database is Down"},
                        {"Service": "OpenSearch", "Status": "Healthy", "Reason": ""}]
        }
    with patch('core.factory.controller_initiator.HealthController', autospec=True) as MockHealthController:
        health_controller_instance = MockHealthController.return_value
        health_controller_instance.get_health_check.return_value = mock_result
        url = f"{BASE_ROUTE}/server/health"
        response = await client.get(url)
        assert response.status_code == 200
        assert response.json() == mock_result


@pytest.mark.asyncio
async def test_get_server_health_opensearch_unhealthy(client: AsyncClient):
    mock_result = {
            "Server": "SecureChat",
            "Time": "2021-09-30 15:30:00",
            "Version": "1.0.0",
            "Status": "Unhealthy",
            "Reason": "Opensearch Connection Error",
            "Details": [{"Service": "Database", "Status": "Healthy", "Reason": ""},
                        {"Service": "OpenSearch", "Status": "Unhealthy",
                         "Reason": "Opensearch service is down due to reason:: Failed to connect the opensearch cluster"}
            ]
        }
    with patch('core.factory.controller_initiator.HealthController', autospec=True) as MockHealthController:
        health_controller_instance = MockHealthController.return_value
        health_controller_instance.get_health_check.return_value = mock_result
        url = f"{BASE_ROUTE}/server/health"
        response = await client.get(url)
        assert response.status_code == 200
        assert response.json() == mock_result
