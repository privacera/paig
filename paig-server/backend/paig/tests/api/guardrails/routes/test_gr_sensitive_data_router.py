import json
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataView
from api.guardrails.controllers.gr_sensitive_data_controller import GRSensitiveDataController
from core.controllers.paginated_response import create_pageable_response

gr_sensitive_data_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "Test name",
    "label": "Test label",
    "description": "Test description",
}

gr_sensitive_data_view = GRSensitiveDataView(**gr_sensitive_data_view_json)


@pytest.fixture()
def mock_gr_sensitive_data_controller():
    mock_gr_sensitive_data_controller = AsyncMock(spec=GRSensitiveDataController)

    mock_gr_sensitive_data_controller.list_gr_sensitive_datas.return_value = create_pageable_response(
        content=[gr_sensitive_data_view],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )

    mock_gr_sensitive_data_controller.create_gr_sensitive_data.return_value = gr_sensitive_data_view
    mock_gr_sensitive_data_controller.get_gr_sensitive_data_by_id.return_value = gr_sensitive_data_view
    mock_gr_sensitive_data_controller.update_gr_sensitive_data.return_value = gr_sensitive_data_view
    mock_gr_sensitive_data_controller.delete_gr_sensitive_data.return_value = None

    return mock_gr_sensitive_data_controller


@pytest.fixture
def gr_sensitive_data_app(mock_gr_sensitive_data_controller, mocker):
    def get_mock_gr_sensitive_data_controller():
        return mock_gr_sensitive_data_controller

    mocker.patch("api.guardrails.controllers.gr_sensitive_data_controller.GRSensitiveDataController", get_mock_gr_sensitive_data_controller)
    from api.guardrails.routes.gr_sensitive_data_router import gr_sensitive_data_router

    # Create client
    from fastapi import FastAPI
    app = FastAPI(
        title="Paig",
        description="Paig Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None
    )

    app.include_router(gr_sensitive_data_router, prefix="/gr_sensitive_data")
    yield app


@pytest.fixture
def gr_sensitive_data_app_client(gr_sensitive_data_app):
    return TestClient(gr_sensitive_data_app)


def test_list_gr_sensitive_data_success(gr_sensitive_data_app_client):
    response = gr_sensitive_data_app_client.get("http://localhost:9090/gr_sensitive_data")
    assert response.status_code == status.HTTP_200_OK
    assert "content" in response.json()
    assert len(response.json()["content"]) == 1


def test_create_gr_sensitive_data_success(gr_sensitive_data_app_client):
    response = gr_sensitive_data_app_client.post("http://localhost:9090/gr_sensitive_data", content=json.dumps(gr_sensitive_data_view_json))
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1
    assert response.json()["status"] == 1
    assert response.json()["name"] == "Test name"
    assert response.json()["label"] == "Test label"
    assert response.json()["description"] == "Test description"


def test_get_gr_sensitive_data_by_id_success(gr_sensitive_data_app_client):
    response = gr_sensitive_data_app_client.get("http://localhost:9090/gr_sensitive_data/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_update_gr_sensitive_data_success(gr_sensitive_data_app_client):
    response = gr_sensitive_data_app_client.put("http://localhost:9090/gr_sensitive_data/1", content=json.dumps(gr_sensitive_data_view_json))
    assert response.status_code == status.HTTP_200_OK


def test_delete_gr_sensitive_data_success(gr_sensitive_data_app_client):
    response = gr_sensitive_data_app_client.delete("http://localhost:9090/gr_sensitive_data/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
