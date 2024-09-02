from sqlalchemy.exc import NoResultFound
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.vector_db_model import VectorDBModel


class VectorDBRepository(BaseOperations[VectorDBModel]):
    """
    Repository class for handling database operations related to Vector DB models.

    Inherits from BaseOperations[VectorDBModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[VectorDBModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(VectorDBModel)

    async def get_vector_db_by_name(self, name: str) -> VectorDBModel:
        """
        Retrieve a Vector DB by its name.

        Args:
            name (str): The name of the Vector DB to retrieve.

        Returns:
            VectorDBModel: The Vector DB with the specified name.

        Raises:
            NoResultFound: If no Vector DB with the specified name is found.
        """
        try:
            return await self.get_by(filters={"name": name}, unique=True)
        except NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB", "name", name))