import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailsDataView, GRVersionHistoryView
from api.guardrails.controllers.guardrail_controller import GuardrailController
from core.controllers.paginated_response import create_pageable_response

guardrail_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "mock_guardrail",
    "description": "test description1",
    "version": 1,
    "guardrailConnectionName": "gr_connection_1",
    "guardrailProvider": "AWS",
}

guardrail_view = GuardrailView(**guardrail_view_json)

guardrail_data_view_json = {
    "applicationKey": "mock_app_key",
    "version": 1,
    "guardrails": [guardrail_view_json]
}

guardrail_data_view = GuardrailsDataView(**guardrail_data_view_json)


gr_version_history_view_json = {
        "id": 1,
        "status": 1,
        "createTime": "2024-10-29T13:03:27.000000",
        "updateTime": "2024-10-29T13:03:27.000000",
        "name": "mock_guardrail",
        "description": "mock description",
        "version": 1,
        "guardrailConnectionName": "gr_connection_1",
        "guardrailProvider": "AWS",
        "guardrailId": 1
    }
guardrail_version_history_view = GRVersionHistoryView(**gr_version_history_view_json)


@pytest.fixture()
def mock_guardrail_controller():
    mock_guardrail_controller = AsyncMock(spec=GuardrailController)

    mock_guardrail_controller.list.return_value = create_pageable_response(
        content=[guardrail_view],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )

    mock_guardrail_controller.get_history.return_value = create_pageable_response(
        content=[guardrail_version_history_view],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )

    mock_guardrail_controller.create.return_value = guardrail_view
    mock_guardrail_controller.get_by_id.return_value = guardrail_view
    mock_guardrail_controller.get_all_by_app_key.return_value = guardrail_data_view
    mock_guardrail_controller.update.return_value = guardrail_view
    mock_guardrail_controller.delete.return_value = None

    return mock_guardrail_controller


@pytest.fixture
def guardrail_app(mock_guardrail_controller, mocker):
    def get_mock_guardrail_controller():
        return mock_guardrail_controller

    mocker.patch("api.guardrails.controllers.guardrail_controller.GuardrailController", get_mock_guardrail_controller)
    from api.guardrails.routes.guardrail_router import guardrail_router

    # Create client
    from fastapi import FastAPI
    app = FastAPI(
        title="Paig",
        description="Paig Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None
    )

    app.include_router(guardrail_router, prefix="/guardrail")
    yield app


@pytest.fixture
def guardrail_app_client(guardrail_app):
    return TestClient(guardrail_app)


def test_list_guardrail_success(guardrail_app_client):
    response = guardrail_app_client.get("http://localhost:9090/guardrail")
    assert response.status_code == status.HTTP_200_OK
    assert "content" in response.json()
    assert len(response.json()["content"]) == 1


def test_get_guardrail_history_success(guardrail_app_client):
    response = guardrail_app_client.get("http://localhost:9090/guardrail/1/history")
    assert response.status_code == status.HTTP_200_OK
    assert "content" in response.json()
    assert len(response.json()["content"]) == 1


def test_get_all_guardrail_history_success(guardrail_app_client):
    response = guardrail_app_client.get("http://localhost:9090/guardrail/history")
    assert response.status_code == status.HTTP_200_OK
    assert "content" in response.json()
    assert len(response.json()["content"]) == 1


def test_create_guardrail_success(guardrail_app_client):
    response = guardrail_app_client.post("http://localhost:9090/guardrail", content=json.dumps(guardrail_view_json))
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1
    assert response.json()["status"] == 1
    assert response.json()["name"] == "mock_guardrail"
    assert response.json()["description"] == "test description1"
    assert response.json()["version"] == 1


def test_get_guardrail_by_id_success(guardrail_app_client):
    response = guardrail_app_client.get("http://localhost:9090/guardrail/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_get_guardrail_by_app_key_success(guardrail_app_client):
    response = guardrail_app_client.get("http://localhost:9090/guardrail/application/mock_app_key?lastKnownVersion=0")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["applicationKey"] == "mock_app_key"
    assert response.json()["version"] == 1
    assert len(response.json()["guardrails"]) == 1


def test_update_guardrail_success(guardrail_app_client):
    response = guardrail_app_client.put("http://localhost:9090/guardrail/1", content=json.dumps(guardrail_view_json))
    assert response.status_code == status.HTTP_200_OK


def test_delete_guardrail_success(guardrail_app_client):
    response = guardrail_app_client.delete("http://localhost:9090/guardrail/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
