from typing import List

from api.user.utils.acc_service_validation_util import AccServiceValidationUtil
from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView, AIApplicationPolicyFilter
from api.governance.services.ai_app_policy_service import AIAppPolicyService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends
from core.factory.events import CreateAIApplicationPolicyEvent, UpdateAIApplicationPolicyEvent
from core.middlewares.usage import background_capture_event


class AIAppPolicyController:
    """
        Controller class specifically for handling AI application policies.

        Args:
            ai_app_policy_service (AIAppPolicyService): The service class for AI application policies.
        """

    def __init__(self,
                 ai_app_policy_service: AIAppPolicyService = SingletonDepends(AIAppPolicyService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil),
                 acc_service_validation_util: AccServiceValidationUtil = SingletonDepends(AccServiceValidationUtil)):
        self.ai_app_policy_service = ai_app_policy_service
        self.gov_service_validation_util = gov_service_validation_util
        self.acc_service_validation_util = acc_service_validation_util

    async def list_ai_application_policies(self, app_policy_filter: AIApplicationPolicyFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of AI application policies.

        Args:
            app_policy_filter (AIApplicationPolicyFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing AI application policy view objects and metadata.
        """
        return await self.ai_app_policy_service.list_ai_application_policies(
            app_policy_filter=app_policy_filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def get_ai_application_policy_by_id(self, app_id: int, id: int) -> AIApplicationPolicyView:
        """
        Retrieve an AI application policy by its ID.

        Args:
            app_id (int): The ID of the AI application.
            id (int): The ID of the AI application policy to retrieve.

        Returns:
            AIApplicationPolicyView: The AI application policy view object corresponding to the ID.
        """
        return await self.ai_app_policy_service.get_ai_application_policy_by_id(app_id, id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_ai_application_policy(self, app_id: int, request: AIApplicationPolicyView) -> AIApplicationPolicyView:
        """
        Create a new AI application policy.

        Args:
            app_id (int): The ID of the AI application.
            request (AIApplicationPolicyView): The view object representing the AI application policy to create.

        Returns:
            AIApplicationPolicyView: The created AI application policy view object.
        """
        # Skipping validation for tag exists as it is not required
        # await self.gov_service_validation_util.validate_tag_exists(request.traits)
        await self.acc_service_validation_util.validate_users_exists(request.users)
        await self.acc_service_validation_util.validate_groups_exists(request.groups)
        created_ai_app_policy = await self.ai_app_policy_service.create_ai_application_policy(app_id, request)
        await background_capture_event(event=CreateAIApplicationPolicyEvent(tags=created_ai_app_policy.tags, prompt=created_ai_app_policy.prompt.value, reply=created_ai_app_policy.reply.value))
        return created_ai_app_policy

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_ai_application_policy(self, app_id: int, id: int, request: AIApplicationPolicyView) -> AIApplicationPolicyView:
        """
        Update an AI application policy identified by its ID.

        Args:
            app_id (int): The ID of the AI application.
            id (int): The ID of the AI application policy to update.
            request (AIApplicationPolicyView): The updated view object representing the AI application policy.

        Returns:
            AIApplicationPolicyView: The updated AI application policy view object.
        """

        # Skipping validation for tag exists as it is not required
        # await self.gov_service_validation_util.validate_tag_exists(request.traits)
        await self.acc_service_validation_util.validate_users_exists(request.users)
        await self.acc_service_validation_util.validate_groups_exists(request.groups)
        updated_ai_app_policy = await self.ai_app_policy_service.update_ai_application_policy(app_id, id, request)
        await background_capture_event(event=UpdateAIApplicationPolicyEvent(tags=updated_ai_app_policy.tags, prompt=updated_ai_app_policy.prompt.value, reply=updated_ai_app_policy.reply.value))
        return updated_ai_app_policy

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_ai_application_policy(self, app_id: int, id: int):
        """
        Delete an AI application policy by its ID.

        Args:
            app_id (int): The ID of the AI application.
            id (int): The ID of the AI application policy to delete.
        """
        await self.ai_app_policy_service.delete_ai_application_policy(app_id, id)
