import pytest

from api.guardrails import GuardrailProvider
from api.guardrails.api_schemas.gr_connection import GRConnectionView
from api.guardrails.api_schemas.guardrail import GRConfigView, GuardrailView
from api.guardrails.providers import GuardrailConfig
from api.guardrails.transformers.guardrail_transformer import GuardrailTransformer
from core.exceptions import BadRequestException

guardrail_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "mock_guardrail",
    "description": "mock description",
    "version": 1,
    "guardrailConnectionName": "gr_connection_1",
    "guardrailProvider": "AWS"
}

gr_content_moderation_config_json = {
    "configType": "CONTENT_MODERATION",
    "configData": {
        "configs": [
            {
                "category": "VIOLENCE",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            },
            {
                "category": "MISCONDUCT",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            },
            {
                "category": "HATE",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "low"
            },
            {
                "category": "SEXUAL",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            },
            {
                "category": "INSULTS",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            }
        ]
    },
    "responseMessage": "I couldn't respond to that message."
}
gr_sensitive_data_config_json = {
    "configType": "SENSITIVE_DATA",
    "status": 1,
    "responseMessage": "I couldn't respond to that message.",
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
    }
}
gr_denied_terms_config_json = {
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
}
gr_off_topic_config_json = {
    "configType": "OFF_TOPIC",
    "responseMessage": "I couldn't respond to that message.",
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
    }
}
gr_prompt_safety_config_json = {
    "configType": "PROMPT_SAFETY",
    "status": 1,
    "responseMessage": "I couldn't respond to that message.",
    "configData": {
        "configs": [
            {
                "category": "PROMPT_ATTACK",
                "filterStrengthPrompt": "HIGH"
            }
        ]
    }
}

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

gr_content_moderation_config = GRConfigView(**gr_content_moderation_config_json)
gr_sensitive_data_config = GRConfigView(**gr_sensitive_data_config_json)
gr_denied_terms_config = GRConfigView(**gr_denied_terms_config_json)
gr_off_topic_config = GRConfigView(**gr_off_topic_config_json)
gr_prompt_safety_config = GRConfigView(**gr_prompt_safety_config_json)

guardrail_view = GuardrailView(**guardrail_view_json)


def test_aws_guardrail_transform_content_moderation_config():
    expected_config = GuardrailConfig(configType="contentPolicyConfig", guardrailProvider="AWS", configData={
        "filtersConfig": [
            {
                "type": "VIOLENCE",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "MISCONDUCT",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "HATE",
                "inputStrength": "HIGH",
                "outputStrength": "LOW"
            },
            {
                "type": "SEXUAL",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "INSULTS",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            }
        ]
    })
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_content_moderation_config])
    assert transformed_config == {"AWS": [expected_config]}


def test_aws_guardrail_transform_content_moderation_config_with_empty_config_data():
    gr_content_moderation_config_with_empty = GRConfigView(**gr_content_moderation_config_json)
    gr_content_moderation_config_with_empty.config_data = {"configs": []}
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_content_moderation_config_with_empty])
    assert transformed_config == {}


def test_aws_guardrail_transform_content_moderation_config_gives_error():
    gr_content_moderation_config_with_partial_data = GRConfigView(**gr_content_moderation_config_json)
    gr_content_moderation_config_with_partial_data.config_data = {"configs": [{"category": "VIOLENCE", "guardrailProvider": "AWS"}]}
    with pytest.raises(BadRequestException) as exc_info:
        GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_content_moderation_config_with_partial_data])

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Failed to process guardrail configurations: Invalid data in content moderation config: [KeyError('filterStrengthPrompt')]"


def test_aws_guardrail_transform_sensitive_data_config():
    expected_config = GuardrailConfig(configType="sensitiveInformationPolicyConfig", guardrailProvider="AWS",
                                      configData={
                                          "regexesConfig": [
                                              {
                                                  "name": "email_regex",
                                                  "description": "email_regex",
                                                  "pattern": "test_pattern",
                                                  "action": "ANONYMIZE"
                                              }
                                          ]
                                      })
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_sensitive_data_config])
    assert transformed_config == {"AWS": [expected_config]}


def test_aws_guardrail_transform_sensitive_data_config_with_empty_config_data():
    gr_sensitive_data_config_with_empty = GRConfigView(**gr_sensitive_data_config_json)
    gr_sensitive_data_config_with_empty.config_data = {"configs": []}
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_sensitive_data_config_with_empty])
    assert transformed_config == {}


def test_aws_guardrail_transform_sensitive_data_config_gives_error():
    gr_sensitive_data_config_with_partial_data = GRConfigView(**gr_sensitive_data_config_json)
    gr_sensitive_data_config_with_partial_data.config_data = {"configs": [{"category": "EMAIL"}]}
    with pytest.raises(BadRequestException) as exc_info:
        GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_sensitive_data_config_with_partial_data])

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Failed to process guardrail configurations: Invalid data in sensitive data config: [KeyError('action')]"


