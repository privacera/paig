from sqlalchemy import and_
from api.evaluation.api_schemas.eval_schema import BaseEvaluationView
from api.evaluation.database.db_models import EvaluationTargetModel
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from core.utils import current_utc_time, get_field_name_by_alias, epoch_to_utc
from core.db_session import session


class EvaluationTargetRepository(BaseOperations[EvaluationTargetModel]):

    def __init__(self):
        """
        Initialize the EvaluationRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationTargetModel)

    async def get_target_by_app_id(self, app_id: int):
        try:
            filters = {'application_id': app_id}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_app_target(self, app_id, eval_target):
        target_data = {'application_id': app_id, 'config': eval_target}
        target = EvaluationTargetModel(**target_data)
        session.add(target)
        await session.flush()
        return target


    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_target(self, target_model):
        return await self.delete(target_model)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_app_target(self, params, target_model):
        target_data = {'config': params, 'update_time': current_utc_time()}
        target_model.set_attribute(target_data)
        return target_model

    async def get_target_hosts_by_in_list(self, field: str, values: list):
        try:
            apply_in_list_filter = True
            filters = {field: values}
            return await self.get_all(filters, apply_in_list_filter=apply_in_list_filter, columns=[EvaluationTargetModel.config, EvaluationTargetModel.application_id])
        except NoResultFound:
            return None