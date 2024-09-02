from api.user.database.db_models import Groups, GroupMembers
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func, delete, and_
from sqlalchemy.future import select
from core.utils import current_utc_time
from core.db_session import session


class GroupRepository(BaseOperations[Groups]):

    def __init__(self):
        """
        Initialize the GroupRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(Groups)

    async def get_all_groups(self):
        return await self.get_all()

    async def get_groups_with_members_count(self, search_filters, page_number, size, sort):
        subquery = (
            select(
                GroupMembers.group_id, func.count(GroupMembers.user_id).label("usersCount")
            )
            .group_by(GroupMembers.group_id)
            .subquery()
        )
        query = select(
                    Groups.id,
                    Groups.name,
                    Groups.description,
                    Groups.create_time,
                    Groups.update_time,
                    subquery.c.usersCount,
                )
        query = self.create_filter(query, search_filters.model_dump())
        query = self.apply_order_by_field(query, sort)
        skip = 0 if page_number is None else (page_number * size)
        query = query.limit(size)
        query = query.offset(skip)
        results = (
            await session.execute(
                query.outerjoin(subquery, Groups.id == subquery.c.group_id)
            )
        ).all()
        total_count = await self.get_count_with_filter(filters=search_filters.model_dump())
        return results, total_count

    async def get_group(self, id: [int, None] = None, filters: [dict, None] = None, unique: bool = True):
        try:
            if filters is None:
                filters = dict()
            if id is not None:
                filters["id"] = id
            return await self.get_by(filters, unique=unique)
        except NoResultFound:
            return None

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_group(self, group_params):
        group_params['update_time'] = current_utc_time()
        group_params['create_time'] = current_utc_time()
        model = await self.create(group_params)
        return model

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_group(self, group_model):
        group_model.update_time = current_utc_time()
        return group_model

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_group(self, group_model):
        return await self.delete(group_model)

    async def get_groups_by_in_list(self, field: str, values: list):
        try:
            apply_in_list_filter = True
            filters = {field: values}
            return await self.get_all(filters, apply_in_list_filter=apply_in_list_filter)
        except NoResultFound:
            return None


class GroupMemberRepository(BaseOperations[GroupMembers]):

    def __init__(self):
        """
        Initialize the GroupMemberRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(GroupMembers)

    async def get_group_members(self, id: [int, None] = None, filters: [dict, None] = None, unique: bool = True):
        try:
            if filters is None:
                filters = dict()
            if id is not None:
                filters["id"] = id
            return await self.get_by(filters, unique=unique)
        except NoResultFound:
            return None

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_group_member(self, group_member_params):
        group_member_params['update_time'] = current_utc_time()
        group_member_params['create_time'] = current_utc_time()
        model = await self.create(group_member_params)
        return model

    @Transactional(propagation=Propagation.REQUIRED)
    async def save_in_bulk(self, new_members_to_add, group_id):
        model_list = [self.model_class(**{'group_id': group_id,
                                          'user_id': user_id,
                                          'create_time': current_utc_time(),
                                          'update_time': current_utc_time()}
                                       ) for user_id in new_members_to_add
                      ]
        model = session.add_all(model_list)
        return model

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_group_member(self, group_member_model):
        return await self.delete(group_member_model)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_in_bulk(self, group_id, members_to_remove):
        statement = delete(self.model_class).where(
            and_(
                self.model_class.group_id == group_id,
                self.model_class.user_id.in_(members_to_remove)
            )
        )
        result = await session.execute(statement)

        # Retrieve the affected row count
        affected_rows = result.rowcount
        return affected_rows
