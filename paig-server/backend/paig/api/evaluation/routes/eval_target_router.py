import json
from typing import List, Optional
from fastapi import APIRouter, Request, Response, Depends, Query, HTTPException

from core.controllers.paginated_response import Pageable
from api.evaluation.api_schemas.eval_schema import EvaluationCommonModel, EvaluationConfigPlugins, IncludeQueryParams,\
include_query_params, exclude_query_params, QueryParamsBase
from core.utils import SingletonDepends
from core.security.authentication import get_auth_user
from api.evaluation.controllers.eval_target_controller import EvaluationTargetController
from api.governance.api_schemas.ai_app import AIApplicationFilter
from api.evaluation.api_schemas.eval_target_schema import TargetCreateRequest, TargetUpdateRequest

evaluation_target_router = APIRouter()

eval_target_controller_instance = Depends(SingletonDepends(EvaluationTargetController, called_inside_fastapi_depends=True))


@evaluation_target_router.get("/application")
async def get_ai_app_with_host(
        application_filter: AIApplicationFilter = Depends(),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        user: dict = Depends(get_auth_user),
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.get_all_ai_app_with_host(application_filter, page, size, sort)


@evaluation_target_router.post("/application/{id}")
async def save_application_target(
        request: Request,
        response: Response,
        id: int,
        body_params: TargetCreateRequest,
        user: dict = Depends(get_auth_user),
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.create_app_target(app_id=id, body_params=body_params.model_dump())


@evaluation_target_router.put("/application/{id}")
async def update_application_target(
        request: Request,
        response: Response,
        id: int,
        body_params: TargetUpdateRequest,
        user: dict = Depends(get_auth_user),
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.update_app_target(app_id=id, body_params=body_params.model_dump())


@evaluation_target_router.delete("/application/{id}")
async def delete_application_target(
        request: Request,
        response: Response,
        id: int,
        user: dict = Depends(get_auth_user),
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.delete_app_target(app_id=id)