from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRApplicationVersionModel, \
    GRVersionHistoryModel
from core.factory.database_initiator import BaseOperations


class GuardrailRepository(BaseOperations[GuardrailModel]):
    """
    Repository class for handling database operations related to guardrail models.

    Inherits from BaseOperations[GuardrailModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GuardrailModel].
    """

    def __init__(self):
        """
        Initialize the GuardrailRepository.
        """
        super().__init__(GuardrailModel)


class GRVersionHistoryRepository(BaseOperations[GRVersionHistoryModel]):
    """
    Repository class for handling database operations related to guardrail history models.

    Inherits from BaseOperations[GRVersionHistoryModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRVersionHistoryModel].
    """

    def __init__(self):
        """
        Initialize the GuardrailHistoryRepository.
        """
        super().__init__(GRVersionHistoryModel)


class GRApplicationVersionRepository(BaseOperations[GRApplicationVersionModel]):
    """
    Repository class for handling database operations related to guardrail application version models.

    Inherits from BaseOperations[GRApplicationVersionModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRApplicationVersionModel].
    """

    def __init__(self):
        """
        Initialize the GRApplicationVersionRepository.
        """
        super().__init__(GRApplicationVersionModel)
