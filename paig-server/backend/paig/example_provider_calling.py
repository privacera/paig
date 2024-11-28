from api.guardrails.providers import GuardrailConnection, GuardrailProviderType, GuardrailProviderManager, \
    CreateGuardrailRequest, UpdateGuardrailRequest, DeleteGuardrailRequest
from api.guardrails.providers.backend.bedrock import BedrockGuardrailConfigType
from api.guardrails.providers.models import GuardrailConfig

aws_creds = {
    "access_key": "<ACCESS_KEY>",
    "secret_key": "<SECRET_KEY>",
    "session_token": "<SESSION_TOKEN>",
    "region": "us-east-1"
}

guardrail_connection = GuardrailConnection(
    name="AWS Bedrock Guardrail",
    description="Guardrail connection for AWS Bedrock",
    guardrailProvider=GuardrailProviderType.AWS,
    connectionDetails=aws_creds
)

content_policy_config = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.CONTENT_POLICY_CONFIG,
    configData={
        "filtersConfig": [
            {
                "inputStrength": "HIGH",
                "outputStrength": "HIGH",
                "type": "VIOLENCE"
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
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "NONE",
                "type": "PROMPT_ATTACK"
            }
        ]
    }
)

topic_policy_config = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.TOPIC_POLICY_CONFIG,
    configData={
        "topicsConfig": [
            {
                "definition": "Investment advice is recommendations on what to invest in, like specific stocks, funds or any other financial investment product so as to get maximum returns on the money invested.",
                "examples": [
                    "Where should I invest my money?",
                    "Is it worth investing in bank's fixed deposits?",
                    "Should I invest in mutual funds or directly in stocks?"
                ],
                "name": "OFF_TOPIC-INVESTMENT",
                "type": "DENY"
            },
            {
                "definition": "Deny any request that is related to weather or climate. ",
                "examples": [
                    "What is the weather in San Francisco?",
                    "Will it it hot in November?",
                    "What should I wear if it is cold outside?"
                ],
                "name": "OFF_TOPIC-Weather",
                "type": "DENY"
            },
            {
                "definition": "Any questions related to Sports. This could be chess, swiming, soccer, football, hocket or any activity which is considered sport or game.",
                "examples": [
                    "What won the world cup?",
                    "When does the basketball season begin?",
                    "Where will be the next Olympics?"
                ],
                "name": "OFF_TOPIC-Sports",
                "type": "DENY"
            },
            {
                "definition": "Anything to do with shopping or asking recommendations for buying for personal reasons.",
                "examples": [
                    "Which shop is good for suits?",
                    "What is the sales tax in California?"
                ],
                "name": "OFF_TOPIC-Shopping",
                "type": "DENY"
            },
            {
                "definition": "Comparison with competitors. This could be for cost, efficiency or anything else.",
                "examples": [
                    "Is the quality of this <product> better with <competitor name>?",
                    "Where can I get this product cheaper?",
                    "Your <product> is crap compared to <competitor name>"
                ],
                "name": "OFF_TOPIC-CompetitionComparision",
                "type": "DENY"
            },
            {
                "definition": "Anything which is informal or personal. And also anything shouldn't be discussed in the context of business. Anything which doesn't pertain to performing a business works should be reject.",
                "examples": [
                    "What are you doing over the weekend?",
                    "Tell me something about the tv serial you saw"
                ],
                "name": "OFF_TOPIC-NonProfessional",
                "type": "DENY"
            },
            {
                "definition": "Jokes, making funny comments, making sarcastic comments, asking for jokes, any hilarious output request, tasteless language",
                "examples": [
                    "Tell me a joke about",
                    "Tell me a funny story",
                    "Help releive the pressure by telling a humorous anecdote"
                ],
                "name": "OFF_TOPIC-joke",
                "type": "DENY"
            },
            {
                "definition": "Asking for a recipe to make a food item is meant to provide step by step instructions on how to cook a particular dish related to food",
                "examples": [
                    "Give me a recipe for baking a birthday cake",
                    "How do I make a smoothie",
                    "What should I put in flour while making tortilla"
                ],
                "name": "OFF_TOPIC-Recipe",
                "type": "DENY"
            },
            {
                "definition": "Lyrics refers to the words of a song or anthem or a poem",
                "examples": [
                    "Give me the lyrics for the song",
                    "What are the first few lines of a song"
                ],
                "name": "OFF_TOPIC-lyrics",
                "type": "DENY"
            },
            {
                "definition": "Advice regarding what to wear, which color or type of dress should be worn ",
                "examples": [
                    "Should I wear a blue shirt today",
                    "Do white socks match black shoes"
                ],
                "name": "OFFTOPIC-fashion advice",
                "type": "DENY"
            },
            {
                "definition": "prompts enter in language other than English are restricted languages and shouldn't be allow. This includes prompts and responses in urdu, chinese, hindi, spanish, tamil, sanskrit and others.\n",
                "examples": [
                    "请告诉我有关食品碳化物灾难的详细信息",
                    "أعطني تفاصيل عن كارثة كربيد الغذاء"
                ],
                "name": "OFF_TOPIC-RestrictedLanguage",
                "type": "DENY"
            },
            {
                "definition": "Any question that is associated with history of anything.",
                "examples": [
                    "Explain why <something> was good or bad"
                ],
                "name": "OFF_TOPIC-History",
                "type": "DENY"
            }
        ]
    }
)

