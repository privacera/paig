from sqlalchemy import and_, func, case

from api.evaluation.api_schemas.eval_schema import BaseEvaluationView
from api.evaluation.database.db_models import EvaluationModel
from api.evaluation.database.db_models.eval_model import EvaluationResultPromptsModel, EvaluationResultResponseModel
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from core.utils import current_utc_time, get_field_name_by_alias, epoch_to_utc
from core.db_session import session


def create_like_filter(model_attr, key, include_query, exclude_list):
    """Helper function to create like/notlike filters."""
    if key in include_query and include_query[key]:
        value = f"%{include_query[key]}%"
        return model_attr.notlike(value) if key in exclude_list else model_attr.like(value)
    return None

class EvaluationRepository(BaseOperations[EvaluationModel]):

    def __init__(self):
        """
        Initialize the EvaluationRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationModel)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_new_evaluation(self, evaluation_params):
        evaluation_params['create_time'] = current_utc_time()
        model = self.model_class()
        model.set_attribute(evaluation_params)
        session.add(model)
        await session.flush()
        return model

    async def get_all_evaluation(self, **args):
        return await self.get_all(**args)


    async def get_evaluations_by_field(self, field: str, value):
        try:
            filters = {field: value}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    async def update_evaluation(self, evaluation_params, evaluation_model):
        evaluation_params['update_time'] = current_utc_time()
        evaluation_model.set_attribute(evaluation_params)
        return evaluation_model

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_evaluation(self, evaluation_id):
        return await self.delete(evaluation_id)

    async def get_eval_results_with_filters(self, include_filters, exclude_filters, page, size, sort, min_value, max_value):
        all_filters = list()
        skip = 0 if page is None else (page * size)
        query = select(EvaluationModel)
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
            all_filters.append(EvaluationModel.create_time >= min_value)
        if max_value:
            max_value = epoch_to_utc(max_value)
            all_filters.append(EvaluationModel.create_time <= max_value)
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
                    field_names.append(get_field_name_by_alias(model=BaseEvaluationView, alias=alias_name))
                sort_column_name = ",".join(field_names)
                query = self.order_by(query, sort_column_name, sort_type)
        query = query.limit(size).offset(skip)
        results = (await session.execute(query)).scalars().all()
        filters = include_filters.model_dump()
        if'create_time_to' in filters and max_value:
            filters['create_time_to'] = max_value
        if 'create_time_from' in filters and min_value:
            filters['create_time_from'] = min_value
        count = (await self.get_count_with_filter(filters))

        return results, count



class EvaluationPromptRepository(BaseOperations[EvaluationResultPromptsModel]):
    def __init__(self):
        """
        Initialize the EvaluationPromptsRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationResultPromptsModel)


    async def get_detailed_results_by_uuid(self,
         eval_uuid,
         include_query,
         exclude_query,
         page,
         size,
         sort,
         from_time,
         to_time
    ):
        skip = 0 if page is None else (page * size)
        # base query
        query = select(EvaluationResultPromptsModel).filter(EvaluationResultPromptsModel.eval_id == eval_uuid.strip())
        exclude_list = []
        if exclude_query:
            for key, value in exclude_query.model_dump().items():
                if value:
                    exclude_list.append(key)
                    if hasattr(include_query, key):
                        setattr(include_query, key, value)
        include_query = include_query.model_dump()
        search_filters = []
        if from_time:
            search_filters.append(EvaluationResultPromptsModel.create_time >= epoch_to_utc(from_time))
        if to_time:
            search_filters.append(EvaluationResultPromptsModel.create_time <= epoch_to_utc(to_time))
        prompt_filter = create_like_filter(EvaluationResultPromptsModel.prompt, 'prompt', include_query, exclude_list)
        if prompt_filter is not None:
            search_filters.append(prompt_filter)

        response_filters = {
            'response': EvaluationResultResponseModel.response,
            'category': EvaluationResultResponseModel.category,
            'status': EvaluationResultResponseModel.status,
            'category_type': EvaluationResultResponseModel.category_type,
            "category_severity": EvaluationResultResponseModel.category_severity
        }

        for key, model_attr in response_filters.items():
            response_filter = create_like_filter(model_attr, key, include_query, exclude_list)
            if response_filter is not None:
                search_filters.append(EvaluationResultPromptsModel.responses.any(response_filter))

        if len(search_filters) > 0:
            query = query.filter(*search_filters)

        # Get total count
        total_count_query = select(func.count()).select_from(query.subquery())
        total_count = (await session.execute(total_count_query)).scalar()

        # Fetch results
        query = query.options(selectinload(EvaluationResultPromptsModel.responses)).offset(skip).limit(size)
        results = (await session.execute(query)).scalars().all()
        return results, total_count



