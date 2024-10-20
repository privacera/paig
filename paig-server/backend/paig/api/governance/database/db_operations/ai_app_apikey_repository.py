import os

from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.ai_app_apikey_model import AIApplicationEncryptionKeyModel, AIApplicationAPIKeyModel


class AIAppEncryptionKeyRepository(BaseOperations[AIApplicationEncryptionKeyModel]):
    """
    Repository class for handling database operations related to AI application encryption key models.

    Inherits from BaseOperations[AIAppEncryptionKeyRepository], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[AIAppEncryptionKeyRepository].
    """

    def __init__(self):
        """
        Initialize the AIAppEncryptionKeyRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AIApplicationEncryptionKeyModel)

    def create_encryption_key(self, app_id):
        key = os.urandom(32)
        self.create_record(AIApplicationEncryptionKeyModel(application_id=app_id, key=key))

class AIAppAPIKeyRepository(BaseOperations[AIApplicationAPIKeyModel]):
    """
    Repository class for handling database operations related to AI application api key models.

    Inherits from BaseOperations[AIApplicationAPIKeyModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[AIApplicationAPIKeyModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AIApplicationAPIKeyModel)