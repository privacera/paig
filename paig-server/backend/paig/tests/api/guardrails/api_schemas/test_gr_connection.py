import pytest
from pydantic import ValidationError
from api.guardrails.api_schemas.gr_connection import GRConnectionView, GRConnectionFilter
from api.guardrails import GuardrailProvider


def test_guardrail_connection_view_valid_data():
    valid_data = {
        "id": 1,
        "status": 1,
        "createTime": "2024-10-29T13:03:27.000000",
        "updateTime": "2024-10-29T13:03:27.000000",
        "name": "gr_connection_1",
        "description": "test description1",
        "guardrailsProvider": GuardrailProvider.AWS,
        "connectionDetails": {
            "access_key": "mock_access_key",
            "secret_key": "mock_secret_key",
            "session_token": "mock_session_token"
        }
    }
    view = GRConnectionView(**valid_data)
    assert view.id == valid_data["id"]
    assert view.status == valid_data["status"]
    assert view.name == valid_data["name"]
    assert view.description == valid_data["description"]
    assert view.guardrail_provider == valid_data["guardrailsProvider"]
    assert view.connection_details == valid_data["connectionDetails"]


def test_guardrail_connection_view_optional_fields():
    partial_data = {
        "name": "gr_connection_1",
        "guardrailsProvider": GuardrailProvider.AWS,
        "connectionDetails": {
            "access_key": "mock_access_key",
            "secret_key": "mock_secret_key",
            "session_token": "mock_session_token"
        }
    }
    view = GRConnectionView(**partial_data)
    assert view.name == partial_data["name"]
    assert view.id is None
    assert view.status is None
    assert view.description is None


def test_guardrail_connection_view_invalid_provider():
    invalid_data = {
        "name": "gr_connection_1",
        "guardrailsProvider": "INVALID_PROVIDER",
        "connectionDetails": {
            "access_key": "mock_access_key",
            "secret_key": "mock_secret_key",
            "session_token": "mock_session_token"
        }
    }
    with pytest.raises(ValidationError):
        GRConnectionView(**invalid_data)


def test_guardrail_connection_filter_valid_data():
    valid_data = {
        "name": "gr_connection_1",
        "description": "test description1",
        "guardrailsProvider": GuardrailProvider.AWS
    }
    filter_ = GRConnectionFilter(**valid_data)
    assert filter_.name == valid_data["name"]
    assert filter_.description == valid_data["description"]
    assert filter_.guardrail_provider == valid_data["guardrailsProvider"]


def test_guardrail_connection_filter_optional_fields():
    partial_data = {
        "guardrailsProvider": GuardrailProvider.AWS
    }
    filter_ = GRConnectionFilter(**partial_data)
    assert filter_.guardrail_provider == partial_data["guardrailsProvider"]
    assert filter_.name is None
    assert filter_.description is None


def test_guardrail_connection_filter_invalid_key_type():
    invalid_data = {
        "guardrailsProvider": "INVALID_PROVIDER",
    }
    with pytest.raises(ValidationError):
        GRConnectionFilter(**invalid_data)
