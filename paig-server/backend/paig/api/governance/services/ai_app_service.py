import copy
from typing import List

import sqlalchemy

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND, ERROR_FIELD_CANNOT_BE_UPDATED
from core.utils import validate_id, validate_string_data, validate_boolean, generate_unique_identifier_key, \
    SingletonDepends
from api.governance.api_schemas.ai_app import AIApplicationView, AIApplicationFilter, GuardrailApplicationsAssociation
from api.governance.api_schemas.vector_db import VectorDBFilter
from api.governance.database.db_models.ai_app_model import AIApplicationModel
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from api.governance.database.db_operations.vector_db_repository import VectorDBRepository
from core.constants import PORT
from core.config import load_config_file

config = load_config_file()


class AIAppRequestValidator:
    """
    Validator class for validating AI application requests.

    Args:
        ai_app_repository (AIAppRepository): The repository handling AI application database operations.
    """

    def __init__(self, ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository),
                 vector_db_repository: VectorDBRepository = SingletonDepends(VectorDBRepository)):
        self.ai_app_repository = ai_app_repository
        self.vector_db_repository = vector_db_repository

    async def validate_create_request(self, request: AIApplicationView):
        """
        Validate a create request for an AI application.

        Args:
            request (AIApplicationView): The view object representing the AI application to create.
        """
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        await self.validate_application_exists_by_name(request.name)

        if request.vector_dbs:
            await self.validate_ai_application_vector_db_exists_by_name(request.vector_dbs)

    def validate_status(self, status: int):
        """
        Validate the status of an AI application.

        Args:
            status (int): The status of the AI application.
        """
        validate_boolean(status, "AI application status")

    def validate_read_request(self, id: int):
        """
        Validate a read request for an AI application.

        Args:
            id (int): The ID of the AI application to retrieve.
        """
        validate_id(id, "AI application ID")

    async def validate_update_request(self, id: int, request: AIApplicationView):
        """
        Validate an update request for an AI application.

        Args:
            id (int): The ID of the AI application to update.
            request (AIApplicationView): The updated view object representing the AI application.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "AI application ID")
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)

        ai_app = await self.get_application_by_name(request.name)
        if ai_app is not None and ai_app.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "AI application", "name",
                                                        [request.name]))

        ai_app_by_id = None
        try:
            ai_app_by_id = await self.ai_app_repository.get_record_by_id(id)
        except sqlalchemy.exc.NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Resource", "id", [id]))

        if ai_app_by_id is not None and ai_app_by_id.application_key != request.application_key:
            raise BadRequestException(
                get_error_message(ERROR_FIELD_CANNOT_BE_UPDATED, "AI application", "applicationKey"))

        if request.vector_dbs:
            await self.validate_ai_application_vector_db_exists_by_name(request.vector_dbs)

    def validate_delete_request(self, id: int):
        """
        Validate a delete request for an AI application.

        Args:
            id (int): The ID of the AI application to delete.
        """
        validate_id(id, "AI application ID")

    def validate_name(self, name: str):
        """
        Validate the name of an AI application.

        Args:
            name (str): The name of the AI application.
        """
        validate_string_data(name, "AI Application name")

    def validate_description(self, description: str):
        """
        Validate the description of an AI application.

        Args:
            description (str): The description of the AI application.
        """
        validate_string_data(description, "AI Application description", required=False, max_length=4000)

    def validate_application_key(self, application_key: str):
        """
        Validate the application key of an AI application.

        Args:
            application_key (str): The application key of the AI application.
        """
        validate_string_data(application_key, "AI Application key")

    async def validate_application_exists_by_name(self, name: str):
        """
        Check if an AI application already exists by its name.

        Args:
            name (str): The name of the AI application.

        Raises:
            BadRequestException: If an AI application with the same name already exists.
        """
        ai_app = await self.get_application_by_name(name)
        if ai_app is not None:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "AI application", "name", [name]))

    async def get_application_by_name(self, name: str):
        """
        Retrieve an AI application by its name.

        Args:
            name (str): The name of the AI application.

        Returns:
            AIApplicationModel: The AI application model corresponding to the name.
        """
        filter = AIApplicationFilter()
        filter.name = name
        filter.exact_match = True
        records, total_count = await self.ai_app_repository.list_records(filter=filter)
        if total_count > 0:
            return records[0]
        return None

    async def validate_ai_application_vector_db_exists_by_name(self, name: List[str]):
        """
        Validate if the vector DBs exist by their names.

        Args:
            name (List[str]): The names of the vector DBs.

        Raises:
            BadRequestException: If any of the vector DBs do not exist.
        """
        vector_db_names = ",".join(name)
        vector_db_filter = VectorDBFilter()
        vector_db_filter.name = vector_db_names
        vector_db_filter.exact_match = True
        records, total_count = await self.vector_db_repository.list_records(filter=vector_db_filter)
        if len(name) != total_count:
            vector_db_names_from_db = [record.name for record in records]
            invalid_vector_db_names = list(set(name) - set(vector_db_names_from_db))
            raise BadRequestException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB", "names",
                                                        invalid_vector_db_names))


class AIAppService(BaseController[AIApplicationModel, AIApplicationView]):

    def __init__(self, ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository),
                 ai_app_request_validator: AIAppRequestValidator = SingletonDepends(AIAppRequestValidator)):
        """
        Initialize the AIAppService.

        Args:
            ai_app_repository (AIAppRepository): The repository handling AI application database operations.
        """
        super().__init__(
            ai_app_repository,
            AIApplicationModel,
            AIApplicationView
        )
        self.ai_app_request_validator = ai_app_request_validator

    def get_repository(self) -> AIAppRepository:
        """
        Get the AI application repository.

        Returns:
            AIAppRepository: The AI application repository.
        """
        return self.repository

    async def list_ai_applications(self, filter: AIApplicationFilter, page_number: int, size: int,
                                   sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of AI applications.

        Args:
            filter (AIApplicationFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing AI application view objects and metadata.
        """
        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def list_ai_applications_by_vector_db(self, vector_db_name: str) -> List[AIApplicationView]:
        """
        Retrieve a list of AI applications by vector DB name.

        Args:
            vector_db_name (str): The name of the vector DB.

        Returns:
            List[AIApplicationView]: A list of AI application view objects.
        """
        return await self.repository.get_all({"vector_dbs": vector_db_name}, apply_in_list_filter=True)

    async def create_ai_application(self, request: AIApplicationView) -> AIApplicationView:
        """
        Create a new AI application.

        Args:
            request (AIApplicationView): The view object representing the AI application to create.

        Returns:
            AIApplicationView: The created AI application view object.
        """
        await self.ai_app_request_validator.validate_create_request(request)
        request.application_key = generate_unique_identifier_key()
        return await self.create_record(request)

    async def get_ai_application_by_id(self, id: int) -> AIApplicationView:
        """
        Retrieve an AI application by its ID.

        Args:
            id (int): The ID of the AI application to retrieve.

        Returns:
            AIApplicationView: The AI application view object corresponding to the ID.
        """
        self.ai_app_request_validator.validate_read_request(id)
        return await self.get_record_by_id(id)

    async def get_ai_application_by_application_key(self, application_key: str) -> AIApplicationView:
        """
        Retrieve an AI application by its application key.

        Args:
            application_key (str): The application key of the AI application to retrieve.

        Returns:
            AIApplicationView: The AI application view object corresponding to the application key.
        """
        repository = self.get_repository()
        return await repository.get_ai_application_by_application_key(application_key)

    async def update_ai_application(self, id: int, request: AIApplicationView) -> AIApplicationView:
        """
        Update an AI application identified by its ID.

        Args:
            id (int): The ID of the AI application to update.
            request (AIApplicationView): The updated view object representing the AI application.

        Returns:
            AIApplicationView: The updated AI application view object.
        """
        await self.ai_app_request_validator.validate_update_request(id, request)
        return await self.update_record(id, request)

    async def delete_ai_application(self, id: int):
        """
        Delete an AI application by its ID.

        Args:
            id (int): The ID of the AI application to delete.
        """
        self.ai_app_request_validator.validate_delete_request(id)
        await self.delete_record(id)

    @staticmethod
    async def get_shield_server_url():
        """
        Get the shield server URL.

        Returns:
            str: The shield server URL.
        """
        if config.get("default_shield_server_url"):
            return config.get("default_shield_server_url")
        return f"http://127.0.0.1:{PORT}"

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
        result = GuardrailApplicationsAssociation(guardrail=request.guardrail, applications=[])
        await self.disassociate_guardrail(request)
        associated_apps = await self.associate_guardrail(request)
        result.applications = associated_apps

        return result

    async def associate_guardrail(self, request: GuardrailApplicationsAssociation):
        applications = []
        ai_apps_by_names: List[AIApplicationModel] = await self.repository.get_all(
            {"name": ','.join(request.applications)})
        updated_apps = []
        for ai_app in ai_apps_by_names:
            ai_app.guardrails = list(set(ai_app.guardrails + [request.guardrail]))
            applications.append(ai_app.name)
            updated_apps.append(ai_app)
        await self.repository.update_all_records(updated_apps)
        return applications

    async def disassociate_guardrail(self, request: GuardrailApplicationsAssociation):
        ai_apps_by_names: List[AIApplicationModel] = await self.repository.get_all(
            {"guardrails": request.guardrail})
        updated_apps = []
        for ai_app in ai_apps_by_names:
            if ai_app.name not in request.applications:
                ai_app.guardrails = [gr for gr in ai_app.guardrails if gr != request.guardrail]
                updated_apps.append(ai_app)
        await self.repository.update_all_records(updated_apps)