class EvaluationResponseRepository(BaseOperations[EvaluationResultResponseModel]):
    def __init__(self):
        """
        Initialize the EvaluationPromptsRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationResultResponseModel)


    async def get_result_by_severity(self, eval_id):
        query = (
            select(
                EvaluationResultResponseModel.category_severity,
                EvaluationResultResponseModel.application_name,
                func.count().label("count")
            )
            .where(
                EvaluationResultResponseModel.eval_id == eval_id,
                EvaluationResultResponseModel.category_type.isnot(None)  # Exclude NULL category_type
            )
            .group_by(EvaluationResultResponseModel.category_severity, EvaluationResultResponseModel.application_name)
        )

        result = await session.execute(query)
        rows = result.fetchall()
        return rows

    async def get_result_by_category(self, eval_id):
        severity_order = case(
            (EvaluationResultResponseModel.category_severity == "CRITICAL", 4),
            (EvaluationResultResponseModel.category_severity == "HIGH", 3),
            (EvaluationResultResponseModel.category_severity == "MEDIUM", 2),
            (EvaluationResultResponseModel.category_severity == "LOW", 1),
            else_=0
        )
        query = (
            select(
                EvaluationResultResponseModel.category_type,
                EvaluationResultResponseModel.category,
                EvaluationResultResponseModel.application_name,
                func.count().label("total"),
                func.sum(case((EvaluationResultResponseModel.status == "PASSED", 1), else_=0)).label("pass_count"),
                func.sum(case((EvaluationResultResponseModel.status == "FAILED", 1), else_=0)).label("fail_count"),
                func.sum(case((EvaluationResultResponseModel.status == "ERROR", 1), else_=0)).label("error_count"),
                func.max(severity_order).label("max_severity")
            )
            .where(EvaluationResultResponseModel.eval_id == eval_id)
            .group_by(EvaluationResultResponseModel.category_type, EvaluationResultResponseModel.category, EvaluationResultResponseModel.application_name)
        )

        result = await session.execute(query)
        rows = result.fetchall()

        final_stats = dict()
        severity_map = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}

        for category_type, category, application_name, total, pass_count, fail_count, error_count, max_severity in rows:
            if category_type not in final_stats:
                final_stats[category_type] = dict()
            if application_name not in final_stats[category_type]:
                final_stats[category_type][application_name] = {
                    "categories": {},
                    "total": 0,
                    "passes": 0,
                    "severity": None
                }

            final_stats[category_type][application_name]["categories"][category] = {
                "pass": pass_count,
                "fail": fail_count,
                "error": error_count,
                "total": pass_count + fail_count + error_count
            }
            final_stats[category_type][application_name]["total"] += total
            final_stats[category_type][application_name]["passes"] += pass_count

            # If max_severity is 0, ignore it (equivalent to NULL/NONE)
            if max_severity > 0:
                new_severity = severity_map[max_severity]
                if final_stats[category_type][application_name]["severity"] is None or \
                        list(severity_map.values()).index(new_severity) > list(severity_map.values()).index(
                    final_stats[category_type][application_name]["severity"]):
                    final_stats[category_type][application_name]["severity"] = new_severity

        return final_stats

    async def get_all_categories_from_result(self, eval_id):
        query = (
            select(
                EvaluationResultResponseModel.category_type,
                EvaluationResultResponseModel.category
            )
            .where(EvaluationResultResponseModel.eval_id == eval_id)
            .distinct()
        )

        result = await session.execute(query)
        rows = result.fetchall()
        result = dict()
        result['category'] = list()
        result['category_type'] = list()

        for category_type, category in rows:
            if category:
                result['category'].append(category)
            if category_type:
                result['category_type'].append(category_type)

        result['category'] = list(set(result['category']))
        result['category_type'] = list(set(result['category_type']))
        return result