import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from api.apikey.controllers.paig_api_key_controller import PaigApiKeyController
from core.exceptions import NotFoundException


@pytest.fixture
def controller():
    return PaigApiKeyController()


@pytest.mark.asyncio
@patch("api.apikey.controllers.paig_api_key_controller.PaigApiKeyService")
@patch("api.apikey.controllers.paig_api_key_controller.create_pageable_response")
async def test_get_api_keys_by_application_id_with_filters_success(mock_response, mock_service):
    mock_instance = mock_service.return_value
    mock_result = MagicMock()
    mock_result.to_ui_dict.return_value = {"mocked": "result"}
    mock_instance.get_api_keys_by_application_id = AsyncMock(return_value=([mock_result], 1))

    mock_response.return_value = {"data": ["paginated"], "meta": {}}

    controller = PaigApiKeyController()
    result = await controller.get_api_keys_by_application_id_with_filters(
        application_id=1,
        api_key_name="My Key",
        description="Test key",
        page=1,
        size=10,
        sort="name",
        key_status="ACTIVE",
        exact_match="True"
    )

    assert result == {"data": ["paginated"], "meta": {}}
    mock_instance.get_api_keys_by_application_id.assert_awaited_once()


@pytest.mark.asyncio
@patch("api.apikey.controllers.paig_api_key_controller.PaigApiKeyService")
async def test_get_api_keys_by_application_id_with_filters_no_results(mock_service):
    mock_instance = mock_service.return_value
    mock_instance.get_api_keys_by_application_id = AsyncMock(return_value=(None, 0))

    controller = PaigApiKeyController()
    with pytest.raises(NotFoundException, match="No results found"):
        await controller.get_api_keys_by_application_id_with_filters(
            application_id=1,
            api_key_name="Key",
            description="Desc",
            page=1,
            size=10,
            sort="name",
            key_status="ACTIVE",
            exact_match=True
        )


@pytest.mark.asyncio
@patch("api.apikey.controllers.paig_api_key_controller.PaigApiKeyService")
async def test_get_api_key_by_ids(mock_service):
    mock_instance = mock_service.return_value
    mock_instance.get_api_key_by_ids = AsyncMock(return_value=["mocked_key"])

    controller = PaigApiKeyController()
    result = await controller.get_api_key_by_ids([1, 2])
    assert result == ["mocked_key"]
    mock_instance.get_api_key_by_ids.assert_awaited_once_with([1, 2])


@pytest.mark.asyncio
@patch("api.apikey.controllers.paig_api_key_controller.PaigApiKeyService")
async def test_create_api_key(mock_service):
    mock_instance = mock_service.return_value
    mock_instance.create_api_key = AsyncMock(return_value={"id": 1})

    controller = PaigApiKeyController()
    result = await controller.create_api_key({"api_key_name": "Test"}, 100)
    assert result == {"id": 1}
    mock_instance.create_api_key.assert_awaited_once_with({"api_key_name": "Test"}, 100)


@pytest.mark.asyncio
@patch("api.apikey.controllers.paig_api_key_controller.PaigApiKeyService")
async def test_disable_api_key(mock_service):
    mock_instance = mock_service.return_value
    mock_instance.disable_api_key = AsyncMock(return_value={"status": "disabled"})

    controller = PaigApiKeyController()
    result = await controller.disable_api_key(123)
    assert result == {"status": "disabled"}
    mock_instance.disable_api_key.assert_awaited_once_with(123)


@pytest.mark.asyncio
@patch("api.apikey.controllers.paig_api_key_controller.PaigApiKeyService")
async def test_permanent_delete_api_key(mock_service):
    mock_instance = mock_service.return_value
    mock_instance.permanent_delete_api_key = AsyncMock(return_value={"status": "deleted"})

    controller = PaigApiKeyController()
    result = await controller.permanent_delete_api_key(123)
    assert result == {"status": "deleted"}
    mock_instance.permanent_delete_api_key.assert_awaited_once_with(123)
