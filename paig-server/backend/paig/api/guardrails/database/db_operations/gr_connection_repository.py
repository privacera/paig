from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails.database.db_models.guardrail_model import GRConnectionMappingModel
from core.factory.database_initiator import BaseOperations


class GRConnectionRepository(BaseOperations[GRConnectionModel]):
    """
    Repository class for handling database operations related to AI application models.

    Inherits from BaseOperations[GRConnectionModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRConnectionModel].
    """

    def __init__(self):
        """
        Initialize the GRConnectionRepository.
        """
        super().__init__(GRConnectionModel)


class GRConnectionMappingRepository(BaseOperations[GRConnectionMappingModel]):
    """
    Repository class for handling database operations related to AI application models.

    Inherits from BaseOperations[GRConnectionMappingModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRConnectionMappingModel].
    """

    def __init__(self):
        """
        Initialize the GRConnectionMappingRepository.
        """
        super().__init__(GRConnectionMappingModel)
