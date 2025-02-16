import json
from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.ai_app import AIApplicationView, AIApplicationFilter, GuardrailApplicationsAssociation
from api.governance.api_schemas.ai_app_config import AIApplicationConfigView
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView
from api.governance.services.ai_app_config_service import AIAppConfigService
from api.governance.services.ai_app_policy_service import AIAppPolicyService
from api.governance.services.ai_app_service import AIAppService
from core.utils import format_to_root_path, SingletonDepends
from core.middlewares.usage import background_capture_event
from core.factory.events import CreateAIApplicationEvent, UpdateAIApplicationEvent, DeleteAIApplicationEvent


class AIAppController:
    """
    Controller class specifically for handling AI application entities.

    Args:
        ai_app_service (AIAppService): The service class for handling AI application entities.
    """

    def __init__(self,
                 ai_app_service: AIAppService = SingletonDepends(AIAppService),
                 ai_app_policy_service: AIAppPolicyService = SingletonDepends(AIAppPolicyService),
                 ai_app_config_service: AIAppConfigService = SingletonDepends(AIAppConfigService)):
        self.ai_app_service = ai_app_service
        self.ai_app_policy_service = ai_app_policy_service
        self.ai_app_config_service = ai_app_config_service

        ai_app_defaults_file_path = format_to_root_path("api/governance/configs/ai_application_defaults.json")
        application_defaults = self.get_application_defaults(ai_app_defaults_file_path)

        # Parse the data into Pydantic models
        self.ai_app_default_config = AIApplicationConfigView.model_validate(application_defaults['configs'])
        self.ai_app_default_policies = [AIApplicationPolicyView.model_validate(policy) for policy in
                                        application_defaults['policies']]

    def get_application_defaults(self, application_defaults_file_path) -> dict:
        data = {}
        with open(application_defaults_file_path, 'r') as file:
            data = json.load(file)
        return data

    async def list_ai_applications(self, filter: AIApplicationFilter, page_number: int, size: int,
                                   sort: List[str]) -> Pageable:
        """
        List AI applications based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (AIApplicationFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of AI applications.
        """
        return await self.ai_app_service.list_ai_applications(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_ai_application(self, request: AIApplicationView) -> AIApplicationView:
        """
        Create a new AI application.

        Args:
            request (AIApplicationView): The view object representing the AI application to create.

        Returns:
            AIApplicationView: The created AI application view object.
        """
        created_app = await self.ai_app_service.create_ai_application(request)

        app_config_create_model = AIApplicationConfigView(**self.ai_app_default_config.model_dump())
        await self.ai_app_config_service.update_ai_app_config(created_app.id, app_config_create_model)

        for policy in self.ai_app_default_policies:
            policy_create_view = AIApplicationPolicyView(**policy.model_dump())
            await self.ai_app_policy_service.create_ai_application_policy(created_app.id, policy_create_view)
        await background_capture_event(event=CreateAIApplicationEvent())
        return created_app

    async def get_ai_application_by_id(self, id: int) -> AIApplicationView:
        """
        Retrieve an AI application by its ID.

        Args:
            id (int): The ID of the AI application to retrieve.

        Returns:
            AIApplicationView: The AI application view object corresponding to the ID.
        """
        return await self.ai_app_service.get_ai_application_by_id(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_ai_application(self, id: int, request: AIApplicationView) -> AIApplicationView:
        """
        Update an AI application identified by its ID.

        Args:
            id (int): The ID of the AI application to update.
            request (AIApplicationView): The updated view object representing the AI application.

        Returns:
            AIApplicationView: The updated AI application view object.
        """
        updated_app = await self.ai_app_service.update_ai_application(id, request)
        await background_capture_event(event=UpdateAIApplicationEvent())
        return updated_app

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_ai_application(self, id: int):
        """
        Delete an AI application by its ID.

        Args:
            id (int): The ID of the AI application to delete.
        """
        await self.ai_app_service.delete_ai_application(id)
        await background_capture_event(event=DeleteAIApplicationEvent())

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_guardrail_application_association(self, request: GuardrailApplicationsAssociation):
        """
        Associates or disassociates applications with a given guardrail.

        - Applications in `request.applications` will be associated with the guardrail.
        - Applications currently linked to the guardrail but missing from `request.applications` will be disassociated.

        Args:
            request (GuardrailAssociationRequest): Guardrail name and list of applications.

        Returns:
            GuardrailApplicationsAssociation: Updated associations.
        """
        return await self.ai_app_service.update_guardrail_application_association(request)
