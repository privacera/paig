import json
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from api.guardrails.api_schemas.gr_connection import GRConnectionView
from api.guardrails.controllers.gr_connection_controller import GRConnectionController
from core.controllers.paginated_response import create_pageable_response

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

gr_connection_view = GRConnectionView(**gr_connection_view_json)


@pytest.fixture()
def mock_guardrail_connection_controller():
    mock_gr_connection_controller = AsyncMock(spec=GRConnectionController)

    mock_gr_connection_controller.list.return_value = create_pageable_response(
        content=[gr_connection_view],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )

    mock_gr_connection_controller.list_connection_provider_names.return_value = ["AWS"]
    mock_gr_connection_controller.create.return_value = gr_connection_view
    mock_gr_connection_controller.get_by_id.return_value = gr_connection_view
    mock_gr_connection_controller.update.return_value = gr_connection_view
    mock_gr_connection_controller.delete.return_value = None

    return mock_gr_connection_controller


@pytest.fixture
def gr_connection_app(mock_guardrail_connection_controller, mocker):
    def get_mock_gr_conn_controller():
        return mock_guardrail_connection_controller

    mocker.patch("api.guardrails.controllers.gr_connection_controller.GRConnectionController", get_mock_gr_conn_controller)
    from api.guardrails.routes.gr_connection_router import gr_connection_router

    # Create client
    from fastapi import FastAPI
    app = FastAPI(
        title="Paig",
        description="Paig Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None
    )

    app.include_router(gr_connection_router, prefix="/connection")
    yield app


@pytest.fixture
def gr_connection_app_client(gr_connection_app):
    return TestClient(gr_connection_app)


def test_list_guardrail_connections_success(gr_connection_app_client):
    response = gr_connection_app_client.get("http://localhost:9090/connection")
    assert response.status_code == status.HTTP_200_OK
    assert "content" in response.json()
    assert len(response.json()["content"]) == 1


def test_list_guardrail_connection_provider_names(gr_connection_app_client):
    response = gr_connection_app_client.get("http://localhost:9090/connection_providers")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json() == ["AWS"]


def test_create_guardrail_connection_success(gr_connection_app_client):
    response = gr_connection_app_client.post("http://localhost:9090/connection", content=json.dumps(gr_connection_view_json))
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1
    assert response.json()["status"] == 1
    assert response.json()["name"] == "gr_connection_1"
    assert response.json()["description"] == "test description1"
    assert response.json()["guardrailsProvider"] == "AWS"


def test_get_guardrail_connection_by_id_success(gr_connection_app_client):
    response = gr_connection_app_client.get("http://localhost:9090/connection/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_update_guardrail_connection_success(gr_connection_app_client):
    response = gr_connection_app_client.put("http://localhost:9090/connection/1", content=json.dumps(gr_connection_view_json))
    assert response.status_code == status.HTTP_200_OK


def test_delete_guardrail_connection_success(gr_connection_app_client):
    response = gr_connection_app_client.delete("http://localhost:9090/connection/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
