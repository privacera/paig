from enum import Enum


class RequestType(Enum):
    PROMPT = 'prompt'
    REPLY = 'reply'
    ENRICHED_PROMPT = 'enriched-prompt'
    RAG = 'rag'


class Guardrail(Enum):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    GUARDRAIL_INTERVENED = 'GUARDRAIL_INTERVENED'
    NONE = 'NONE'
    BLOCKED = 'BLOCKED'
