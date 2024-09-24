from typing import List

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND, \
    ERROR_RESOURCE_ALREADY_EXISTS, ERROR_FIELD_REQUIRED
from core.utils import validate_id, validate_string_data, validate_boolean, SingletonDepends
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView, AIApplicationPolicyFilter
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel
from api.governance.database.db_operations.ai_app_policy_repository import AIAppPolicyRepository
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from core.middlewares.usage import background_capture_event
from core.factory.events import DeleteAIApplicationPolicyEvent


class AIAppPolicyRequestValidator:
    """
    Validator class for validating AI application policy requests.

    Args:
        ai_app_policy_repository (AIAppPolicyRepository): The repository handling AI application policy database operations.
    """

    def __init__(self, ai_app_policy_repository: AIAppPolicyRepository = SingletonDepends(AIAppPolicyRepository), ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository)):
        self.ai_app_policy_repository = ai_app_policy_repository
        self.ai_app_repository = ai_app_repository

    async def validate_create_request(self, request: AIApplicationPolicyView):
        """
        Validate a create request for an AI application policy.

        Args:
            request (AIApplicationPolicyView): The view object representing the AI application policy to create.
        """
        validate_id(request.application_id, "AI Application ID")
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_tags(request.tags)
        self.validate_actors(request)
        await self.validate_ai_application_exists_by_id(request.application_id)
        await self.validate_application_policy_already_exists(request)

    def validate_status(self, status: int):
        """
        Validate the status of an AI application policy.

        Args:
            status (int): The status of the AI application policy.
        """
        validate_boolean(status, "AI Application Policy status")

    def validate_name(self, name: str):
        """
        Validate the name of an AI application policy.

        Args:
            name (str): The name of the AI application policy.
        """
        validate_string_data(name, "AI Application Policy name", required=False)

    def validate_description(self, description: str):
        """
        Validate the description of an AI application policy.

        Args:
            description (str): The description of the AI application policy.
        """
        validate_string_data(description, "AI Application policy description", required=False, max_length=4000)

    def validate_tags(self, tags: list[str]):
        """
        Validate the tags of an AI application policy.

        Args:
            tags (list[str]): The tags of the AI application policy.
        """
        if not tags:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Tags"))

    async def validate_application_policy_already_exists(self, ai_application_policy: AIApplicationPolicyView):
        """
        Check if an AI application policy already exists by matching description or tags and permissions.

        Args:
            ai_application_policy (AIApplicationPolicyView): The AI application policy to check.

        Raises:
            BadRequestException: If an AI application policy with the same description/tags already exists.
        """
        ai_app_policy = await self.get_application_policy_with_same_description(ai_application_policy)
        if ai_app_policy is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS,
                                                        "AI application policy",
                                                        "description",
                                                        [ai_application_policy.description]))

        ai_app_policy = await self.get_application_policy_with_same_tags(ai_application_policy)
        if ai_app_policy is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS,
                                                        "AI application policy",
                                                        "tags",
                                                        ai_application_policy.tags))

    async def get_application_policy_with_same_description(self, ai_application_policy: AIApplicationPolicyView):
        """
        Retrieve an AI application policy by matching description.

        Args:
            ai_application_policy (AIApplicationPolicyView): The AI application policy to retrieve.

        Returns:
            AIApplicationModel: The AI application model corresponding to the name.
        """
        if ai_application_policy.status == 0:
            return None

        ai_app_policy_filter = AIApplicationPolicyFilter()
        ai_app_policy_filter.application_id = ai_application_policy.application_id
        ai_app_policy_filter.status = ai_application_policy.status
        ai_app_policy_filter.description = ai_application_policy.description
        ai_app_policy_filter.exact_match = True

        records, total_count = await self.ai_app_policy_repository.list_records(filter=ai_app_policy_filter)
        for record in records:
            if record.id != ai_application_policy.id:
                return record

        return None

    async def get_application_policy_with_same_tags(self, ai_application_policy: AIApplicationPolicyView):
        """
        Retrieve an AI application policy by matching tags and permissions.

        Args:
            ai_application_policy (AIApplicationPolicyView): The AI application policy to retrieve.

        Returns:
            AIApplicationModel: The AI application model corresponding to the name.
        """
        if ai_application_policy.status == 0:
            return None

        ai_app_policy_filter = AIApplicationPolicyFilter()
        ai_app_policy_filter.application_id = ai_application_policy.application_id
        ai_app_policy_filter.status = ai_application_policy.status
        ai_app_policy_filter.tags = ",".join(ai_application_policy.tags) if isinstance(ai_application_policy.tags,
                                                                                       list) else ai_application_policy.tags
        ai_app_policy_filter.prompt = ai_application_policy.prompt
        ai_app_policy_filter.reply = ai_application_policy.reply
        ai_app_policy_filter.enriched_prompt = ai_application_policy.enriched_prompt
        ai_app_policy_filter.exact_match = True

        records, total_count = await self.ai_app_policy_repository.list_records(filter=ai_app_policy_filter)
        for record in records:
            if record.id != ai_application_policy.id and sorted(record.tags) == sorted(ai_application_policy.tags) :
                return record

        return None

    async def validate_update_request(self, request):
        """
        Validate an update request for an AI application policy.

        Args:
           id (int): The ID of the AI application policy to update.
           request (AIApplicationPolicyView): The updated view object representing the AI application policy.

        Raises:
           BadRequestException: If the ID is not a positive integer.
        """
        self.validate(request.application_id, request.id)
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_tags(request.tags)
        self.validate_actors(request)
        await self.validate_application_policy_already_exists(request)

    def validate_delete_request(self, app_id, id):
        """
        Validate a delete request for an AI application policy.

        Args:
            app_id (int): The ID of the AI application id to delete.
            id (int): The ID of the AI application id to delete.
        """
        self.validate(app_id, id)

    def validate_read_request(self, app_id, id):
        """
       Validate a delete request for an AI application policy.

       Args:
           id (int): The ID of the AI application id to delete.
       """
        self.validate(app_id, id)

    def validate(self, app_id, id):
        validate_id(app_id, "AI Application ID")
        validate_id(id, "AI Application policy ID")

    def validate_search_request(self, app_id):
        """
        Validate a search request for an AI application policies.

        Args:
            app_id (int): The ID of the AI application id to retrieve.
        """
        validate_id(app_id, "AI Application ID")

    async def validate_ai_application_exists_by_id(self, app_id: int):
        """
        Check if an AI application exists by its ID.

        Args:
            app_id (int): The ID of the AI application.
        """
        record = await self.ai_app_repository.get_record_by_id(app_id)
        if record is None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "AI Application", "ID", [app_id]))

    def validate_actors(self, request):
        """
        Validate the actors of an AI application policy.

        Args:
            request (AIApplicationPolicyView): The view object representing the AI application policy.
        """
        if not request.users and not request.groups and not request.roles:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Users, Groups or Roles in AI Application policy"))


