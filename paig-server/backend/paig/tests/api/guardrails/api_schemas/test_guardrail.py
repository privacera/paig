import pytest
from pydantic import ValidationError

from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter

guardrail_data = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "mock_guardrail",
    "description": "mock description",
    "version": 1,
    "guardrailConnectionName": "gr_connection_1",
    "guardrailProvider": "AWS",
    "guardrailConfigs": [
        {
            "id": 1,
            "status": 1,
            "createTime": "2024-12-05T10:17:04.662783",
            "updateTime": "2024-12-05T10:17:04.662832",
            "configType": "CONTENT_MODERATION",
            "configData": {
                "configs": [
                    {
                        "category": "Hate",
                        "filterStrengthPrompt": "high",
                        "filterStrengthResponse": "medium"
                    },
                    {
                        "category": "Insults",
                        "filterStrengthPrompt": "high",
                        "filterStrengthResponse": "medium"
                    }
                ]
            },
            "responseMessage": "I couldn't respond to that message."
        },
        {
            "id": 2,
            "status": 1,
            "createTime": "2024-12-05T10:17:04.662783",
            "updateTime": "2024-12-05T10:17:04.662832",
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "category": "EMAIL",
                        "action": "DENY"
                    },
                    {
                        "category": "USERNAME",
                        "action": "ALLOW"
                    },
                    {
                        "category": "PASSWORD",
                        "action": "REDACT"
                    },
                    {
                        "type": "regex",
                        "name": "email_regex",
                        "description": "email_regex",
                        "pattern": "test_pattern",
                        "action": "REDACT"
                    }
                ]
            },
            "responseMessage": "I couldn't respond to that message."
        },
        {
            "id": 3,
            "status": 1,
            "createTime": "2024-12-05T10:17:04.662783",
            "updateTime": "2024-12-05T10:17:04.662832",
            "configType": "OFF_TOPIC",
            "configData": {
                "configs": [
                    {
                        "topic": "Sports",
                        "definition": "Sports Definition",
                        "samplePhrases": [
                            "Who's playing NFL tonight ?",
                            "Who's leading tonight ?"
                        ],
                        "action": "DENY"
                    }
                ]
            },
            "responseMessage": "I couldn't respond to that message."
        },
        {
            "id": 4,
            "status": 1,
            "createTime": "2024-12-05T10:17:04.662783",
            "updateTime": "2024-12-05T10:17:04.662832",
            "configType": "DENIED_TERMS",
            "configData": {
                "configs": [
                    {
                        "type": "PROFANITY",
                        "value": True
                    },
                    {
                        "term": "Violance",
                        "keywords": [
                            "Violent Bahaviour",
                            "Physical Assault"
                        ]
                    }
                ]
            },
            "responseMessage": "I couldn't respond to that message."
        },
        {
            "id": 5,
            "status": 1,
            "createTime": "2024-12-05T10:17:04.662783",
            "updateTime": "2024-12-05T10:17:04.662832",
            "configType": "PROMPT_SAFETY",
            "configData": {
                "configs": [
                    {
                        "category": "PROMPT_ATTACK",
                        "filterStrengthPrompt": "HIGH"
                    }
                ]
            },
            "responseMessage": "I couldn't respond to that message."
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
    assert view.guardrail_provider.value == guardrail_data["guardrailProvider"]
    assert view.guardrail_connection_name == guardrail_data["guardrailConnectionName"]
    assert view.guardrail_configs[0].config_data == guardrail_data["guardrailConfigs"][0]["configData"]
    assert view.guardrail_configs[0].config_type.value == guardrail_data["guardrailConfigs"][0]["configType"]
    assert view.guardrail_configs[0].response_message == guardrail_data["guardrailConfigs"][0]["responseMessage"]
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
    invalid_data["guardrailProvider"] = "INVALID_PROVIDER"
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
