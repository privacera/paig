from fastapi import APIRouter, Request, Response, Depends, Query
from api.audit.api_schemas.access_audit_schema import IncludeQueryParams, include_query_params, exclude_query_params, QueryParamsBase
from core.security.authentication import get_auth_user
from typing import List, Optional
from api.audit.controllers.data_store_controller import DataStoreController
from core.utils import SingletonDepends

data_service_router = APIRouter()

data_store_controller_instance = Depends(SingletonDepends(DataStoreController, called_inside_fastapi_depends=True))

@data_service_router.get("/api/shield_audits/search")
async def get_access_audits(
        request: Request,
        response: Response,
        user: dict = Depends(get_auth_user),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        excludeQuery: QueryParamsBase = Depends(exclude_query_params),
        data_store_controller: DataStoreController = data_store_controller_instance
):
    return await data_store_controller.get_service().get_access_audits(includeQuery, excludeQuery, page, size, sort,
                                                                       fromTime, toTime)


@data_service_router.get("/api/shield_audits/usage_counts")
async def get_usage_counts(
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_usage_counts(includeQuery, fromTime, toTime)


@data_service_router.get("/api/shield_audits/trait_counts")
async def get_trait_counts_by_application(
        request: Request,
        response: Response,
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_trait_counts_by_application(includeQuery, fromTime, toTime)


@data_service_router.get("/api/shield_audits/access_data_counts")
async def get_access_data_counts(
        request: Request,
        response: Response,
        fromTime: int = Query(0, description="The from time"),
        toTime: int = Query(0, description="The to time"),
        interval: Optional[str] = Query('month', description="The interval"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_access_data_counts(includeQuery, fromTime, toTime, interval)


@data_service_router.get("/api/shield_audits/user_id_counts")
async def get_user_id_counts(
        request: Request,
        response: Response,
        size: int = Query(100, description="The number of items per page"),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance
):
    return await data_store_controller.get_service().get_user_id_counts(size)


@data_service_router.get("/api/shield_audits/app_name_counts")
async def get_app_name_counts(
        request: Request,
        response: Response,
        size: int = Query(100, description="The number of items per page"),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_app_name_counts(size)


@data_service_router.get("/api/shield_audits/app_by_user_counts")
async def get_app_name_by_user_id(
        request: Request,
        response: Response,
        user: dict = Depends(get_auth_user),
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        data_store_controller: DataStoreController = data_store_controller_instance
):
    return await data_store_controller.get_service().get_app_name_by_user_id(includeQuery, fromTime, toTime)


@data_service_router.get("/api/shield_audits/top_users_count")
async def get_top_users_by_id(
        request: Request,
        response: Response,
        size: int = Query(10, description="The number of items per page"),
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_top_users_count(includeQuery, size, fromTime, toTime)


@data_service_router.get("/api/shield_audits/uniq_user_id_counts")
async def get_user_id_count(
        request: Request,
        response: Response,
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_unique_user_id_count(includeQuery, fromTime, toTime)


@data_service_router.get("/api/shield_audits/uniq_trait_counts")
async def get_trait_count(
        request: Request,
        response: Response,
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_unique_trait_count(includeQuery, fromTime, toTime)


@data_service_router.get("/api/shield_audits/activity_trend_counts")
async def get_activity_trend_counts(
        request: Request,
        response: Response,
        fromTime: int = Query(0, description="The from time"),
        toTime: int = Query(0, description="The to time"),
        interval: Optional[str] = Query('month', description="The interval"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_activity_trend_counts(includeQuery, fromTime, toTime, interval)


@data_service_router.get("/api/admin_audits/search")
async def get_admin_audits(
        request: Request,
        response: Response,
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        fromTime: int = Query(0, description="The from time"),
        toTime: int = Query(0, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_admin_audits(includeQuery, page, size, sort, fromTime, toTime)

@data_service_router.get("/api/admin_audits/count")
async def get_admin_audits_count(
        request: Request,
        response: Response,
        size: int = Query(10, description="The number of items per page"),
        fromTime: int = Query(0, description="The from time"),
        toTime: int = Query(0, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        groupBy: str = Query(None, description="The group by"),
        cardinality: bool = Query(False, description="The cardinality"),
        interval: Optional[str] = Query(None, description="The interval"),
        user: dict = Depends(get_auth_user),
        data_store_controller: DataStoreController = data_store_controller_instance,
):
    return await data_store_controller.get_service().get_admin_audits_count(includeQuery, size, fromTime, toTime, groupBy, cardinality, interval)
