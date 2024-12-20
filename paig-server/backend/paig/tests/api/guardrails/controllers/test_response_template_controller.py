import pytest
from unittest.mock import AsyncMock, create_autospec

from sqlalchemy.ext.asyncio import AsyncSession

from api.guardrails.api_schemas.response_template import ResponseTemplateView, ResponseTemplateFilter
from api.guardrails.services.response_template_service import ResponseTemplateService
from core.controllers.paginated_response import Pageable, create_pageable_response
from api.guardrails.controllers.response_template_controller import ResponseTemplateController


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
def mock_response_template_service():
    """Fixture to create a mock for ResponseTemplateService."""
    return AsyncMock(spec=ResponseTemplateService)


@pytest.fixture
def controller(mock_response_template_service):
    """Fixture to create an instance of ResponseTemplateController with a mocked service."""
    return ResponseTemplateController(response_template_service=mock_response_template_service)


@pytest.mark.asyncio
async def test_list_response_templates(controller, mock_response_template_service, mock_session, session_context, mocker):
    """Test listing response templates."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_filter = ResponseTemplateFilter()  # Adjust with actual filter fields as needed
    mock_pageable = create_pageable_response(
        content=[],
        total_elements=0,
        page_number=1,
        size=10,
        sort=["id"]
    )
    mock_response_template_service.list_response_templates.return_value = mock_pageable

    result = await controller.list_response_templates(mock_filter, page_number=1, size=10, sort=["id"])

    mock_response_template_service.list_response_templates.assert_awaited_once_with(
        filter=mock_filter, page_number=1, size=10, sort=["id"]
    )
    assert result == mock_pageable


@pytest.mark.asyncio
async def test_create_response_template(controller, mock_response_template_service, mock_session, session_context, mocker):
    """Test creating a response template."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_request = ResponseTemplateView(name="Test Template", content="Sample Content")
    mock_response = ResponseTemplateView(id=1, name="Test Template", content="Sample Content")
    mock_response_template_service.create_response_template.return_value = mock_response

    result = await controller.create_response_template(mock_request)

    mock_response_template_service.create_response_template.assert_awaited_once_with(mock_request)
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_response_template_by_id(controller, mock_response_template_service, mock_session, session_context, mocker):
    """Test retrieving a response template by ID."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_response = ResponseTemplateView(id=1, name="Test Template", content="Sample Content")
    mock_response_template_service.get_response_template_by_id.return_value = mock_response

    result = await controller.get_response_template_by_id(1)

    mock_response_template_service.get_response_template_by_id.assert_awaited_once_with(1)
    assert result == mock_response


@pytest.mark.asyncio
async def test_update_response_template(controller, mock_response_template_service, mock_session, session_context, mocker):
    """Test updating a response template."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_request = ResponseTemplateView(name="Updated Template", content="Updated Content")
    mock_response = ResponseTemplateView(id=1, name="Updated Template", content="Updated Content")
    mock_response_template_service.update_response_template.return_value = mock_response

    result = await controller.update_response_template(1, mock_request)

    mock_response_template_service.update_response_template.assert_awaited_once_with(1, mock_request)
    assert result == mock_response


@pytest.mark.asyncio
async def test_delete_response_template(controller, mock_response_template_service, mock_session, session_context, mocker):
    """Test deleting a response template."""
    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    mock_response_template_service.get_response_template_by_id.return_value = ResponseTemplateView(id=1)
    mock_response_template_service.delete_response_template.return_value = None

    await controller.delete_response_template(1)

    mock_response_template_service.get_response_template_by_id.assert_awaited_once_with(1)
    mock_response_template_service.delete_response_template.assert_awaited_once_with(1)
