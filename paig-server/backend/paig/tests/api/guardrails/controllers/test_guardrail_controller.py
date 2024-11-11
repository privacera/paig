from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.guardrails.api_schemas.guardrail import GuardrailFilter, GuardrailView
from api.guardrails.controllers.guardrail_controller import GuardrailController
from api.guardrails.services.guardrails_service import GuardrailService
from core.controllers.paginated_response import create_pageable_response


@pytest.fixture
def mock_guardrail_service():
    return AsyncMock(spec=GuardrailService)


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def session_context():
    from contextvars import ContextVar
    session_context = ContextVar("session_context")
    session_context.set("test")
    return session_context


def get_dummy_guardrail_view():
    guardrail_view_json = {
            "id": 1,
            "status": 1,
            "createTime": "2024-10-29T13:03:27.000000",
            "updateTime": "2024-10-29T13:03:27.000000",
            "name": "mock_guardrail",
            "description": "mock description",
            "version": 1
        }
    return GuardrailView(**guardrail_view_json)


@pytest.mark.asyncio
async def test_list_guardrail(mock_guardrail_service, mock_session):
    # Mock filter and parameters
    filter = GuardrailFilter()
    page_number = 1
    size = 10
    sort = ["id"]

    # Mock return value from service
    mock_pageable = create_pageable_response(
        content=[get_dummy_guardrail_view()],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )
    mock_guardrail_service.list.return_value = mock_pageable

    # Create instance of controller
    controller = GuardrailController(guardrail_service=mock_guardrail_service)

    # Call the method under test
    result = await controller.list(filter, page_number, size, sort)

    # Assertions
    assert result == mock_pageable
    mock_guardrail_service.list.assert_called_once_with(filter=filter, page_number=page_number, size=size, sort=sort)


@pytest.mark.asyncio
async def test_create_guardrail(mock_guardrail_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_guardrail_view = get_dummy_guardrail_view()
    mock_guardrail_service.create.return_value = mock_guardrail_view
    mock_session.commit.return_value = None

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = GuardrailController(guardrail_service=mock_guardrail_service)

    # Call the method under test
    result = await controller.create(mock_guardrail_view)

    # Assertions
    assert result == mock_guardrail_view
    mock_guardrail_service.create.assert_called_once_with(mock_guardrail_view)


@pytest.mark.asyncio
async def test_get_guardrail_by_id(mock_guardrail_service):
    # Mock return value from service
    mock_guardrail_view = get_dummy_guardrail_view()
    mock_guardrail_service.get_by_id.return_value = mock_guardrail_view

    # Create instance of controller
    controller = GuardrailController(guardrail_service=mock_guardrail_service)

    # Call the method under test
    result = await controller.get_by_id(id=1)

    # Assertions
    assert result == mock_guardrail_view
    mock_guardrail_service.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_update_guardrail(mock_guardrail_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_guardrail_view = get_dummy_guardrail_view()
    mock_guardrail_service.update.return_value = mock_guardrail_view

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = GuardrailController(guardrail_service=mock_guardrail_service)

    # Call the method under test
    result = await controller.update(id=1, request=mock_guardrail_view)

    # Assertions
    assert result == mock_guardrail_view
    mock_guardrail_service.update.assert_called_once_with(1, mock_guardrail_view)


@pytest.mark.asyncio
async def test_delete_guardrail(mock_guardrail_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_guardrail_service.delete.return_value = None

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = GuardrailController(guardrail_service=mock_guardrail_service)

    # Call the method under test
    await controller.delete(id=1)

    # Assertions
    mock_guardrail_service.delete.assert_called_once_with(1)

