from enum import Enum


class GuardrailProvider(Enum):
    AWS = 'AWS'
    PAIG = 'PAIG'
    LLAMA = 'LLAMA'
    OPENAI = 'OPENAI'
    MULTIPLE = 'MULTIPLE'


class GuardrailConfigType(Enum):
    CONTENT_MODERATION = 'contentModeration'
    SENSITIVE_DATA = 'sensitiveData'
    OFF_TOPIC = 'offTopic'
    DENIED_TERMS = 'deniedTerms'
    PROMPT_SAFETY = 'promptSafety'
