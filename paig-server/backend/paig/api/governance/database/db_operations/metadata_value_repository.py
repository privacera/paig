from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.metadata_value_model import VectorDBMetaDataValueModel


class MetadataValueRepository(BaseOperations[VectorDBMetaDataValueModel]):
    """
    Repository class for handling database operations related to Vector DB Metadata attribute value models.

    Inherits from BaseOperations[VectorDBMetaDataValueModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[VectorDBMetaDataValueModel].
    """

    def __init__(self):
        """
        Initialize the MetadataRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(VectorDBMetaDataValueModel)