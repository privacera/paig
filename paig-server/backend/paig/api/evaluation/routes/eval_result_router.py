from typing import List, Optional
from fastapi import APIRouter, Request, Response, Depends, Query
from api.evaluation.api_schemas.eval_schema import IncludeQueryParams, \
    include_query_params, exclude_query_params, QueryParamsBase,  \
    ResultsIncludeQueryParams, ResultsQueryParamsBase, results_include_query_params, results_exclude_query_params
from core.utils import SingletonDepends
from core.security.authentication import get_auth_user
from api.evaluation.controllers.eval_controllers import EvaluationController
evaluation_result_router = APIRouter()

evaluator_controller_instance = Depends(SingletonDepends(EvaluationController, called_inside_fastapi_depends=True))


@evaluation_result_router.get("/list")
async def get_evaluation_results(
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
        evaluation_controller: EvaluationController = evaluator_controller_instance,
):
    return await evaluation_controller.get_evaluation_results(includeQuery, excludeQuery, page, size, sort,
                                                                       fromTime, toTime)


@evaluation_result_router.delete("/{eval_id}")
async def evaluation_delete(
    eval_id: int,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
    return await evaluation_controller.delete_evaluation(eval_id)


@evaluation_result_router.get("/{eval_id}")
async def evaluation_get(
    eval_id: str,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
    return await evaluation_controller.get_evaluation(eval_id)


@evaluation_result_router.get("/{eval_uuid}/cumulative")
async def get_cumulative_result(
    eval_uuid: str,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
   return await evaluation_controller.get_cumulative_results(eval_uuid)


@evaluation_result_router.get("/{eval_uuid}/detailed")
async def get_detailed_result(
    eval_uuid: str,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
    page: int = Query(0, description="The page number to retrieve"),
    size: int = Query(10, description="The number of items per page"),
    sort: List[str] = Query([], description="The sort options"),
    from_time: Optional[int] = Query(None, description="The from time"),
    to_time: Optional[int] = Query(None, description="The to time"),
    include_query: ResultsIncludeQueryParams = Depends(results_include_query_params),
    exclude_query: ResultsQueryParamsBase = Depends(results_exclude_query_params),
):
   return await evaluation_controller.get_detailed_results(
       eval_uuid,
       include_query,
       exclude_query,
       page,
       size,
       sort,
       from_time,
       to_time
   )

@evaluation_result_router.get("/{eval_uuid}/severity")
async def get_result_by_severity(
    eval_uuid: str,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
   return await evaluation_controller.get_result_by_severity(eval_uuid)


@evaluation_result_router.get("/{eval_uuid}/category-stats")
async def get_result_by_category(
    eval_uuid: str,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
   return await evaluation_controller.get_result_by_category(eval_uuid)

@evaluation_result_router.get("/{eval_uuid}/category")
async def get_all_categories_from_result(
    eval_uuid: str,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
   return await evaluation_controller.get_all_categories_from_result(eval_uuid)