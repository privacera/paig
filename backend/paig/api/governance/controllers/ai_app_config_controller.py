
from api.user.utils.acc_service_validation_util import AccServiceValidationUtil
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.ai_app_config import AIApplicationConfigView
from api.governance.services.ai_app_config_service import AIAppConfigService
from api.governance.services.ai_app_service import AIAppService
from core.utils import SingletonDepends


class AIAppConfigController:
    """
    Controller class for handling AI application configuration operations.

    Args:
        ai_app_config_service (AIAppConfigService): The service class for handling AI application configuration operations.
        acc_service_validation_util (AccServiceValidationUtil): The validation utility class for account
    """

    def __init__(self,
                 ai_app_config_service: AIAppConfigService = SingletonDepends(AIAppConfigService),
                 ai_app_service: AIAppService = SingletonDepends(AIAppService),
                 acc_service_validation_util: AccServiceValidationUtil = SingletonDepends(AccServiceValidationUtil)):
        self.ai_app_config_service = ai_app_config_service
        self.ai_app_service = ai_app_service
        self.acc_service_validation_util = acc_service_validation_util

    async def get_ai_app_config(self, application_id: int):
        """
        Get the configuration of an AI application.

        Args:
            application_id (int): The ID of the AI application.

        Returns:
            AIApplicationConfigView: The configuration of the AI application.
        """
        return await self.ai_app_config_service.get_ai_app_config(application_id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_ai_app_config(self, application_id: int, request: AIApplicationConfigView):
        """
        Update the configuration of an AI application.

        Args:
            application_id (int): The ID of the AI application.
            request (AIApplicationConfigView): The updated configuration of the AI application.

        Returns:
            AIApplicationConfigView: The updated configuration of the AI application.
        """
        users = request.allowed_users.copy()
        users.extend(request.denied_users.copy())
        await self.acc_service_validation_util.validate_users_exists(users)

        groups = request.allowed_groups.copy()
        groups.extend(request.denied_groups.copy())
        await self.acc_service_validation_util.validate_groups_exists(groups)

        return await self.ai_app_config_service.update_ai_app_config(application_id, request)
