from datetime import datetime, timezone

from sqlalchemy import func, and_
from sqlalchemy.sql import select

from api.audit.RDS_service.db_models.admin_audit_model import AdminAuditModel
from api.audit.api_schemas.admin_audit_schema import BaseAdminAuditView
from core.db_session import session
from core.db_session.transactional import Transactional, Propagation
from core.factory.database_initiator import BaseOperations
from core.utils import get_field_name_by_alias, format_time_for_datetime_series


class AdminAuditRepository(BaseOperations[AdminAuditModel]):

    def __init__(self):
        """
        Initialize the AccessAuditRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AdminAuditModel)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_admin_audit(self, admin_audit_params: BaseAdminAuditView):
        if not isinstance(admin_audit_params, dict):
            admin_audit_params = admin_audit_params.model_dump()
        model = self.model_class()
        model.set_attribute(admin_audit_params)
        session.add(model)
        return model

    async def get_access_audits_with_filters(self, include_filters, exclude_filters, page, size, sort, min_value, max_value):
        all_filters = list()
        skip = 0 if page is None else (page * size)
        query = select(AdminAuditModel)
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
            all_filters.append(AdminAuditModel.log_time >= min_value)
        if max_value:
            all_filters.append(AdminAuditModel.log_time <= max_value)
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
                    field_names.append(get_field_name_by_alias(model=BaseAdminAuditView, alias=alias_name))
                sort_column_name = ",".join(field_names)
                query = self.order_by(query, sort_column_name, sort_type)
        query = query.limit(size).offset(skip)
        results = (await session.execute(query)).scalars().all()
        count = (await self.get_count_with_filter(include_filters.model_dump()))
        return results, count
