from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.ai_app_model import AIApplicationModel


class AIAppRepository(BaseOperations[AIApplicationModel]):
    """
    Repository class for handling database operations related to AI application models.

    Inherits from BaseOperations[AIApplicationModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[AIApplicationModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AIApplicationModel)

    async def get_ai_application_by_application_key(self, application_key: str) -> AIApplicationModel:
        """
        Retrieve an AI application by its application key.

        Args:
            application_key (str): The application key to search for.

        Returns:
            AIApplicationModel: The AI application with the specified application key.

        Raises:
            NoResultFound: If no AI application with the specified application key is found.
        """
        try:
            return await self.get_by(filters={"application_key": application_key}, unique=True)
        except NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "AI Application", "applicationKey", application_key))

    async def get_ai_application_with_host(self, search_filters, page, size, sort):
        results, count = await self.list_records(search_filters, page, size, sort,
                                                 relation_load_options=[selectinload(self.model_class.host)])
        return results, count

    async def get_ai_application_names_by_in_list(self, field: str, values: list):
        try:
            return await self.get_all({field: values}, apply_in_list_filter=True)
        except NoResultFound:
            return None