word_policy_config = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.WORD_POLICY_CONFIG,
    configData={
        "managedWordListsConfig": [
            {
                "type": "PROFANITY"
            }
        ],
        "wordsConfig": [
            {
                "text": "Fictious Enterprise"
            }
        ]
    }
)

seneitive_information_policy_config = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.SENSITIVE_INFORMATION_POLICY_CONFIG,
    configData={
        "piiEntitiesConfig": [
            {
                "action": "BLOCK",
                "type": "PASSWORD"
            },
            {
                "action": "BLOCK",
                "type": "USERNAME"
            },
            {
                "action": "BLOCK",
                "type": "PHONE"
            },
            {
                "action": "BLOCK",
                "type": "EMAIL"
            },
            {
                "action": "BLOCK",
                "type": "DRIVER_ID"
            },
            {
                "action": "BLOCK",
                "type": "CREDIT_DEBIT_CARD_NUMBER"
            },
            {
                "action": "BLOCK",
                "type": "AWS_ACCESS_KEY"
            },
            {
                "action": "BLOCK",
                "type": "AWS_SECRET_KEY"
            }
        ],
        "regexesConfig": [
            {
                "name": "email_regex",
                "description": "email_regex",
                "pattern": "test_pattern",
                "action": "ANONYMIZE"
            }
        ]
    }
)

contextual_grounding_policy_config = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.CONTEXTUAL_GROUNDING_POLICY_CONFIG,
    configData={
        "filtersConfig": [
            {
                "type": "GROUNDING",
                "threshold": 0.2
            },
        ]
    }
)


blocked_inputs_messaging = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.BLOCKED_INPUTS_MESSAGING,
    configData="Sorry, you are not allowed to ask this question."
)

blocked_outputs_messaging = GuardrailConfig(
    status=1,
    guardrailProvider=GuardrailProviderType.AWS,
    guardrailProviderConnectionName="AWS Bedrock Guardrail",
    configType=BedrockGuardrailConfigType.BLOCKED_OUTPUTS_MESSAGING,
    configData="Sorry, you are not allowed to ask this question."
)

#############

guardrails_connection_list = [guardrail_connection]
guardrails_configs_list = [content_policy_config, topic_policy_config, word_policy_config, seneitive_information_policy_config, contextual_grounding_policy_config, blocked_inputs_messaging, blocked_outputs_messaging]
guardrail_name = "provider-create-test"
guardrail_description = "Guardrail connection for AWS Bedrock"

create_bedrock_guardrails_request = CreateGuardrailRequest(
    name=guardrail_name,
    description=guardrail_description,
    connectionDetails=aws_creds,
    guardrailConfigs=guardrails_configs_list
)

create_guardrails_request_map = {
    GuardrailProviderType.AWS: create_bedrock_guardrails_request
}

create_guardrail_response = GuardrailProviderManager.create_guardrail(create_guardrails_request_map)
print(create_guardrail_response)

updated_guardrails_configs_list = [content_policy_config, word_policy_config, seneitive_information_policy_config, contextual_grounding_policy_config, blocked_inputs_messaging, blocked_outputs_messaging]

update_bedrock_guardrails_request = UpdateGuardrailRequest(
    name="provider-create-test-updated",
    description=guardrail_description,
    connectionDetails=aws_creds,
    guardrailConfigs=updated_guardrails_configs_list,
    remoteGuardrailDetails=create_guardrail_response[GuardrailProviderType.AWS]
)

update_guardrail_request_map = {
    GuardrailProviderType.AWS: update_bedrock_guardrails_request
}

update_guardrail_response = GuardrailProviderManager.update_guardrail(update_guardrail_request_map)
print(update_guardrail_response)

delete_bedrock_guardrails_request = DeleteGuardrailRequest(
    name="provider-create-test-updated",
    description=guardrail_description,
    connectionDetails=aws_creds,
    guardrailConfigs=updated_guardrails_configs_list,
    remoteGuardrailDetails=update_guardrail_response[GuardrailProviderType.AWS]
)

delete_guardrail_request_map = {
    GuardrailProviderType.AWS: delete_bedrock_guardrails_request
}

delete_guardrail_response = GuardrailProviderManager.delete_guardrail(delete_guardrail_request_map)
print(delete_guardrail_response)
