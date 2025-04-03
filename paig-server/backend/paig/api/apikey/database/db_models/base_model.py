from enum import Enum

class EncryptionKeyStatus(Enum):
    ACTIVE = 'ACTIVE'
    PASSIVE = 'PASSIVE'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class ApiKeyStatus(Enum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'
