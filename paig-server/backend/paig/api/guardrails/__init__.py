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
    """
    Quickly convert a SQLAlchemy model instance to a dictionary.

    Args:
        model: The SQLAlchemy model instance to convert.

    Returns:
        dict: The dictionary representation of the model instance
    """
    return {key: value for key, value in model.__dict__.items() if value and not key.startswith('_')}


def dict_to_model(dict, model_type):
    """
    Convert a dictionary by filtering out invalid column to a SQLAlchemy model instance.

    Args:
        dict: The dictionary to convert.
        model_type: The SQLAlchemy model type to convert to.

    Returns:
        model_type: The SQLAlchemy model instance.
    """
    valid_columns = set(model_type.__table__.columns.keys())
    filtered_dict = {k: v for k, v in dict.items() if k in valid_columns}
    return model_type(**filtered_dict)
