from sqlalchemy import and_
from api.evaluation.api_schemas.eval_config_schema import EvalConfigView
from api.evaluation.database.db_models import EvaluationConfigModel, EvaluationConfigHistoryModel, EvaluationModel
from core.factory.database_initiator import BaseOperations
from core.db_session.transactional import Transactional, Propagation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from core.utils import current_utc_time, get_field_name_by_alias, epoch_to_utc
from sqlalchemy import func, outerjoin
from sqlalchemy.orm import aliased
from core.db_session import session
from core.controllers.paginated_response import Pageable, create_pageable_response
import logging

logger = logging.getLogger(__name__)

EvalRun = aliased(EvaluationModel)

class EvaluationConfigRepository(BaseOperations[EvaluationConfigModel]):

    def __init__(self):
        """
        Initialize the EvaluationRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationConfigModel)
        self.view_type = EvalConfigView

    async def get_all_eval_config(self, search_filters, page_number, size, sort) -> Pageable:
        """
        Get all evaluation configurations.

        Args:
            search_filters (BaseEvaluationView): The search filters.
            page_number (int): The page number.
            size (int): The number of items per page.
            sort (List[str]): The sort options.

        Returns:
            List[EvalConfigView]: The list of evaluation configurations.
        """
        records, total_count =  await self.list_records(search_filters, page_number, size, sort, relation_load_options=[selectinload(self.model_class.eval_runs)])
        v_records = [
            self.view_type.model_validate({
                **record.__dict__,
                "eval_run_count": len(record.eval_runs) if isinstance(record.eval_runs, list) else 0
            })
            for record in records
        ]
        return create_pageable_response(v_records, total_count, page_number, size, sort)

    async def create_eval_config(self, body_params: dict):
        """
        Create a new evaluation configuration.

        Args:
            body_params (dict): The evaluation configuration parameters.

        Returns:
            dict: The response message.
        """
        param = EvaluationConfigModel(**body_params)
        session.add(param)
        await session.flush()
        return param

    async def get_eval_config_by_id(self, config_id: int):
        """
        Get an evaluation configuration by ID.

        Args:
            config_id (int): The ID of the evaluation configuration.

        Returns:
            EvaluationConfigModel: The evaluation configuration.
        """
        try:
            return await self.get_record_by_id(config_id)
        except NoResultFound:
            return None
        except Exception as e:
            raise e

    async def update_eval_config(self, params, eval_config_model):
        eval_config_model.set_attribute(params)
        return eval_config_model

    async def delete_eval_config(self, eval_config_model):
        return await self.delete(eval_config_model)


class EvaluationConfigHistoryRepository(BaseOperations[EvaluationConfigHistoryModel]):

    def __init__(self):
        """
        Initialize the EvaluationRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EvaluationConfigHistoryModel)
        self.view_type = EvalConfigView

    async def get_all_eval_config_history(self, search_filters, page_number, size, sort):
        """
        Get all evaluation configuration history.

        Args:
            search_filters (BaseEvaluationView): The search filters.
            page_number (int): The page number.
            size (int): The number of items per page.
            sort (List[str]): The sort options.

        Returns:
            List[EvalConfigView]: The list of evaluation configurations.
        """
        try:
            return await self.list_records(search_filters, page_number, size, sort)
        except Exception as e:
            raise e

    async def create_eval_config_history(self, body_params: dict):
        """
        Create a new evaluation configuration history.

        Args:
            body_params (dict): The evaluation configuration history parameters.

        Returns:
            dict: The response message.
        """
        param = EvaluationConfigHistoryModel(**body_params)
        session.add(param)
        await session.flush()
        return param

    async def  get_eval_config_by_config_id(self, eval_config_id: int):
        try:
            filters = {'eval_config_id': eval_config_id}
            return await self.get_by(filters, unique=True)
        except NoResultFound:
            return None