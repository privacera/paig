from api.user.database.db_models import User
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from core.utils import current_utc_time
from core.db_session import session

class UserRepository(BaseOperations[User]):

    def __init__(self):
        """
        Initialize the UserRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(User)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_user(self, user_params, groups):
        user_params['create_time'] = current_utc_time()
        model = self.model_class()
        model.set_attribute(user_params)
        if groups:
            model.groups.extend(groups)
        session.add(model)
        return model

    async def get_user(self, username: [str, None] = None, id: [int, None] = None):
        try:
            filters = dict()
            if username is not None:
                filters["username"] = username
            if id is not None:
                filters["id"] = id
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    async def get_user_by_field(self, field: str, value: str):
        try:
            filters = {field: value}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    async def get_all_users(self, **args):
        return await self.get_all(**args)

    async def get_users_with_groups(self, search_filters, page, size, sort):
        results, count = await self.list_records(search_filters, page, size, sort, relation_load_options=[selectinload(self.model_class.groups)])
        return results, count

    async def get_user_with_related_data(self, user_id: int):
        query = select(self.model_class).filter(self.model_class.id == user_id).options(selectinload(self.model_class.groups))
        result = await session.scalars(query)
        result = result.one()
        return result

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_user(self, user_params, user_model):
        user_params['update_time'] = current_utc_time()
        user_model.set_attribute(user_params)
        return user_model

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_user(self, user_id):
        return await self.delete(user_id)
