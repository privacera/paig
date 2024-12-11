from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataView, GRSensitiveDataFilter
from api.guardrails.controllers.gr_sensitive_data_controller import GRSensitiveDataController
from api.guardrails.services.gr_sensitive_data_service import GRSensitiveDataService
from core.controllers.paginated_response import Pageable, create_pageable_response


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.commit.return_value = None
    return session


@pytest.fixture
def session_context():
    from contextvars import ContextVar
    session_context = ContextVar("session_context")
    session_context.set("test")
    return session_context


@pytest.fixture
def mock_gr_sensitive_data_service():
    """Fixture to create a mock for GRSensitiveDataService."""
    return AsyncMock(spec=GRSensitiveDataService)


@pytest.fixture
def mock_gov_service_validation_util():
    """Fixture to create a mock for GovServiceValidationUtil."""
    return AsyncMock(spec=GovServiceValidationUtil)


@pytest.fixture
def controller(mock_gr_sensitive_data_service, mock_gov_service_validation_util):
    """Fixture to create an instance of GRSensitiveDataController with mocked services."""
    return GRSensitiveDataController(
        gr_sensitive_data_service=mock_gr_sensitive_data_service,
        gov_service_validation_util=mock_gov_service_validation_util
    )


@pytest.mark.asyncio
async def test_list_gr_sensitive_datas(controller, mock_gr_sensitive_data_service, mock_session, session_context, mocker):
    """Test listing Guardrail Sensitive Data."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_filter = GRSensitiveDataFilter()  # Adjust with actual filter fields as needed
    mock_pageable = create_pageable_response(
        content=[],
        total_elements=0,
        page_number=1,
        size=10,
        sort=["id"]
    )
    mock_gr_sensitive_data_service.list_gr_sensitive_datas.return_value = mock_pageable

    result = await controller.list_gr_sensitive_datas(mock_filter, page_number=1, size=10, sort=["id"])

    mock_gr_sensitive_data_service.list_gr_sensitive_datas.assert_awaited_once_with(
        filter=mock_filter, page_number=1, size=10, sort=["id"]
    )
    assert result == mock_pageable


@pytest.mark.asyncio
async def test_create_gr_sensitive_data(controller, mock_gr_sensitive_data_service, mock_session, session_context, mocker):
    """Test creating a new Guardrail Sensitive Data."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_request = GRSensitiveDataView(id=None, name="Sensitive Data", description="Sensitive data description")
    mock_response = GRSensitiveDataView(id=1, name="Sensitive Data", description="Sensitive data description")
    mock_gr_sensitive_data_service.create_gr_sensitive_data.return_value = mock_response

    result = await controller.create_gr_sensitive_data(mock_request)

    mock_gr_sensitive_data_service.create_gr_sensitive_data.assert_awaited_once_with(mock_request)
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_gr_sensitive_data_by_id(controller, mock_gr_sensitive_data_service, mock_session, session_context, mocker):
    """Test retrieving a Guardrail Sensitive Data by ID."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_response = GRSensitiveDataView(id=1, name="Sensitive Data", description="Sensitive data description")
    mock_gr_sensitive_data_service.get_gr_sensitive_data_by_id.return_value = mock_response

    result = await controller.get_gr_sensitive_data_by_id(1)

    mock_gr_sensitive_data_service.get_gr_sensitive_data_by_id.assert_awaited_once_with(1)
    assert result == mock_response


@pytest.mark.asyncio
async def test_update_gr_sensitive_data(controller, mock_gr_sensitive_data_service, mock_session, session_context, mocker):
    """Test updating an existing Guardrail Sensitive Data."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_request = GRSensitiveDataView(id=None, name="Updated Sensitive Data", description="Updated description")
    mock_response = GRSensitiveDataView(id=1, name="Updated Sensitive Data", description="Updated description")
    mock_gr_sensitive_data_service.update_gr_sensitive_data.return_value = mock_response

    result = await controller.update_gr_sensitive_data(1, mock_request)

    mock_gr_sensitive_data_service.update_gr_sensitive_data.assert_awaited_once_with(1, mock_request)
    assert result == mock_response


@pytest.mark.asyncio
async def test_delete_gr_sensitive_data(controller, mock_gr_sensitive_data_service, mock_session, session_context, mocker):
    """Test deleting a Guardrail Sensitive Data."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_gr_sensitive_data_service.get_gr_sensitive_data_by_id.return_value = GRSensitiveDataView(id=1)
    mock_gr_sensitive_data_service.delete_gr_sensitive_data.return_value = None

    await controller.delete_gr_sensitive_data(1)

    mock_gr_sensitive_data_service.delete_gr_sensitive_data.assert_awaited_once_with(1)
