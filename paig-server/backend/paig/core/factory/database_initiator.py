from typing import Generic, Type, TypeVar, Tuple, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Select, asc, literal, text
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import func, false
from core.db_session.session import Base, session
from typing import Union

from datetime import datetime

from core.db_models.utils import CommaSeparatedList

ModelType = TypeVar("ModelType", bound=Base)
from sqlalchemy import desc
from sqlalchemy.orm import load_only, defer
from sqlalchemy import or_


class BaseAPIFilter(BaseModel):
    """
       A base filter for common fields shared across multiple filters.

       Attributes:
           id (Optional[int]): The unique identifier of the resource.
           status (Optional[int]): The status of the resource.
           create_time (Optional[datetime]): The creation time of the resource.
           update_time (Optional[datetime]): The last update time of the resource.
       """
    id: Optional[int] = Field(None, description="The unique identifier of the resource")
    status: Optional[int] = Field(None, description="The status of the resource")
    create_time_from: Optional[datetime] = Field(None, description="The creation time from of the resource", alias="createTimeFrom")
    create_time_to: Optional[datetime] = Field(None, description="The creation time to of the resource", alias="createTimeTo")
    update_time_from: Optional[datetime] = Field(None, description="The last update time from of the resource", alias="updateTimeFrom")
    update_time_to: Optional[datetime] = Field(None, description="The last update time to of the resource", alias="updateTimeTo")
    exact_match: Optional[bool] = Field(False, description="The exact match of the resource", alias="exactMatch")
    exclude_match: Optional[bool] = Field(False, description="The exclude match of the resource", alias="excludeMatch")
    exclude_list: Optional[str] = Field(None, description="The exclude list of the resource", alias="excludeList")


