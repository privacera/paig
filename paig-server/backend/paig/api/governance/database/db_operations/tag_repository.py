from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.tag_model import TagModel


class TagRepository(BaseOperations[TagModel]):
    """
    Repository class for handling database operations related to Tag models.

    Inherits from BaseOperations[TagModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[TagModel].
    """

    def __init__(self):
        """
        Initialize the TagRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(TagModel)