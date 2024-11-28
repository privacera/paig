from enum import Enum


class GuardrailProvider(Enum):
    AWS = 'AWS'
    PAIG = 'PAIG'
    LLAMA = 'LLAMA'
    OPENAI = 'OPENAI'
    MULTIPLE = 'MULTIPLE'


class GuardrailConfigType(Enum):
    CONTENT_MODERATION = 'CONTENT_MODERATION'
    SENSITIVE_DATA = 'SENSITIVE_DATA'
    OFF_TOPIC = 'OFF_TOPIC'
    DENIED_TERMS = 'DENIED_TERMS'
    PROMPT_SAFETY = 'PROMPT_SAFETY'