class BaseOperations(Generic[ModelType]):

    def __init__(self, model: Type[ModelType]):
        self.model_class: Type[ModelType] = model

    async def create(self, attributes) -> ModelType:
        model = self.model_class()
        # set attributes
        model.set_attribute(attributes)
        session.add(model)
        return model

    def _get_filter(self, filters, apply_in_list_filter=False):
        all_filters = []
        for field, value in filters.items():
            filter_data = self.process_filters(filters, field, value, apply_in_list_filter)
            if filter_data is not None:
                all_filters.append(filter_data)

        # Handle datetime range filters separately
        self._add_datetime_filters('create_time', filters, all_filters)
        self._add_datetime_filters('update_time', filters, all_filters)

        # handle lookup_columns
        self.handle_lookup_columns(all_filters, filters, apply_in_list_filter)

        return all_filters

    def process_filters(self, filters, field, value, apply_in_list_filter):
        column = getattr(self.model_class, field, None)
        if column is not None and value is not None:
            if isinstance(column.type, CommaSeparatedList):
                return self._process_comma_separated_list(column, value, filters)
            else:
                if isinstance(value, str) and "," in value:
                    return self._process_multi_value_filter(column, value, filters, field)
                else:
                    return self._process_single_value_filter(column, value, filters, apply_in_list_filter, field)

    def handle_lookup_columns(self, all_filters, filters, apply_in_list_filter):
        if 'lookup_columns' in filters:
            lookup_columns = filters['lookup_columns']
            for field in lookup_columns:
                value = filters[field]
                if value is not None:
                    column_filters = []
                    columns = lookup_columns[field]
                    for column in columns:
                        filter_data = self.process_filters(filters, column, value, apply_in_list_filter)
                        if filter_data is not None:
                            column_filters.append(filter_data)
                    all_filters.append(or_(*column_filters))

    def _add_datetime_filters(self, field_name, filters, all_filters):
        column = getattr(self.model_class, field_name, None)
        if column is not None:
            if f'{field_name}_from' in filters and filters[f'{field_name}_from'] is not None:
                all_filters.append(column >= filters[f'{field_name}_from'])
            if f'{field_name}_to' in filters and filters[f'{field_name}_to'] is not None:
                all_filters.append(column <= filters[f'{field_name}_to'])

    def _process_comma_separated_list(self, column, value, filters):
        all_filters = []
        for val in value.split(","):
            if filters.get('exact_match') is False:
                all_filters.append(column.like('%' + val + '%'))
            elif filters.get('exclude_match'):
                all_filters.append(column != val)
            else:
                all_filters.append(or_(
                    column.like(val),
                    column.like(val + ',%'),
                    column.like('%,' + val + ',%'),
                    column.like('%,' + val)
                ))
        return or_(*all_filters)

    def _process_multi_value_filter(self, column, value, filters, field=None):
        multi_val_filter = []
        for val in value.split(","):
            multi_val_filter.append(self._process_single_value_filter(column, val, filters, field))
        return or_(*multi_val_filter)

    def _process_single_value_filter(self, column, value, filters, apply_in_list_filter=False, field=None):
        if apply_in_list_filter and isinstance(value, list):
            return column.in_(value)
        elif self._is_col_excluded(filters, field):
            if filters.get('exact_match'):
                return column != value
            else:
                return column.notlike('%' + value + '%')
        elif isinstance(value, str) and filters.get('exact_match') is False:
            return column.like('%' + value + '%')
        else:
            return column == value

    @staticmethod
    def _is_col_excluded(filters, field):
        exclude_flag = filters.get('exclude_match')
        exclude_list = filters.get('exclude_list')
        if exclude_flag and exclude_list:
            exclude_list = exclude_list.split(',')
            return field in exclude_list
        return exclude_flag

    def create_filter(self, query, filters, apply_in_list_filter=False):
        if filters is not None:
            return query.filter(*self._get_filter(filters, apply_in_list_filter))
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

    def order_by(self, query, fields, sort_type="asc"):
        if fields:
            for field in fields.split(','):
                field = field.strip()  # Remove any extra spaces around the field name
                column = getattr(self.model_class, field, None)
                if column is not None:
                    sort = asc(column) if sort_type.lower() == "asc" else desc(column)
                    query = query.order_by(sort)
        return query

    def parse_sort_option(self, sort_option: str) -> Tuple[str, str]:
        if "," in sort_option:
            splited = sort_option.split(",")
            column_name = splited[0]
            if splited[-1].lower() in ["asc", "desc"]:
                sort_type = splited[-1].lower()
                column_name = ",".join(splited[:-1])  # in case the column name has commas
            else:
                sort_type = "asc"  # default sort type
        else:
            column_name = sort_option
            sort_type = "asc"  # default sort type
        return column_name, sort_type

    def apply_order_by_field(self, query, order_by_field):
        if not isinstance(order_by_field, list):
            order_by_field = [order_by_field]
        for sort_option in order_by_field:
            column_name, sort_type = self.parse_sort_option(sort_option)
            query = self.order_by(query, column_name, sort_type)
        return query

    async def get_all(self,
                      filters=None,
                      columns=None,
                      deferred_col=None,
                      order_by_field=None,
                      skip: Union[int, None] = None,
                      limit: Union[int, None] = None,
                      apply_in_list_filter=False,
                      **kwargs
                      ) -> list[ModelType]:
        # Usage: select all query executor
        query = await self._query()
        query = self.create_filter(query, filters, apply_in_list_filter)
        query = self.select_columns(query, columns)
        if deferred_col is not None:
            query = query.options(defer(getattr(self.model_class, deferred_col, None)))

        if 'relation_load_options' in kwargs and kwargs['relation_load_options']:
            query = query.options(*kwargs['relation_load_options'])

        if order_by_field:
            query = self.apply_order_by_field(query, order_by_field)

        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        cardinality = kwargs.get('cardinality')
        if cardinality:
            query = query.distinct(text(cardinality)).group_by(text(cardinality))

        return await self._all(query)

    async def get_count_with_filter(self, filters: dict):
        return await session.scalar(select(func.count()).filter(*self._get_filter(filters)).select_from(self.model_class))

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
        query = await session.scalars(query)
        return query.all()

    async def _one(self, query: Select) -> ModelType:
        # Usage: returns first record of the result else NoResultFound
        query = await session.scalars(query)
        return query.one()

    async def _get_by(self, query: Select, filters) -> Select:
        # Usage: executes actual query conditional select
        return query.where(*self._get_filter(filters))

    # CRUD Operations
    async def list_records(
        self,
        filter: BaseAPIFilter = None,
        page_number: int = None,
        size: int = None,
        sort: List[str] = None,
        **kwargs
    ) -> Tuple[List[ModelType], int]:
        """
        List records with pagination and sorting.

        This method retrieves records based on the provided filters, page number,
        page size, and sorting criteria. It returns a tuple containing a list of
        records and the total count of records that match the filters.

        Args:
            filter (BaseAPIFilter): The filters to apply to the query. This should be an instance of `APIFilters` containing the filtering criteria.
            page_number (int): The page number for pagination. The number of records to skip is calculated as `page_number * size`.
            size (int): The number of records to return per page.
            sort (List[str]): The fields by which to sort the records. This should be a list of field names.

        Returns:
            Tuple[List[ModelType], int]: A tuple containing:
                - A list of records (`ModelType`) that match the filters, sorted and paginated.
                - The total count of records that match the filters.
        """
        skip = 0 if page_number is None else (page_number * size)

        # check if the filter has model fields and if model field has json_schema_extra lookup_columns then fill filter_dict with those fields
        filter_dict = filter.model_dump()
        lookup_columns_dict = {}

        for field in filter.model_fields:
            value = getattr(filter, field)
            extra_params = filter.model_fields[field].json_schema_extra
            if value is not None and extra_params is not None and 'lookup_columns' in extra_params:
                lookup_columns_dict[field] = extra_params['lookup_columns']

        filter_dict['lookup_columns'] = lookup_columns_dict

        result = await self.get_all(
            filters=filter_dict,
            skip=skip,
            limit=size,
            order_by_field=sort,
            **kwargs
        )
        total_count = await self.get_count_with_filter(filters=filter_dict)
        return result, total_count

    async def create_record(self, model: ModelType) -> ModelType:
        """
        Create a new record in the database.

        This method adds the provided model instance to the database session and
        returns the model instance. The actual commit to the database must be
        handled outside this method.

        Args:
            model (ModelType): The model instance to be added to the database.

        Returns:
            ModelType: The model instance that was added to the session.
        """
        session.add(model)
        await session.flush()
        return await self.get_record_by_id(model.id)

    async def get_record_by_id(self, id: int) -> ModelType:
        """
        Retrieve a record from the database by its ID.

        This method constructs a filter based on the provided ID and retrieves
        the corresponding record from the database.

        Args:
            id (int): The unique identifier of the record to retrieve.

        Returns:
            ModelType: The model instance that matches the given ID.

        Raises:
            sqlalchemy.exc.NoResultFound: If no record is found with the given ID.
        """
        filters = {"id": id}
        return await self.get_by(
            filters=filters,
            unique=True
        )

    async def update_record(self, updated_model: ModelType) -> ModelType:
        """
        Update an existing record in the database.

        This method takes an updated model instance, adds it to the session,
        and returns the updated model instance. It is expected that the
        `updated_model` contains the necessary changes.

        Args:
            updated_model (ModelType): The model instance with updated data.

        Returns:
            ModelType: The updated model instance.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If there is an issue with updating the record in the database.
        """
        session.add(updated_model)
        return updated_model

    async def delete_record(self, model: ModelType) -> None:
        """
        Deletes the specified model from the database.

        This method deletes the provided model instance from the session and
        eventually from the database. The model instance must be a valid
        instance that is part of the current session.

        Args:
            model (ModelType): The model instance to delete.

        Returns:
            None

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If there is an issue with deleting the record from the database.
        """
        await session.delete(model)

    async def update(self, attributes) -> ModelType:
        # send all required attributes to update
        model = self.model_class()
        model.set_attribute(attributes)
        return model

    async def delete(self, model: ModelType) -> None:
        await session.delete(model)

    async def generate_datetime_series(self, start_time, end_time, interval):
        # Generate a series of datetime
        # Base case: select the start time
        base_query = select(literal(start_time).label('date'))
        # Recursive case: increment the date by the interval
        date_series_cte = base_query.cte(name='date_series', recursive=True)
        recursive_query = select(
            func.datetime(date_series_cte.c.date, text(f"'{interval}'")).label('date')
        ).where(func.datetime(date_series_cte.c.date, text(f"'{interval}'")) <= text(f"'{end_time}'"))
        # Define the CTE
        query = date_series_cte.union_all(recursive_query)
        return query