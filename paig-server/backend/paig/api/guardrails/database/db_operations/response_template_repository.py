from core.factory.database_initiator import BaseOperations
from api.guardrails.database.db_models.response_template_model import ResponseTemplateModel


class ResponseTemplateRepository(BaseOperations[ResponseTemplateModel]):
    """
    Repository class for handling database operations related to ResponseTemplate models.

    Inherits from BaseOperations[ResponseTemplateModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[ResponseTemplateModel].
    """

    def __init__(self):
        """
        Initialize the ResponseTemplateRepository.
        """
        super().__init__(ResponseTemplateModel)
