from app.db_models import Messages
from core.factory.database_initiator import BaseOperations
from core.database.transactional import Transactional, Propagation


class MessageRepository(BaseOperations[Messages]):
    # Usage: Queries that are related to message table

    async def get_messages_by_conversation_id(self, conversation_id: str, skip: int = 0, limit: int = 1000) -> str:
        # Usage: get message by message id
        filters = {"conversation_id": conversation_id}
        return await self.get_all(filters=filters, order_by_field="id", skip=skip, limit=limit)

    async def get_messages_count(self, conversation_id: str) -> str:
        filters = {"conversation_id": conversation_id}
        return await self.get_count_with_filter(filters)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_message(self, request_params):
        return await self.create(request_params)
