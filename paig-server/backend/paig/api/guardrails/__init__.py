from enum import Enum


class GuardrailProvider(Enum):
    AWS = 'AWS'
    # TODO: enable these providers whenever they are implemented
    # LLAMA = 'LLAMA'
    # OPENAI = 'OPENAI'


class GuardrailConfigType(Enum):
    CONTENT_MODERATION = 'CONTENT_MODERATION'
    SENSITIVE_DATA = 'SENSITIVE_DATA'
    OFF_TOPIC = 'OFF_TOPIC'
    DENIED_TERMS = 'DENIED_TERMS'
    PROMPT_SAFETY = 'PROMPT_SAFETY'


def model_to_dict(model):
    """Quickly convert a SQLAlchemy model instance to a dictionary."""
    return {key: value for key, value in model.__dict__.items() if not key.startswith('_')}
