from sqlalchemy.exc import NoResultFound
from core.exceptions import NotFoundException
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

    async def create_encryption_key(self, new_record):
        record = await self.create_record(new_record)
        return record

    async def get_valid_encryption_keys(self, app_id):
        try:
            filters = {"application_id": app_id, "status": 1}
            return await self.get_all(filters=filters, order_by="created_at", desc=True)
        except NoResultFound:
            return None


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

    def create_api_key(self, new_record):
        record = self.create_record(new_record)
        return record