from api.governance.database.db_operations.ai_app_apikey_repository import AIAppAPIKeyRepository, \
    AIAppEncryptionKeyRepository
from core.utils import SingletonDepends


class AIAppAPIKeyService:

    def __init__(self, ai_app_apikey_repository: AIAppAPIKeyRepository = SingletonDepends(AIAppAPIKeyRepository),
                 ai_app_encryptionkey_repository: AIAppEncryptionKeyRepository = SingletonDepends(
                     AIAppEncryptionKeyRepository)
                 ):
       self.ai_app_apikey_repository = ai_app_apikey_repository
       self.ai_app_encryptionkey_repository = ai_app_encryptionkey_repository

    def create_app_encryption_key(self, app_id):
        return self.ai_app_encryptionkey_repository.create_encryption_key(app_id)