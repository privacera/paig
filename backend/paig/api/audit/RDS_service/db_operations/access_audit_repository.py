from datetime import datetime, timezone
from api.audit.RDS_service.db_models.access_audit_model import AccessAuditModel
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy import func, and_, cast, String
from core.db_session import session
from api.audit.api_schemas.access_audit_schema import BaseAccessAuditView
from core.utils import get_field_name_by_alias, format_time_for_datetime_series
from sqlalchemy.sql import true, select




class AccessAuditRepository(BaseOperations[AccessAuditModel]):

    def __init__(self):
        """
        Initialize the AccessAuditRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AccessAuditModel)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_access_audit(self, access_audit_params: BaseAccessAuditView):
        if not isinstance(access_audit_params, dict):
            access_audit_params = access_audit_params.model_dump()
        model = self.model_class()
        model.set_attribute(access_audit_params)
        session.add(model)
        return model

    async def _build_datetime_series(self, min_value, max_value, interval):
        formatted_date = func.datetime(AccessAuditModel.event_time/1000, 'unixepoch')
        formatted_start_time = datetime.fromtimestamp(min_value/1000, timezone.utc)
        formatted_end_time = datetime.fromtimestamp(max_value/1000, timezone.utc)
        (
            offset_interval,
            formatted_start_time,
            formatted_end_time,
            formatted_time
        ) = format_time_for_datetime_series(
            interval,
            formatted_start_time,
            formatted_end_time,
            formatted_date
        )
        formatted_ms = func.strftime('%s', formatted_time)
        cte = await self.generate_datetime_series(formatted_start_time, formatted_end_time, offset_interval)
        return cte, formatted_ms

    async def get_access_audits_with_filters(self, include_filters, exclude_filters, page, size, sort, min_value, max_value):
        all_filters = list()
        skip = 0 if page is None else (page * size)
        query = select(AccessAuditModel)
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
            all_filters.append(AccessAuditModel.event_time >= min_value)
        if max_value:
            all_filters.append(AccessAuditModel.event_time <= max_value)
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
                    field_names.append(get_field_name_by_alias(model=BaseAccessAuditView, alias=alias_name))
                sort_column_name = ",".join(field_names)
                query = self.order_by(query, sort_column_name, sort_type)
        query = query.limit(size).offset(skip)
        results = (await session.execute(query)).scalars().all()
        count = (await self.get_count_with_filter(include_filters.model_dump()))
        return results, count

    async def get_access_audits_counts_group_by_result(self, filters, min_value, max_value):
        query = select(
            AccessAuditModel.result.label("result"), func.count(AccessAuditModel.result).label("count")
        )

        query = query.group_by(AccessAuditModel.result)

        filters = self._get_filter(filters.model_dump())

        query = query.filter(
            and_(
                *filters,
                AccessAuditModel.event_time >= min_value,
                AccessAuditModel.event_time <= max_value
            )
        )
        results = (await session.execute(query)).all()
        return results

    async def get_access_audits_counts_group_by_traits_and_application(self, filters, min_value, max_value):
        json_each = func.json_each(AccessAuditModel.traits).table_valued('value')
        query = (
            select(
                json_each.c.value.label('trait'),
                AccessAuditModel.app_name.label("app_name"),
                func.count().label('count')
            )
            .select_from(AccessAuditModel)
            .join(json_each, true())
            .group_by(*[json_each.c.value, AccessAuditModel.app_name])
        )

        query = self.create_filter(query, filters)
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_value,
                AccessAuditModel.event_time <= max_value
            )
        )
        results = (await session.execute(query)).all()
        return results

    async def get_access_audits_counts_group_by_result_interval(self, filters, min_value, max_value, interval):
        cte, formatted_ms = await self._build_datetime_series(min_value, max_value, interval)
        query = select(
            AccessAuditModel.result.label("result"),
            func.count(AccessAuditModel.result).label("count"),
            formatted_ms.label("interval"),
            AccessAuditModel.event_time.label("event_time")
        )
        query = query.group_by(*[AccessAuditModel.result, formatted_ms])
        query = self.create_filter(query, filters)
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_value,
                AccessAuditModel.event_time <= max_value
            )
        )
        subquery = (
            query.subquery()
        )
        main_query = select(
                cast(func.strftime('%s', cte.c.date)*1000, String), subquery.c.result, subquery.c.count
        )
        query = main_query.outerjoin(subquery, subquery.c.interval == func.strftime('%s', cte.c.date))
        results = (await session.execute(query)).all()
        return results
        
    async def get_access_audits_counts_group_by_user_id(self, size):
        query = select(
            AccessAuditModel.user_id.label("user_id"),
            func.count().label('count')
        )
        query = query.group_by(AccessAuditModel.user_id)
        query = query.order_by(func.count().desc())
        query = query.limit(size)
        results = (await session.execute(query)).all()
        return results

    async def get_access_audits_counts_group_by_app_name(self, size):
        query = select(
            AccessAuditModel.app_name.label("app_name"),
            func.count().label('count')
        )
        query = query.group_by(AccessAuditModel.app_name)
        query = query.order_by(func.count().desc())
        query = query.limit(size)
        results = (await session.execute(query)).all()
        return results

    async def get_access_audits_counts_group_by_app_name_and_user_id(self, filters, min_value, max_value):
        query = select(
            AccessAuditModel.app_name.label("app_name"),
            AccessAuditModel.user_id.label("user_id"),
            func.count(AccessAuditModel.app_name).label('app_name_count'),
            func.count(AccessAuditModel.user_id).label('user_id_count')
        )
        query = query.group_by(AccessAuditModel.app_name, AccessAuditModel.user_id)
        query = self.create_filter(query, filters.model_dump())
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_value,
                AccessAuditModel.event_time <= max_value
            )
        )
        results = (await session.execute(query)).all()
        return results

    async def get_access_audits_top_users_count_group_by_id(self, filters, size, min_time, max_time):
        query = select(
            AccessAuditModel.user_id.label("user_id"),
            func.count().label('count')
        )
        query = query.group_by(AccessAuditModel.user_id)
        query = self.create_filter(query, filters.model_dump())
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_time,
                AccessAuditModel.event_time <= max_time
            )
        )
        query = query.order_by(func.count().desc())
        query = query.limit(size)
        results = (await session.execute(query)).all()
        return results

    async def get_audits_counts_unique_user_id_count(self, filters, min_time, max_time):
        query = select(
            func.count(AccessAuditModel.user_id).label('count')
        )
        query = query.group_by(AccessAuditModel.user_id)
        query = self.create_filter(query, filters.model_dump())
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_time,
                AccessAuditModel.event_time <= max_time
            )
        )
        results = (await session.execute(query)).scalar()
        return results

    async def get_audits_counts_unique_trait_count(self, filters, min_time, max_time):
        json_each = func.json_each(AccessAuditModel.traits).table_valued('value')
        query = (
            select(
                json_each.c.value.label('trait'),
                func.count().label('count')
            )
            .select_from(AccessAuditModel)
            .join(json_each, true())
            .group_by(json_each.c.value)
        )
        query = self.create_filter(query, filters.model_dump())
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_time,
                AccessAuditModel.event_time <= max_time
            )
        )
        results = (await session.execute(query)).all()
        return results

    async def get_activity_trend_counts(self, filters, min_value, max_value, interval):
        cte, formatted_ms = await self._build_datetime_series(min_value, max_value, interval)
        query = select(
            func.count('*').label("count"),
            formatted_ms.label("interval"),
            AccessAuditModel.event_time.label("event_time")
        )
        query = query.group_by(*[formatted_ms])
        query = self.create_filter(query, filters)
        query = query.filter(
            and_(
                AccessAuditModel.event_time >= min_value,
                AccessAuditModel.event_time <= max_value
            )
        )
        subquery = (
            query.subquery()
        )
        main_query = select(
            cast(func.strftime('%s', cte.c.date) * 1000, String), subquery.c.count
        )
        query = main_query.outerjoin(subquery, subquery.c.interval == func.strftime('%s', cte.c.date))
        results = (await session.execute(query)).all()
        return results