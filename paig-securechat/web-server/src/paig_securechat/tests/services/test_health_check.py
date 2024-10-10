from unittest.mock import AsyncMock
from services.health_check import get_db_health_check, get_opensearch_health_check
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.controllers.health_check import HealthController, HEALTHY, UNHEALTHY, REASON, STATUS
from vectordb.vector_utils import opensearch_indexes




@pytest.mark.asyncio
async def test_get_db_health_check_success():
    mock_session = AsyncMock()
    mock_session.execute.return_value.scalar.return_value = 1
    result = await get_db_health_check(mock_session)
    assert result == (True, "")

@pytest.mark.asyncio
async def test_get_db_health_check_failure():
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("Database error")
    result = await get_db_health_check(mock_session)
    assert result == (False, "Database service is down due to reason:: Database error")


@pytest.mark.asyncio
async def test_opensearch_health_check_success():
    config = {
        "opensearch": {
            "user": "username",
            "password": "password",
            "domain_name": "example_domain",
            "region": "us-west-2",
            "hosts": ["host1", "host2"]
        }
    }

    opensearch_indexes.append("index1")

    with patch('services.health_check.get_secret', return_value="mocked_password"), \
            patch('services.health_check.get_opensearch_endpoint', return_value=["mocked_host1", "mocked_host2"]), \
            patch('services.health_check.get_opensearch_cluster_client',
                  return_value=MagicMock(cluster=MagicMock(health=MagicMock(return_value={'status': 'green'})))):
        result, message = await get_opensearch_health_check(config)
        opensearch_indexes.pop()
        assert result is True



@pytest.mark.asyncio
async def test_opensearch_health_check_missing_config():
    config = {}
    opensearch_indexes.append("index1")
    with patch('services.health_check.get_secret', return_value="mocked_password"), \
            patch('services.health_check.get_opensearch_endpoint', return_value=["mocked_host1", "mocked_host2"]), \
            patch('services.health_check.get_opensearch_cluster_client',
                  return_value=MagicMock(cluster=MagicMock(health=MagicMock(return_value={'status': 'green'})))):
        result, message = await get_opensearch_health_check(config)
        opensearch_indexes.pop()
        assert result is False


class TestHealthController:
    @pytest.fixture
    def db_session(self):
        return Mock()

    @pytest.fixture
    def health_controller(self, db_session):
        return HealthController(db_session)

    @pytest.mark.asyncio
    async def test_get_health_check_healthy(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(True, '')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == HEALTHY
                assert result[REASON] == ''

    @pytest.mark.asyncio
    async def test_get_health_check_unhealthy_db(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(False, 'Database connection failed')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(True, '')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == UNHEALTHY

    @pytest.mark.asyncio
    async def test_get_health_check_unhealthy_opensearch(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(False, 'OpenSearch connection failed')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == UNHEALTHY

    @pytest.mark.asyncio
    async def test_get_health_check_unhealthy_both(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(False, 'Database connection failed')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(False, 'OpenSearch connection failed')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == UNHEALTHY

    @pytest.mark.asyncio
    async def test_get_health_check_opensearch_none(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(None, '')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == HEALTHY
                assert result[REASON] == ''

    @pytest.mark.asyncio
    async def test_get_health_check_opensearch_reason_empty_string(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(False, '')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == UNHEALTHY

    @pytest.mark.asyncio
    async def test_get_health_check_opensearch_reason(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(False, 'Authentication error')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == UNHEALTHY


    @pytest.mark.asyncio
    async def test_get_health_check_opensearch_status_none_reason_none(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(None, None)):
                result = await health_controller.get_health_check()
                assert result[STATUS] == HEALTHY
                assert result[REASON] == ''

    @pytest.mark.asyncio
    async def test_get_health_check_opensearch_status_true_reason_empty_string(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(True, '')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == HEALTHY
                assert result[REASON] == ''

    @pytest.mark.asyncio
    async def test_get_health_check_opensearch_status_false_reason_empty_string(self, health_controller):
        with patch('app.controllers.health_check.get_db_health_check', return_value=(True, '')):
            with patch('app.controllers.health_check.get_opensearch_health_check', return_value=(False, '')):
                result = await health_controller.get_health_check()
                assert result[STATUS] == UNHEALTHY