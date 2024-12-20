import pytest
from pydantic import ValidationError

from api.guardrails.api_schemas.response_template import ResponseTemplateView, ResponseTemplateFilter

def test_response_template_view_valid():
    data = {
        "response": "This is a sample response",
        "description": "This is a description"
    }
    view = ResponseTemplateView(**data)

    assert view.response == data["response"]
    assert view.description == data["description"]

def test_response_template_view_missing_optional_fields():
    data = {
        "response": "This is a sample response"
    }
    view = ResponseTemplateView(**data)

    assert view.response == data["response"]
    assert view.description is None

def test_response_template_view_invalid_data():
    data = {
        "response": None
    }
    with pytest.raises(ValidationError):
        ResponseTemplateView(**data)

# Unit tests for ResponseTemplateFilter

def test_response_template_filter_valid():
    data = {
        "response": "Sample filter response",
        "description": "Sample filter description"
    }
    filter_obj = ResponseTemplateFilter(**data)

    assert filter_obj.response == data["response"]
    assert filter_obj.description == data["description"]

def test_response_template_filter_missing_fields():
    data = {}
    filter_obj = ResponseTemplateFilter(**data)

    assert filter_obj.response is None
    assert filter_obj.description is None

def test_response_template_filter_partial_data():
    data = {
        "response": "Partial filter response"
    }
    filter_obj = ResponseTemplateFilter(**data)

    assert filter_obj.response == data["response"]
    assert filter_obj.description is None
