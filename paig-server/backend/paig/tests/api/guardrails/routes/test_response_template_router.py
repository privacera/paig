import json
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from api.guardrails.api_schemas.response_template import ResponseTemplateView
from api.guardrails.controllers.response_template_controller import ResponseTemplateController
from core.controllers.paginated_response import create_pageable_response

response_template_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "response": "Test response",
    "description": "Test description",
}

response_template_view = ResponseTemplateView(**response_template_view_json)


@pytest.fixture()
def mock_response_template_controller():
    mock_response_template_controller = AsyncMock(spec=ResponseTemplateController)

    mock_response_template_controller.list_response_templates.return_value = create_pageable_response(
        content=[response_template_view],
        total_elements=1,
        page_number=1,
        size=10,
        sort=["id"]
    )

    mock_response_template_controller.create_response_template.return_value = response_template_view
    mock_response_template_controller.get_response_template_by_id.return_value = response_template_view
    mock_response_template_controller.update_response_template.return_value = response_template_view
    mock_response_template_controller.delete_response_template.return_value = None

    return mock_response_template_controller


@pytest.fixture
def response_template_app(mock_response_template_controller, mocker):
    def get_mock_response_template_controller():
        return mock_response_template_controller

    mocker.patch("api.guardrails.controllers.response_template_controller.ResponseTemplateController", get_mock_response_template_controller)
    from api.guardrails.routes.response_template_router import response_template_router

    # Create client
    from fastapi import FastAPI
    app = FastAPI(
        title="Paig",
        description="Paig Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None
    )

    app.include_router(response_template_router, prefix="/response_template")
    yield app


@pytest.fixture
def response_template_app_client(response_template_app):
    return TestClient(response_template_app)


def test_list_response_templates_success(response_template_app_client):
    response = response_template_app_client.get("http://localhost:9090/response_template")
    assert response.status_code == status.HTTP_200_OK
    assert "content" in response.json()
    assert len(response.json()["content"]) == 1


def test_create_response_template_success(response_template_app_client):
    response = response_template_app_client.post("http://localhost:9090/response_template", content=json.dumps(response_template_view_json))
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1
    assert response.json()["status"] == 1
    assert response.json()["response"] == "Test response"
    assert response.json()["description"] == "Test description"


def test_get_response_template_by_id_success(response_template_app_client):
    response = response_template_app_client.get("http://localhost:9090/response_template/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_update_response_template_success(response_template_app_client):
    response = response_template_app_client.put("http://localhost:9090/response_template/1", content=json.dumps(response_template_view_json))
    assert response.status_code == status.HTTP_200_OK


def test_delete_response_template_success(response_template_app_client):
    response = response_template_app_client.delete("http://localhost:9090/response_template/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
