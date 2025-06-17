from typing import List
from fastapi import APIRouter, Request, Response, Depends, Query
from core.utils import SingletonDepends
from ..controllers.eval_target_controller import EvaluationTargetController
from ..api_schemas.eval_target_schema import IncludeQueryParams, QueryParamsBase, include_query_params, exclude_query_params
from ..api_schemas.eval_target_schema import TargetCreateRequest, TargetUpdateRequest, TargetApplicationConnectionRequest

evaluation_target_router = APIRouter()

eval_target_controller_instance = Depends(SingletonDepends(EvaluationTargetController, called_inside_fastapi_depends=True))


@evaluation_target_router.get("/application/list")
async def get_ai_app_with_host(
        include_query: IncludeQueryParams = Depends(include_query_params),
        exclude_query: QueryParamsBase = Depends(exclude_query_params),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.get_all_ai_app_with_host(include_query, exclude_query, page, size, sort)


@evaluation_target_router.post("/application")
async def save_target_application(
        request: Request,
        response: Response,
        body_params: TargetCreateRequest,
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.create_app_target(body_params=body_params.model_dump())


@evaluation_target_router.put("/application/{id}")
async def update_target_application(
        request: Request,
        response: Response,
        id: int,
        body_params: TargetUpdateRequest,
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.update_app_target(app_id=id, body_params=body_params.model_dump())


@evaluation_target_router.delete("/application/{id}")
async def delete_application_target(
        request: Request,
        response: Response,
        id: int,
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.delete_app_target(app_id=id)


@evaluation_target_router.get("/application/{id}")
async def get_application_target_by_id(
        request: Request,
        response: Response,
        id: int,
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.get_app_target_by_id(app_id=id)


@evaluation_target_router.post("/application/connection")
async def check_target_application_connection(
        request: Request,
        response: Response,
        body_params: TargetApplicationConnectionRequest,
        eval_target_controller: EvaluationTargetController = eval_target_controller_instance
):
    return await eval_target_controller.check_target_application_connection(body_params=body_params.model_dump())