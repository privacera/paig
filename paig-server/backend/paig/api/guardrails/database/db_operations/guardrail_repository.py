from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRConfigModel, \
    GRProviderResponseModel, GuardrailViewModel
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


class GRConfigRepository(BaseOperations[GRConfigModel]):
    """
    Repository class for handling database operations related to guardrail config models.

    Inherits from BaseOperations[GRConfigModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRConfigModel].
    """

    def __init__(self):
        """
        Initialize the GRConfigRepository.
        """
        super().__init__(GRConfigModel)


class GRProviderResponseRepository(BaseOperations[GRProviderResponseModel]):
    """
    Repository class for handling database operations related to guardrail provider response models.

    Inherits from BaseOperations[GRProviderResponseModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GRProviderResponseModel].
    """

    def __init__(self):
        """
        Initialize the GRProviderResponseRepository.
        """
        super().__init__(GRProviderResponseModel)


class GuardrailViewRepository(BaseOperations[GuardrailViewModel]):
    """
    Repository class for handling database operations related to guardrail view models.

    Inherits from BaseOperations[GuardrailViewModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[GuardrailViewModel].
    """

    def __init__(self):
        """
        Initialize the GuardrailRepository.
        """
        super().__init__(GuardrailViewModel)