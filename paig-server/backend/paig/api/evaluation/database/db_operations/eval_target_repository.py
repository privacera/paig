from sqlalchemy import and_, func, or_, union_all
from api.evaluation.database.db_models import EvaluationTargetModel
from api.governance.database.db_models.ai_app_model import AIApplicationModel
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.future import select
from core.utils import current_utc_time
from core.db_session import session


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
        all_filters = []
        skip = 0 if page is None else (page * size)
        # Define common columns
        columns = [
            AIApplicationModel.id.label("ai_application_model_id"),
            EvaluationTargetModel.id.label("eval_target_model_id"),
            AIApplicationModel.name.label("application_name"),
            AIApplicationModel.description.label("ai_application_desc"),
            EvaluationTargetModel.url.label("eval_target_model_url"),
            EvaluationTargetModel.name.label("eval_target_name"),
        ]

        # Query 1: Get all AIApplicationModel entries (Left Join)
        query1 = select(*columns).outerjoin(
            EvaluationTargetModel, AIApplicationModel.id == EvaluationTargetModel.application_id
        )

        # Query 2: Get all EvaluationTargetModel entries (Right Join Simulation)
        query2 = select(*columns).outerjoin(
            AIApplicationModel, AIApplicationModel.id == EvaluationTargetModel.application_id
        )
        combined_query = union_all(query1, query2).subquery()
        query = (
            select(
                combined_query.c.ai_application_model_id,
                combined_query.c.eval_target_model_id,
                combined_query.c.application_name,
                combined_query.c.ai_application_desc,
                combined_query.c.eval_target_model_url,
                combined_query.c.eval_target_name,
            )
            .distinct(combined_query.c.eval_target_model_id)
            # Remove duplicates
        )

        # query = select(combined_query)
        # Handle include_filters on application_name
        if include_filters and "name" in include_filters.model_dump():
            filter_value = include_filters.model_dump()["name"]
            if filter_value:
                query = query.filter(
                    or_(
                        combined_query.c.application_name.like(f"%{filter_value}%"),
                        combined_query.c.eval_target_name.like(f"%{filter_value}%")
                    )
                )

        # Handle exclude_filters on application_name
        if exclude_filters and "name" in exclude_filters.model_dump():
            filter_value = exclude_filters.model_dump()["name"]
            if filter_value:
                query = query.filter(
                    and_(
                        combined_query.c.application_name.is_(None) | combined_query.c.application_name.notlike(
                            f"%{filter_value}%"),
                        combined_query.c.eval_target_name.is_(None) | combined_query.c.eval_target_name.notlike(
                            f"%{filter_value}%"),
                    )
                )

        if all_filters:
            query = query.filter(and_(*all_filters))
        total_count_query = select(func.count()).select_from(query.subquery())
        total_count = (await session.execute(total_count_query)).scalar()

        query = query.limit(size).offset(skip)
        results = await session.execute(query)
        return results.all(), total_count


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

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_app_target(self, eval_target):
        target = EvaluationTargetModel(**eval_target)
        session.add(target)
        await session.flush()
        return target


    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_target(self, target_model):
        return await self.delete(target_model)

    @Transactional(propagation=Propagation.REQUIRED)
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
        query = select(
            select(EvaluationTargetModel.id).filter(EvaluationTargetModel.name == name).exists()
        ).scalar_subquery() | select(
            select(AIApplicationModel.id).filter(AIApplicationModel.name == name).exists()
        ).scalar_subquery()

        return (await session.execute(select(query))).scalar()