import pytest
from pydantic import ValidationError
from api.guardrails import GuardrailProvider
from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataView, GRSensitiveDataFilter

def test_gr_sensitive_data_view_valid_data():
    valid_data = {
        "name": "sensitive_data_1",
        "label": "label_1",
        "guardrailsProvider": GuardrailProvider.PAIG,
        "description": "Test description of sensitive data"
    }
    view = GRSensitiveDataView(**valid_data)
    assert view.name == valid_data["name"]
    assert view.label == valid_data["label"]
    assert view.guardrail_provider == valid_data["guardrailsProvider"]
    assert view.description == valid_data["description"]


def test_gr_sensitive_data_view_optional_fields():
    partial_data = {
        "name": "sensitive_data_1",
        "label": "label_1",
        "guardrailsProvider": GuardrailProvider.PAIG
    }
    view = GRSensitiveDataView(**partial_data)
    assert view.name == partial_data["name"]
    assert view.label == partial_data["label"]
    assert view.guardrail_provider == partial_data["guardrailsProvider"]
    assert view.description is None


def test_gr_sensitive_data_view_invalid_provider():
    invalid_data = {
        "name": "sensitive_data_1",
        "label": "label_1",
        "guardrailsProvider": "INVALID_PROVIDER"
    }
    with pytest.raises(ValidationError):
        GRSensitiveDataView(**invalid_data)


def test_gr_sensitive_data_filter_valid_data():
    valid_data = {
        "name": "sensitive_data_1",
        "label": "label_1",
        "guardrailsProvider": GuardrailProvider.PAIG,
        "description": "Test description of sensitive data"
    }
    filter_ = GRSensitiveDataFilter(**valid_data)
    assert filter_.name == valid_data["name"]
    assert filter_.label == valid_data["label"]
    assert filter_.guardrail_provider == valid_data["guardrailsProvider"]
    assert filter_.description == valid_data["description"]


def test_gr_sensitive_data_filter_optional_fields():
    partial_data = {
        "guardrailsProvider": GuardrailProvider.PAIG
    }
    filter_ = GRSensitiveDataFilter(**partial_data)
    assert filter_.guardrail_provider == partial_data["guardrailsProvider"]
    assert filter_.name is None
    assert filter_.label is None
    assert filter_.description is None


def test_gr_sensitive_data_filter_invalid_provider():
    invalid_data = {
        "guardrailsProvider": "INVALID_PROVIDER",
    }
    with pytest.raises(ValidationError):
        GRSensitiveDataFilter(**invalid_data)


def test_gr_sensitive_data_filter_invalid_key_type():
    invalid_data = {
        "name": 12345,  # Invalid type for name (should be string)
        "guardrailsProvider": GuardrailProvider.PAIG
    }
    with pytest.raises(ValidationError):
        GRSensitiveDataFilter(**invalid_data)
