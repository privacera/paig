from core.factory.database_initiator import BaseOperations
from api.governance.api_schemas.ai_app_config import AIApplicationConfigFilter
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel


class AIAppConfigRepository(BaseOperations[AIApplicationConfigModel]):
    """
    Repository class for handling database operations related to AI application config models.

    Inherits from BaseOperations[AIApplicationConfigModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[AIApplicationConfigModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AIApplicationConfigModel)

    async def get_ai_app_config_by_ai_application_id(self, application_id: int):
        """
        Get the AI application config by AI application ID.

        Args:
            application_id (int): The ID of the AI application.

        Returns:
            AIApplicationConfigModel: The AI application config model.
        """
        filter = AIApplicationConfigFilter(application_id=application_id)
        records, total_count = await self.list_records(filter=filter)
        ai_app_config = records[0] if records else None
        return ai_app_config