def test_aws_guardrail_transform_denied_terms_config():
    expected_config = GuardrailConfig(configType="wordPolicyConfig", guardrailProvider="AWS", configData={
        "wordsConfig": [
            {
                "text": "Violance"
            },
            {
                "text": "Violent Bahaviour"
            },
            {
                "text": "Physical Assault"
            }
        ],
        "managedWordListsConfig": [
            {
                "type": "PROFANITY"
            }
        ]
    })
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_denied_terms_config])
    assert transformed_config == {"AWS": [expected_config]}


def test_aws_guardrail_transform_denied_terms_config_with_empty_config_data():
    gr_denied_terms_config_with_empty = GRConfigView(**gr_denied_terms_config_json)
    gr_denied_terms_config_with_empty.config_data = {"configs": []}
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_denied_terms_config_with_empty])
    assert transformed_config == {}


def test_aws_guardrail_transform_denied_terms_config_gives_error():
    gr_denied_terms_config_with_partial_data = GRConfigView(**gr_denied_terms_config_json)
    gr_denied_terms_config_with_partial_data.config_data = {"configs": [{"type": "PROFANITY"}]}
    with pytest.raises(BadRequestException) as exc_info:
        GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_denied_terms_config_with_partial_data])

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Failed to process guardrail configurations: Invalid data in denied terms config: [KeyError('value')]"


def test_aws_guardrail_transform_off_topic_config():
    expected_config = GuardrailConfig(configType="topicPolicyConfig", guardrailProvider="AWS", configData={
        "topicsConfig": [
            {
                "name": "Sports",
                "definition": "Sports Definition",
                "examples": [
                    "Who's playing NFL tonight ?",
                    "Who's leading tonight ?"
                ],
                "type": "DENY"
            }
        ]
    })
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_off_topic_config])
    assert transformed_config == {"AWS": [expected_config]}


def test_aws_guardrail_transform_off_topic_config_with_empty_config_data():
    gr_off_topic_config_with_empty = GRConfigView(**gr_off_topic_config_json)
    gr_off_topic_config_with_empty.config_data = {"configs": []}
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_off_topic_config_with_empty])
    assert transformed_config == {}


def test_aws_guardrail_transform_off_topic_config_gives_error():
    gr_off_topic_config_with_partial_data = GRConfigView(**gr_off_topic_config_json)
    gr_off_topic_config_with_partial_data.config_data = {"configs": [{"topic": "Sports"}]}
    with pytest.raises(BadRequestException) as exc_info:
        GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_off_topic_config_with_partial_data])

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Failed to process guardrail configurations: Invalid data in off topic config: [KeyError('definition')]"


def test_aws_guardrail_transform_prompt_safety_config():
    expected_config = GuardrailConfig(configType="contentPolicyConfig", guardrailProvider="AWS", configData={
        "filtersConfig": [
            {'inputStrength': 'HIGH', 'outputStrength': 'NONE', 'type': 'PROMPT_ATTACK'},
            {'inputStrength': 'NONE', 'outputStrength': 'NONE', 'type': 'HATE'},
            {'inputStrength': 'NONE', 'outputStrength': 'NONE', 'type': 'INSULTS'},
            {'inputStrength': 'NONE', 'outputStrength': 'NONE', 'type': 'SEXUAL'},
            {'inputStrength': 'NONE', 'outputStrength': 'NONE', 'type': 'VIOLENCE'},
            {'inputStrength': 'NONE', 'outputStrength': 'NONE', 'type': 'MISCONDUCT'}
        ]
    })
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_prompt_safety_config])
    assert {"AWS": [expected_config]} == transformed_config


def test_aws_guardrail_transform_prompt_safety_config_with_empty_config_data():
    gr_prompt_safety_config_with_empty = GRConfigView(**gr_prompt_safety_config_json)
    gr_prompt_safety_config_with_empty.config_data = {"configs": []}
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_prompt_safety_config_with_empty])
    assert transformed_config == {}


def test_aws_guardrail_transform_multiple_configs():
    expected_config = GuardrailConfig(configType="contentPolicyConfig", guardrailProvider="AWS", configData={
        "filtersConfig": [
            {
                "type": "VIOLENCE",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "MISCONDUCT",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "HATE",
                "inputStrength": "HIGH",
                "outputStrength": "LOW"
            },
            {
                "type": "SEXUAL",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "INSULTS",
                "inputStrength": "HIGH",
                "outputStrength": "MEDIUM"
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "NONE",
                "type": "PROMPT_ATTACK"
            }
        ]
    })
    transformed_config = GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_prompt_safety_config, gr_content_moderation_config])
    assert transformed_config == {"AWS": [expected_config]}


def test_aws_guardrail_transform_prompt_safety_config_gives_error():
    gr_prompt_safety_config_with_partial_data = GRConfigView(**gr_prompt_safety_config_json)
    gr_prompt_safety_config_with_partial_data.config_data = {"configs": [{"category": "PROMPT_ATTACK", "guardrailProvider": "AWS"}]}
    with pytest.raises(BadRequestException) as exc_info:
        GuardrailTransformer.transform(GuardrailProvider.AWS, [gr_content_moderation_config, gr_prompt_safety_config_with_partial_data])

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Failed to process guardrail configurations: Invalid data in prompt safety config: [KeyError('filterStrengthPrompt')]"
