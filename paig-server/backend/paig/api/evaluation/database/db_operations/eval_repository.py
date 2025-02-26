from dns.e164 import query
from sqlalchemy import and_, func
from api.evaluation.api_schemas.eval_schema import BaseEvaluationView
from api.evaluation.database.db_models import EvaluationModel
from api.evaluation.database.db_models.eval_model import EvaluationResultPromptsModel, EvaluationResultResponseModel
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.future import select
from core.utils import current_utc_time, get_field_name_by_alias, epoch_to_utc
from core.db_session import session


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
        count = (await self.get_count_with_filter(include_filters.model_dump()))
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
        if 'prompt' in include_query and include_query['prompt']:
            if 'prompt' in exclude_list:
                search_filters.append(EvaluationResultPromptsModel.prompt.notlike('%' + include_query['prompt'] + '%'))
            else:
                search_filters.append(EvaluationResultPromptsModel.prompt.like('%' + include_query['prompt'] + '%'))
        if 'response' in include_query and include_query['response']:
            if 'response' in exclude_list:
                search_filters.append(EvaluationResultPromptsModel.responses.any(EvaluationResultResponseModel.response.notlike('%' + include_query['response'] + '%')))
            else:
                search_filters.append(EvaluationResultPromptsModel.responses.any(EvaluationResultResponseModel.response.like('%' + include_query['response'] + '%')))
        if 'category' in include_query and include_query['category']:
            if 'category' in exclude_list:
                search_filters.append(EvaluationResultPromptsModel.responses.any(EvaluationResultResponseModel.category.notlike('%' + include_query['category'] + '%')))
            else:
                search_filters.append(EvaluationResultPromptsModel.responses.any(EvaluationResultResponseModel.category.like('%' + include_query['category'] + '%')))
        if 'status' in include_query and include_query['status']:
            if 'status' in exclude_list:
                search_filters.append(EvaluationResultPromptsModel.responses.any(EvaluationResultResponseModel.status.notlike('%' + include_query['status'] + '%')))
            else:
                search_filters.append(EvaluationResultPromptsModel.responses.any(EvaluationResultResponseModel.status.like('%' + include_query['status'] + '%')))
        if len(search_filters) > 0:
            query = query.filter(*search_filters)

        # Get total count
        total_count_query = select(func.count()).select_from(query.subquery())
        total_count = (await session.execute(total_count_query)).scalar()

        # Fetch results
        query = query.options(selectinload(EvaluationResultPromptsModel.responses)).offset(skip).limit(size)
        results = (await session.execute(query)).scalars().all()
        return results, total_count




