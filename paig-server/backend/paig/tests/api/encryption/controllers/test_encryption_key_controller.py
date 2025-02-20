import sys

import pytest
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from api.encryption.api_schemas.encryption_key import EncryptionKeyFilter, EncryptionKeyView
from api.encryption.controllers.encryption_key_controller import EncryptionKeyController
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType, EncryptionKeyStatus
from api.encryption.services.encryption_key_service import EncryptionKeyService
from core.controllers.paginated_response import create_pageable_response


@pytest.fixture
def mock_encryption_key_service():
    return AsyncMock(spec=EncryptionKeyService)


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def session_context():
    from contextvars import ContextVar
    session_context = ContextVar("session_context")
    session_context.set("test")
    return session_context


def get_dummy_encryption_key_view():
    return EncryptionKeyView(
        id=1,
        status=1,
        create_time="2021-01-01T00:00:00Z",
        update_time="2021-01-01T00:00:00Z",
        public_key="public_key",
        private_key="private_key",
        key_status=EncryptionKeyStatus.ACTIVE,
        key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)


@pytest.mark.asyncio
async def test_list_encryption_keys(mock_encryption_key_service, mock_session):
    # Mock filter and parameters
    filter = EncryptionKeyFilter(key_status=EncryptionKeyStatus.ACTIVE.value)
    page_number = 1
    size = 10
    sort = ["id"]

    # Mock return value from service
    mock_pageable = create_pageable_response(
        content=[get_dummy_encryption_key_view()],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )
    mock_encryption_key_service.list_encryption_keys.return_value = mock_pageable

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    result = await controller.list_encryption_keys(filter, page_number, size, sort)

    # Assertions
    assert result == mock_pageable
    mock_encryption_key_service.list_encryption_keys.assert_called_once_with(filter, page_number, size, sort)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Test requires Python 3.11 or higher")
@pytest.mark.asyncio
async def test_create_encryption_key(mock_encryption_key_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_encryption_key_view = get_dummy_encryption_key_view()
    mock_encryption_key_service.create_encryption_key.return_value = mock_encryption_key_view

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    result = await controller.create_encryption_key(key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)

    # Assertions
    assert result == mock_encryption_key_view
    mock_encryption_key_service.create_encryption_key.assert_called_once_with(EncryptionKeyType.MSG_PROTECT_SHIELD)


@pytest.mark.asyncio
async def test_get_public_encryption_key_by_id(mock_encryption_key_service):
    # Mock return value from service
    mock_encryption_key_view = EncryptionKeyView(id=1, key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)
    mock_encryption_key_service.get_public_encryption_key_by_id.return_value = mock_encryption_key_view

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    result = await controller.get_public_encryption_key_by_id(id=1)

    # Assertions
    assert result == mock_encryption_key_view
    mock_encryption_key_service.get_public_encryption_key_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_encryption_key_by_id(mock_encryption_key_service):
    # Mock return value from service
    mock_encryption_key_view = EncryptionKeyView(id=1, key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)
    mock_encryption_key_service.get_encryption_key_by_id.return_value = mock_encryption_key_view

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    result = await controller.get_encryption_key_by_id(id=1)

    # Assertions
    assert result == mock_encryption_key_view
    mock_encryption_key_service.get_encryption_key_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_active_encryption_key_by_type(mock_encryption_key_service):
    # Mock return value from service
    mock_encryption_key_view = EncryptionKeyView(id=1, key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)
    mock_encryption_key_service.get_active_encryption_key_by_type.return_value = mock_encryption_key_view

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    result = await controller.get_active_encryption_key_by_type(key_type=EncryptionKeyType.MSG_PROTECT_SHIELD)

    # Assertions
    assert result == mock_encryption_key_view
    mock_encryption_key_service.get_active_encryption_key_by_type.assert_called_once_with(
        EncryptionKeyType.MSG_PROTECT_SHIELD)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Test requires Python 3.11 or higher")
@pytest.mark.asyncio
async def test_delete_disabled_encryption_key(mock_encryption_key_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_encryption_key_service.delete_disabled_encryption_key.return_value = None

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    await controller.delete_disabled_encryption_key(id=1)

    # Assertions
    mock_encryption_key_service.delete_disabled_encryption_key.assert_called_once_with(1)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Test requires Python 3.11 or higher")
@pytest.mark.asyncio
async def test_disable_passive_encryption_key(mock_encryption_key_service, mock_session, session_context, mocker):
    # Mock return value from service
    mock_encryption_key_service.disable_passive_encryption_key.return_value = None

    mocker.patch("core.db_session.session", mock_session)
    mocker.patch("core.db_session.session.session_context", session_context)

    # Create instance of controller
    controller = EncryptionKeyController(encryption_key_service=mock_encryption_key_service)

    # Call the method under test
    await controller.disable_passive_encryption_key(id=1)

    # Assertions
    mock_encryption_key_service.disable_passive_encryption_key.assert_called_once_with(1)