class AIAppPolicyService(BaseController[AIApplicationPolicyModel, AIApplicationPolicyView]):
    """
    Service class specifically for handling AI application policies.

    Args:
        ai_app_policy_repository (AIAppPolicyRepository): The repository handling AI application policy database operations.
    """

    def __init__(self, ai_app_policy_repository: AIAppPolicyRepository = SingletonDepends(AIAppPolicyRepository), policy_request_validator: AIAppPolicyRequestValidator = SingletonDepends(AIAppPolicyRequestValidator)):
        super().__init__(ai_app_policy_repository, AIApplicationPolicyModel, AIApplicationPolicyView)
        self.policy_request_validator = policy_request_validator

    def get_repository(self) -> AIAppPolicyRepository:
        """
        Get the AI application repository.

        Returns:
            AIAppPolicyRepository: The AI application repository.
        """
        return self.repository

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
        return await self.list_records(
            filter=app_policy_filter,
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
        self.policy_request_validator.validate_read_request(app_id, id)
        return await self.get_policy_by_id_and_application_id(app_id, id)

    async def get_policy_by_id_and_application_id(self, app_id, id):
        """
        Retrieve an AI application policy by its ID and application ID.

        Args:
            app_id (int): The ID of the AI application.
            id (int): The ID of the AI application policy to retrieve.

        Returns:
            AIApplicationPolicyModel: The AI application policy model corresponding to the ID.
        """
        app_policy_filter = AIApplicationPolicyFilter()
        app_policy_filter.application_id = app_id
        app_policy_filter.id = id
        app_policy_filter.exact_match = True
        records, total_count = await self.repository.list_records(filter=app_policy_filter)
        if total_count == 0:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "AI application policy", "Id", [id]))
        return records[0]

    async def create_ai_application_policy(self, app_id: int, request: AIApplicationPolicyView) -> AIApplicationPolicyView:
        """
        Create a new AI application policy.

        Args:
            app_id (int): The ID of the AI application.
            request (AIApplicationPolicyView): The view object representing the AI application policy to create.

        Returns:
            AIApplicationPolicyView: The created AI application policy view object.
        """
        request.application_id = app_id
        await self.policy_request_validator.validate_create_request(request)
        return await self.create_record(request)

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
        request.application_id = app_id
        request.id = id
        await self.policy_request_validator.validate_update_request(request)
        # get the policy by id and application id to check if it exists
        await self.get_policy_by_id_and_application_id(app_id, id)
        return await self.update_record(id, request)

    async def delete_ai_application_policy(self, app_id: int, id: int):
        """
        Delete an AI application policy by its ID.

        Args:
            app_id (int): The ID of the AI application.
            id (int): The ID of the AI application policy to delete.
        """
        self.policy_request_validator.validate_delete_request(app_id, id)
        # get the policy by id and application id to check if it exists
        ai_app_policy = await self.get_policy_by_id_and_application_id(app_id, id)
        await self.delete_record(id)
        await background_capture_event(event=DeleteAIApplicationPolicyEvent(tags=ai_app_policy.tags, prompt=ai_app_policy.prompt.value, reply=ai_app_policy.reply.value))

    async def list_ai_application_authorization_policies(self, app_id: int, traits: List[str], user: str, groups: List[str]) -> List[AIApplicationPolicyView]:
        """
        List AI application policies for authorization.

        Args:
            app_id (int): The ID of the AI application.
            traits (List[str]): The list of traits to filter by.
            user (str): The user to filter by.
            groups (List[str]): The list of groups to filter by.

        Returns:
            List[AIApplicationPolicyModel]: A list of AI application policy models.
        """
        repository = self.get_repository()
        return await repository.list_policies_for_authorization(app_id, traits, user, groups)