import pytest
from flask import Response as FlaskResponse
from fastapi.responses import Response as FastApiResponse
from paig_common.response import Response


def test_response_initialization():
    response = Response("Test content", 404)
    assert response.content == "Test content"
    assert response.status_code == 404


def test_to_flask_response():
    response = Response("Test content", 404)
    flask_response = response.to_flask_response()
    assert isinstance(flask_response, FlaskResponse)
    assert flask_response.get_data(as_text=True) == "Test content"
    assert flask_response.status_code == 404


def test_to_fastapi_response():
    response = Response("Test content", 404)
    fastapi_response = response.to_fastapi_response()
    assert isinstance(fastapi_response, FastApiResponse)
    assert fastapi_response.body == b"Test content"
    assert fastapi_response.status_code == 404
