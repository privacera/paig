from typing import Any, Generic, Type, TypeVar
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import func
from core.database import Base
from typing import Union
ModelType = TypeVar("ModelType", bound=Base)
from sqlalchemy import desc
from sqlalchemy.orm import load_only, defer


class BaseOperations(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.session = db_session
        self.model_class: Type[ModelType] = model

    async def create(self, attributes) -> ModelType:
        model = self.model_class()
        # set attributes
        model.set_attribute(attributes)
        self.session.add(model)
        return model

    def _get_filter(self, filters):
        all_filters = []
        for field, value in filters.items():
            column = getattr(self.model_class, field, None)
            if column is not None:
                all_filters.append(column == value)
        return all_filters

    def create_filter(self, query, filters):
        if filters is not None:
            return query.filter(*self._get_filter(filters))
        else:
            return query

    def select_columns(self, query, columns):
        if columns is not None:
            cols = []
            for field in columns:
                column = getattr(self.model_class, field, None)
                if column is not None:
                    cols.append(column)
            return query.options(load_only(*cols))
        else:
            return query

    def order_by(self, query, field):
        if field is not None:
            column = getattr(self.model_class, field, None)
            return query.order_by(desc(column))
        else:
            return query

    async def get_all(self,
                      filters=None,
                      columns=None,
                      deferred_col=None,
                      order_by_field=None,
                      skip: Union[int, None] = None,
                      limit: Union[int, None] = None
                      ) -> list[ModelType]:
        # Usage: select all query executor
        query = await self._query()
        query = self.create_filter(query, filters)
        query = self.select_columns(query, columns)
        if deferred_col is not None:
            query = query.options(defer(getattr(self.model_class, deferred_col, None)))
        query = self.order_by(query, order_by_field)
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)
        return await self._all(query)

    async def get_count_with_filter(self, filters: dict):
        return await self.session.scalar(select(func.count()).filter(*self._get_filter(filters)).select_from(self.model_class))

    async def get_by(self, filters, unique: bool = False) -> ModelType:
        # Usage: get by id, username, etc
        query = await self._query()
        query = await self._get_by(query, filters)
        if unique:
            return await self._one(query)

        return await self._all(query)

    async def _query(self) -> Select:
        # Usage: Construct a query
        query = select(self.model_class)
        return query

    async def _all(self, query: Select) -> list[ModelType]:
        # return all result of query
        query = await self.session.scalars(query)
        return query.all()

    async def _one(self, query: Select) -> ModelType:
        # Usage: returns first record of the result else NoResultFound
        query = await self.session.scalars(query)
        return query.one()

    async def _get_by(self, query: Select, filters) -> Select:
        # Usage: executes actual query conditional select
        return query.where(*self._get_filter(filters))
