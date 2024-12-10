from core.factory.database_initiator import BaseOperations
from api.guardrails.database.db_models.gr_sensitive_data_model import GRSensitiveDataModel


class GRSensitiveDataRepository(BaseOperations[GRSensitiveDataModel]):
    """
    Repository class for handling database operations related to GRSensitiveData models.

    Inherits from BaseOperations[GRSensitiveDataModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRSensitiveDataModel].
    """

    def __init__(self):
        """
        Initialize the GRSensitiveDataRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(GRSensitiveDataModel)