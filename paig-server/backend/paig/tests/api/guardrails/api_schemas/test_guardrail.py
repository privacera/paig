import pytest
from pydantic import ValidationError

from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GRApplicationView, GRConfigView, \
    GuardrailsDataView
from api.guardrails.database.db_models.gr_connection_model import GuardrailProvider

guardrail_data = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "mock_guardrail",
    "description": "mock description",
    "version": 1,
    "applicationKeys": ["mock_app_key1", "mock_app_key2"],
    "guardrailConfigs": [
        {
            "id": 3,
            "status": 1,
            "createTime": "2024-10-29T13:03:27.000000",
            "updateTime": "2024-10-29T13:03:27.000000",
            "guardrailProvider": GuardrailProvider.AWS,
            "guardrailProviderConnectionName": "mock_gr_connection",
            "configType": "contentPolicyConfig",
            "configData": {
                "filtersConfig": [
                    {
                        "inputStrength": "HIGH",
                        "outputStrength": "HIGH",
                        "type": "VIOLENCE"
                    },
                    {
                        "inputStrength": "HIGH",
                        "outputStrength": "NONE",
                        "type": "PROMPT_ATTACK"
                    },
                    {
                        "inputStrength": "HIGH",
                        "outputStrength": "HIGH",
                        "type": "MISCONDUCT"
                    },
                    {
                        "inputStrength": "HIGH",
                        "outputStrength": "HIGH",
                        "type": "HATE"
                    },
                    {
                        "inputStrength": "HIGH",
                        "outputStrength": "HIGH",
                        "type": "SEXUAL"
                    },
                    {
                        "inputStrength": "HIGH",
                        "outputStrength": "HIGH",
                        "type": "INSULTS"
                    }
                ]
            }
        }
    ],
    "guardrailProviderResponse": {
        "AWS": {
            "success": True,
            "response": {
                "guardrailId": "jedhzp6tz8ic",
                "guardrailArn": "arn:aws:bedrock:us-east-1:404161567776:guardrail/jedhzp6tz8ic",
                "version": "DRAFT"
            }
        }
    }
}


def test_guardrail_view_valid_data():
    view = GuardrailView(**guardrail_data)
    assert view.id == guardrail_data["id"]
    assert view.status == guardrail_data["status"]
    assert view.name == guardrail_data["name"]
    assert view.description == guardrail_data["description"]
    assert view.version == guardrail_data["version"]
    assert view.application_keys == guardrail_data["applicationKeys"]
    assert view.guardrail_configs[0].config_data == guardrail_data["guardrailConfigs"][0]["configData"]
    assert view.guardrail_configs[0].config_type == guardrail_data["guardrailConfigs"][0]["configType"]
    assert view.guardrail_configs[0].guardrail_provider == guardrail_data["guardrailConfigs"][0]["guardrailProvider"]
    assert view.guardrail_configs[0].guardrail_provider_connection_name == guardrail_data["guardrailConfigs"][0]["guardrailProviderConnectionName"]
    assert view.guardrail_provider_response == guardrail_data["guardrailProviderResponse"]


def test_guardrail_view_optional_fields():
    partial_data = guardrail_data.copy()
    partial_data.pop("id")
    partial_data.pop("status")
    partial_data.pop("description")

    view = GuardrailView(**partial_data)

    assert view.name == partial_data["name"]
    assert view.id is None
    assert view.status is None
    assert view.description is None


def test_guardrail_view_invalid_provider():
    import copy
    invalid_data = copy.deepcopy(guardrail_data)
    invalid_data["guardrailConfigs"][0]["guardrailProvider"] = "INVALID_PROVIDER"
    with pytest.raises(ValidationError):
        GuardrailView(**invalid_data)


def test_guardrail_filter_valid_data():
    valid_data = {
        "name": "mock_guardrail",
        "description": "test description1",
        "version": 1,
    }
    filter_ = GuardrailFilter(**valid_data)
    assert filter_.name == valid_data["name"]
    assert filter_.description == valid_data["description"]
    assert filter_.version == valid_data["version"]


