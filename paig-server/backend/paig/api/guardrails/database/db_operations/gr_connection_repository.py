from sqlalchemy import select

from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from core.db_session import session
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

    async def get_connection_providers(self):
        """
        Retrieve a list of distinct connection providers from the database.

        Returns:
            list[str]: A list of distinct connection providers.
        """
        query = select(GRConnectionModel.guardrail_provider).distinct()
        result = await session.execute(query)
        return result.scalars().all()
