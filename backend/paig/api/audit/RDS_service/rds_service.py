from api.audit.RDS_service.db_operations.access_audit_repository import AccessAuditRepository
from core.exceptions import NotFoundException, BadRequestException
from core.controllers.paginated_response import create_pageable_response
from api.audit.factory.service_interface import DataServiceInterface
from api.audit.api_schemas.access_audit_schema import BaseAccessAuditView
from core.utils import SingletonDepends



class RdsService(DataServiceInterface):
    def __init__(self, access_audit_repository):
        self.access_audit_repository = access_audit_repository

    async def create_access_audit(self, access_audit_params: BaseAccessAuditView):
        return await self.access_audit_repository.create_access_audit(access_audit_params)

    async def get_access_audits(self, include_filters, exclude_filters, page, size, sort, min_time, max_time):
        if include_filters.user_id:
            include_filters.user_id = include_filters.user_id.strip("*")
        if include_filters.app_name:
            include_filters.app_name = include_filters.app_name.strip("*")
        if exclude_filters.user_id:
            exclude_filters.user_id = exclude_filters.user_id.strip("*")
        if exclude_filters.app_name:
            exclude_filters.app_name = exclude_filters.app_name.strip("*")
        access_audits, total_count = await self.access_audit_repository.get_access_audits_with_filters(include_filters, exclude_filters, page, size, sort, min_time, max_time)
        if access_audits is None:
            raise NotFoundException("No access audits found")
        access_audit_list = [BaseAccessAuditView.model_validate(access_audit) for access_audit in access_audits]
        return create_pageable_response(access_audit_list, total_count, page, size, sort)

    async def get_usage_counts(self, filters, min_value, max_value):
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_access_audits_counts_group_by_result(filters, min_value, max_value)
        result_dict = dict()
        for r in results:
            result_dict[r.result] = {"count": r.count}
        return {"result": result_dict}

    async def get_trait_counts_by_application(self, filters, min_value, max_value):
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_access_audits_counts_group_by_traits_and_application(filters.model_dump(), min_value, max_value)
        result_dict = dict()
        for r in results:
            if r.trait in result_dict:
                result_dict[r.trait]["count"] += r.count
                result_dict[r.trait]["applicationName"][r.app_name] = {"count": r.count}
            else:
                result_dict[r.trait] = {"count": r.count, "applicationName": {r.app_name: {"count": r.count}}}
        return {"traits": result_dict}

    async def get_access_data_counts(self, filters, min_value, max_value, interval):
        if max_value <= min_value:
            raise BadRequestException("Invalid date range")
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_access_audits_counts_group_by_result_interval(filters.model_dump(), min_value, max_value, interval)
        result_dict = dict()
        for r in results:
            epoch_ms = r[0]
            if epoch_ms not in result_dict:
                if r[1] and r[2]:
                    result_dict[epoch_ms] = {"result": {r[1]: {"count": r[2]}}}
                else:
                    result_dict[epoch_ms] = {"result": {}}
            else:
                if r[1] and r[2]:
                    result_dict[epoch_ms]["result"][r[1]] = {"count": r[2]}

        return {interval: result_dict}

    async def get_user_id_counts(self, size):
        results = await self.access_audit_repository.get_access_audits_counts_group_by_user_id(size)
        result_dict = dict()
        for result in results:
            result_dict[result.user_id] = {"count": result.count}
        return {"userId": result_dict}

    async def get_app_name_counts(self, size):
        results = await self.access_audit_repository.get_access_audits_counts_group_by_app_name(size)
        result_dict = dict()
        for result in results:
            result_dict[result.app_name] = {"count": result.count}
        return {"applicationName": result_dict}

    async def get_app_name_by_user_id(self, filters, min_value, max_value):
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_access_audits_counts_group_by_app_name_and_user_id(filters, min_value, max_value)
        result_dict = dict()
        for result in results:
            result_dict[result.app_name] = {"count": result.app_name_count, "userId": {"count": result.user_id_count}}
        return {"applicationName": result_dict}

    async def get_top_users_count(self, filters, size, min_time, max_time):
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_access_audits_top_users_count_group_by_id(filters, size, min_time, max_time)
        result_dict = dict()
        for result in results:
            result_dict[result.user_id] = {"count": result.count}
        return {"userId": result_dict}

    async def get_unique_user_id_count(self, filters, min_time, max_time):
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_audits_counts_unique_user_id_count(filters, min_time, max_time)
        return {"userId": {"count": results}}

    async def get_unique_trait_count(self, filters, min_time, max_time):
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_audits_counts_unique_trait_count(filters, min_time, max_time)
        result_dict = dict()
        for result in results:
            result_dict[result.trait] = {"count": result.count}
        return {"traits": result_dict}

    async def get_activity_trend_counts(self, filters, min_value, max_value, interval):
        if max_value <= min_value:
            raise BadRequestException("Invalid date range")
        if filters.user_id or filters.app_name:
            filters.exact_match = True
        results = await self.access_audit_repository.get_activity_trend_counts(filters.model_dump(), min_value, max_value, interval)
        result_dict = dict()
        for r in results:
            epoch_ms = r[0]
            if epoch_ms not in result_dict:
                if r[1]:
                    result_dict[epoch_ms] = {"tenantId": {'1': {"count": r[1]}}}
                else:
                    result_dict[epoch_ms] = {"tenantId": {}}
            else:
                if r[1]:
                    result_dict[epoch_ms]["tenantId"]['1'] = {"count": r[1]}
        return {interval: result_dict}


def get_rds_service(access_audit_repository: AccessAuditRepository = SingletonDepends(AccessAuditRepository)):
    return RdsService(access_audit_repository=access_audit_repository)
