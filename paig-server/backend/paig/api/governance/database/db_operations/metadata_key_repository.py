from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.metadata_key_model import VectorDBMetaDataKeyModel


class MetadataKeyRepository(BaseOperations[VectorDBMetaDataKeyModel]):
    """
    Repository class for handling database operations related to VectorDB Metadata Key models.

    Inherits from BaseOperations[VectorDBMetaDataKeyModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[VectorDBMetaDataKeyModel].
    """

    def __init__(self):
        """
        Initialize the MetadataRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(VectorDBMetaDataKeyModel)