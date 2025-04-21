from sqlalchemy import and_
from ..db_models import EvaluationTargetModel
from core.factory.database_initiator import BaseOperations
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.future import select
from core.utils import current_utc_time, epoch_to_utc
from core.db_session import session
from core.middlewares.request_session_context_middleware import get_tenant_id

class EvaluationTargetRepository(BaseOperations[EvaluationTargetModel]):

    def __init__(self):
        """
        Initialize the EvaluationRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationTargetModel)

    async def get_application_list_with_filters(
            self,
            include_filters,
            exclude_filters,
            page: int,
            size: int,
            sort,
            min_value,
            max_value
    ):
        all_filters = list()
        skip = 0 if page is None else (page * size)
        query = select(EvaluationTargetModel)
        if exclude_filters:
            exclude_list = ''
            for key, value in exclude_filters.model_dump().items():
                if value:
                    exclude_list = exclude_list + ',' + key
            if exclude_list:
                exclude_filters.exclude_match = True
                exclude_filters.exclude_list = exclude_list
                query = self.create_filter(query, exclude_filters.model_dump())
        query = self.create_filter(query, include_filters.model_dump())
        if min_value:
            min_value = epoch_to_utc(min_value)
            all_filters.append(EvaluationTargetModel.create_time >= min_value)
        if max_value:
            max_value = epoch_to_utc(max_value)
            all_filters.append(EvaluationTargetModel.create_time <= max_value)
        tenant_id = get_tenant_id()
        all_filters.append(EvaluationTargetModel.tenant_id == tenant_id)
        if all_filters:
            query = query.filter(and_(*all_filters))
        if sort:
            if not isinstance(sort, list):
                sort = [sort]
            for sort_option in sort:
                column_name, sort_type = self.parse_sort_option(sort_option)
                alias_names = column_name.split(",")
                field_names = []
                for alias_name in alias_names:
                    field_names.append(alias_name)
                sort_column_name = ",".join(field_names)
                query = self.order_by(query, sort_column_name, sort_type)
        query = query.limit(size).offset(skip)
        results = (await session.execute(query)).scalars().all()
        filters = include_filters.model_dump()
        if 'create_time_to' in filters and max_value:
            filters['create_time_to'] = max_value
        if 'create_time_from' in filters and min_value:
            filters['create_time_from'] = min_value
        filters['tenant_id'] = tenant_id
        count = (await self.get_count_with_filter(filters))

        return results, count
        


    async def get_target_by_app_id(self, app_id: int):
        try:
            filters = {'application_id': app_id}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    async def get_target_by_id(self, target_id):
        try:
            filters = {'id': target_id}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    async def create_app_target(self, eval_target):
        target = EvaluationTargetModel(**eval_target)
        return await self.create_record(target)


    async def delete_target(self, target_model):
        return await self.delete(target_model)

    async def update_app_target(self, params, target_model):
        params['update_time']  = current_utc_time()
        target_model.set_attribute(params)
        return target_model

    async def get_target_hosts_by_in_list(self, field: str, values: list):
        try:
            apply_in_list_filter = True
            filters = {field: values}
            return await self.get_all(filters, apply_in_list_filter=apply_in_list_filter, columns=[EvaluationTargetModel.config, EvaluationTargetModel.application_id])
        except NoResultFound:
            return None

    async def get_applications_by_in_list(self, field: str, values: list):
        try:
            apply_in_list_filter = True
            filters = {field: values}
            return await self.get_all(filters, apply_in_list_filter=apply_in_list_filter)
        except NoResultFound:
            return None

    async def application_name_exists(self, name: str) -> bool:
        filters = {'name': name}
        try:
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None