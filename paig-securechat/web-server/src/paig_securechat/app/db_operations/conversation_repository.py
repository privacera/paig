from app.db_models import Conversations
from core.factory.database_initiator import BaseOperations
from core.database.transactional import Transactional, Propagation


class ConversationRepository(BaseOperations[Conversations]):

    async def get_conversations(self, user_id, skip, limit):
        filters = {"user_id": user_id, "is_deleted": False}
        deferred_col = "is_deleted"
        return await self.get_all(filters=filters, order_by_field="id", deferred_col=deferred_col, skip=skip, limit=limit)

    async def get_conversations_count(self, user_id):
        filters = {"user_id": user_id, "is_deleted": False}
        return await self.get_count_with_filter(filters)

    async def get_conversation_by_uuid(self, conversation_uuid: str, user_id):
        filters = {"conversation_uuid": conversation_uuid, "is_deleted": False, "user_id": user_id}
        return await self.get_by(filters, unique=True)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_conversation(self, request_params):
        return await self.create(request_params)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_conversation(self, conversation_uuid: str):
        filters = {"conversation_uuid": conversation_uuid, "is_deleted": False}
        res = await self.get_by(filters, True)
        res.is_deleted = True
