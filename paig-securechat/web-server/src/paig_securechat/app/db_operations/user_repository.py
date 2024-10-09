from app.db_models import User
from core.factory.database_initiator import BaseOperations
from core.database.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound


class UserRepository(BaseOperations[User]):
    @Transactional(propagation=Propagation.REQUIRED)
    async def create_user(self, user_params):
        model = await self.create(user_params)
        return model

    async def get_user_by_user_name(self, user_name: str):
        try:
            filters = {"user_name": user_name}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    async def get_user(self, user_name: str, user_id: str):
        try:
            filters = {"user_name": user_name, "user_id": user_id}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None