def test_guardrail_filter_optional_fields():
    partial_data = {
        "name": "mock_guardrail"
    }
    filter_ = GuardrailFilter(**partial_data)
    assert filter_.name == partial_data["name"]
    assert filter_.version is None
    assert filter_.description is None


def test_guardrail_filter_invalid_key_type():
    invalid_data = {
        "name": 121,
    }
    with pytest.raises(ValidationError):
        GuardrailFilter(**invalid_data)


def test_guardrail_application_view_valid_data():
    application_data = {
        "applicationKey": "mock_app_key",
        "applicationId": 1,
        "applicationName": "mock_app"
    }
    view = GRApplicationView(**application_data)
    assert view.application_key == application_data["applicationKey"]
    assert view.application_id == application_data["applicationId"]
    assert view.application_name == application_data["applicationName"]


def test_guardrail_application_view_optional_fields():
    partial_data = {
        "applicationKey": "mock_app_key",
        "applicationName": "mock_app"
    }
    view = GRApplicationView(**partial_data)
    assert view.application_key == partial_data["applicationKey"]
    assert view.application_id is None
    assert view.application_name == partial_data["applicationName"]


def test_guardrail_application_view_invalid_key_type():
    invalid_data = {
        "applicationKey": 121,
    }
    with pytest.raises(ValidationError):
        GRApplicationView(**invalid_data)


def test_to_guardrail_config():
    guardrail_config_data = {
        "guardrailProvider": GuardrailProvider.AWS,
        "guardrailProviderConnectionName": "mock_gr_connection",
        "configType": "contentPolicyConfig",
        "configData": {
            "filtersConfig": [
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                    "type": "VIOLENCE"
                },
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "NONE",
                    "type": "PROMPT_ATTACK"
                },
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                    "type": "MISCONDUCT"
                },
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                    "type": "HATE"
                },
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                    "type": "SEXUAL"
                },
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                    "type": "INSULTS"
                }
            ]
        }
    }
    view = GRConfigView(**guardrail_config_data)
    guardrail_config = view.to_guardrail_config()
    assert guardrail_config.guardrailProvider == guardrail_config_data["guardrailProvider"].name
    assert guardrail_config.guardrailProviderConnectionName == guardrail_config_data["guardrailProviderConnectionName"]
    assert guardrail_config.configType == guardrail_config_data["configType"]
    assert guardrail_config.configData == guardrail_config_data["configData"]


def test_guardrails_data_view_valid_data():
    guardrails_data_for_app = {
        "applicationKey": "mock_app_key",
        "version": 1,
        "guardrails": [guardrail_data]
    }
    view = GuardrailsDataView(**guardrails_data_for_app)
    assert view.app_key == guardrails_data_for_app["applicationKey"]
    assert view.version == guardrails_data_for_app["version"]
    assert view.guardrails[0].id == guardrail_data["id"]
    assert view.guardrails[0].status == guardrail_data["status"]
    assert view.guardrails[0].name == guardrail_data["name"]
    assert view.guardrails[0].description == guardrail_data["description"]
    assert view.guardrails[0].version == guardrail_data["version"]
    assert view.guardrails[0].application_keys == guardrail_data["applicationKeys"]
    assert view.guardrails[0].guardrail_configs[0].config_data == guardrail_data["guardrailConfigs"][0]["configData"]
    assert view.guardrails[0].guardrail_configs[0].config_type == guardrail_data["guardrailConfigs"][0]["configType"]
    assert view.guardrails[0].guardrail_configs[0].guardrail_provider == guardrail_data["guardrailConfigs"][0]["guardrailProvider"]
    assert view.guardrails[0].guardrail_configs[0].guardrail_provider_connection_name == guardrail_data["guardrailConfigs"][0]["guardrailProviderConnectionName"]
    assert view.guardrails[0].guardrail_provider_response == guardrail_data["guardrailProviderResponse"]