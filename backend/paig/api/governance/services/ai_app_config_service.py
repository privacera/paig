from datetime import datetime
from sqlalchemy.exc import NoResultFound

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.utils import validate_id, SingletonDepends
from api.governance.api_schemas.ai_app_config import AIApplicationConfigView, AIApplicationConfigFilter
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from api.governance.database.db_operations.ai_app_config_repository import AIAppConfigRepository
from api.governance.database.db_operations.ai_app_repository import AIAppRepository


class AIAppConfigRequestValidator:

    def __init__(self, ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository)):
        self.ai_app_repository = ai_app_repository

    async def validate_read_request(self, id: int):
        """
        Validate a read request for an AI application.

        Args:
            id (int): The ID of the AI application to retrieve.
        """
        validate_id(id, "AI application ID")
        await self.validate_application_exists_by_id(id)

    async def validate_update_request(self, id: int, request: AIApplicationConfigView):
        """
        Validate an update request for an AI application.

        Args:
            id (int): The ID of the AI application to update.
            request (AIApplicationView): The updated view object representing the AI application.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "AI application ID")
        await self.validate_application_exists_by_id(id)

    async def validate_application_exists_by_id(self, id: int):
        """
        Validate if an AI application exists by ID.

        Args:
            id (int): The ID of the AI application.
        """
        try:
            await self.ai_app_repository.get_record_by_id(id)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "AI Application", "ID", [id]))


class AIAppConfigService(BaseController[AIApplicationConfigModel, AIApplicationConfigView]):
    """
    Service class specifically for handling AI application policies.

    Args:
        ai_app_policy_repository (AIAppPolicyRepository): The repository handling AI application policy database operations.
    """

    def __init__(self, ai_app_config_repository: AIAppConfigRepository = SingletonDepends(AIAppConfigRepository), app_config_request_validator: AIAppConfigRequestValidator = SingletonDepends(AIAppConfigRequestValidator)):
        super().__init__(ai_app_config_repository, AIApplicationConfigModel, AIApplicationConfigView)
        self.app_config_request_validator = app_config_request_validator

    def get_repository(self) -> AIAppConfigRepository:
        """
        Get the AI application repository.

        Returns:
            AIAppConfigRepository: The AI application repository.
        """
        return self.repository

    async def get_ai_app_config(self, application_id: int):
        """
        Get the configuration of an AI application.

        Args:
            application_id (int): The ID of the AI application.

        Returns:
            AIApplicationConfigView: The configuration of the AI application.
        """
        await self.app_config_request_validator.validate_read_request(application_id)

        repository = self.get_repository()
        ai_app_config_model = await repository.get_ai_app_config_by_ai_application_id(application_id)
        if ai_app_config_model is None:
            ai_app_config_model = AIApplicationConfigModel(
                id=0,
                status=1,
                create_time=datetime.now(),
                update_time=datetime.now(),
                allowed_users=[],
                allowed_groups=[],
                allowed_roles=[],
                denied_users=[],
                denied_groups=[],
                denied_roles=[],
                application_id=application_id
            )
        return ai_app_config_model

    async def list_ai_app_configs(self, ai_app_config_filter: AIApplicationConfigFilter, page_number: int, size: int, sort: list) -> Pageable:
        """
        List AI application configurations.

        Args:
            ai_app_config_filter (dict): The filter to apply to the query.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (list): The sort order to apply to the query.

        Returns:
            PageableResponse: The pageable response containing the list of AI application configurations.
        """
        return await self.list_records(ai_app_config_filter, page_number, size, sort)

    async def update_ai_app_config(self, application_id: int, request: AIApplicationConfigView):
        """
        Update the configuration of an AI application.

        Args:
            application_id (int): The ID of the AI application.
            request (AIApplicationConfigView): The updated configuration of the AI application.

        Returns:
            AIApplicationConfigView: The updated configuration of the AI application.
        """
        await self.app_config_request_validator.validate_update_request(application_id, request)

        repository = self.get_repository()
        model = await repository.get_ai_app_config_by_ai_application_id(application_id)
        if model is not None:
            updated_data = request.model_dump(exclude_unset=True, exclude={"id", "create_time", "update_time", "application_id"})
            model.set_attribute(updated_data)
            model.update_time = datetime.now()
            return await self.repository.update_record(model)
        else:
            request_data = request.model_dump(exclude_unset=True,
                                              exclude={"id", "create_time", "update_time", "application_id"})
            updated_request = AIApplicationConfigView(**request_data)
            updated_request.application_id = application_id
            record = await self.create_record(updated_request)
            return record
