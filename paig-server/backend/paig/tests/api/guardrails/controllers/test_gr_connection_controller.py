from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.guardrails import GuardrailProvider
from api.guardrails.api_schemas.gr_connection import GRConnectionView, GRConnectionFilter
from api.guardrails.controllers.gr_connection_controller import GRConnectionController
from api.guardrails.services.gr_connections_service import GRConnectionService
from core.controllers.paginated_response import create_pageable_response


@pytest.fixture
def mock_guardrail_connection_service():
    return AsyncMock(spec=GRConnectionService)


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def session_context():
    from contextvars import ContextVar
    session_context = ContextVar("session_context")
    session_context.set("test")
    return session_context


def get_dummy_guardrail_connection_view():
    gr_connection_view_json = {
            "id": 1,
            "status": 1,
            "createTime": "2024-10-29T13:03:27.000000",
            "updateTime": "2024-10-29T13:03:27.000000",
            "name": "gr_connection_1",
            "description": "test description1",
            "guardrailsProvider": "AWS",
            "connectionDetails": {
                "access_key": "mock_access_key",
                "secret_key": "mock_secret_key",
                "session_token": "mock_session_token"
            }
        }
    return GRConnectionView(**gr_connection_view_json)


@pytest.mark.asyncio
async def test_list_guardrail_connections(mock_guardrail_connection_service, mock_session):
    # Mock filter and parameters
    filter = GRConnectionFilter()
    page_number = 1
    size = 10
    sort = ["id"]

    # Mock return value from service
    mock_pageable = create_pageable_response(
        content=[get_dummy_guardrail_connection_view()],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )
    mock_guardrail_connection_service.list.return_value = mock_pageable

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    # Call the method under test
    result = await controller.list(filter, page_number, size, sort)

    # Assertions
    assert result == mock_pageable
    mock_guardrail_connection_service.list.assert_called_once_with(filter=filter, page_number=page_number, size=size, sort=sort)


@pytest.mark.asyncio
async def test_list_guardrail_connection_provider_names(mock_guardrail_connection_service, mock_session):
    # Mock return value from service
    expected_result = ["AWS", "Azure"]
    mock_guardrail_connection_service.list_connection_provider_names.return_value = expected_result

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    # Call the method under test
    result = await controller.list_connection_provider_names()

    # Assertions
    assert result == expected_result
    mock_guardrail_connection_service.list_connection_provider_names.assert_called_once()


@pytest.mark.asyncio
async def test_create_guardrail_connection(mock_guardrail_connection_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_guardrail_connection_view = get_dummy_guardrail_connection_view()
    mock_guardrail_connection_service.create.return_value = mock_guardrail_connection_view
    mock_session.commit.return_value = None

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    # Call the method under test
    result = await controller.create(mock_guardrail_connection_view)

    # Assertions
    assert result == mock_guardrail_connection_view
    mock_guardrail_connection_service.create.assert_called_once_with(mock_guardrail_connection_view)


@pytest.mark.asyncio
async def test_get_guardrail_connection_by_id(mock_guardrail_connection_service):
    # Mock return value from service
    mock_guardrail_connection_view = get_dummy_guardrail_connection_view()
    mock_guardrail_connection_service.get_by_id.return_value = mock_guardrail_connection_view

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    # Call the method under test
    result = await controller.get_by_id(id=1)

    # Assertions
    assert result == mock_guardrail_connection_view
    mock_guardrail_connection_service.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_update_guardrail_connection(mock_guardrail_connection_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_guardrail_connection_view = get_dummy_guardrail_connection_view()
    mock_guardrail_connection_service.update.return_value = mock_guardrail_connection_view

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    # Call the method under test
    result = await controller.update(id=1, request=mock_guardrail_connection_view)

    # Assertions
    assert result == mock_guardrail_connection_view
    mock_guardrail_connection_service.update.assert_called_once_with(1, mock_guardrail_connection_view)


@pytest.mark.asyncio
async def test_delete_guardrail_connection(mock_guardrail_connection_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_guardrail_connection_service.delete.return_value = None

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    # Call the method under test
    await controller.delete(id=1)

    # Assertions
    mock_guardrail_connection_service.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_test_guardrail_connection(mock_guardrail_connection_service):
    # Mock return value from service
    mock_guardrail_connection_service.test_connection.return_value = True

    # Create instance of controller
    controller = GRConnectionController(gr_connection_service=mock_guardrail_connection_service)

    request = GRConnectionView(
        name="test_connection",
        description="Test description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"key": "value"}
    )

    # Call the method under test
    result = await controller.test_connection(request)

    # Assertions
    assert result is True
    mock_guardrail_connection_service.test_connection.assert_called_once_with(request)
