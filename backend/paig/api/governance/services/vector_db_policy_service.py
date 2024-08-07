from typing import List

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND, ERROR_FIELD_REQUIRED, ERROR_INVALID_PERMISSION_PUBLIC_ALLOWED, \
    ERROR_SAME_ACTORS_IN_ALLOWED_DENIED, ERROR_ALLOWED_VALUES
from core.utils import validate_string_data, validate_id, validate_boolean, SingletonDepends
from api.governance.api_schemas.vector_db import VectorDBFilter
from api.governance.api_schemas.vector_db_policy import VectorDBPolicyFilter, VectorDBPolicyView
from api.governance.database.db_models.vector_db_policy_model import VectorDBPolicyModel
from api.governance.database.db_operations.vector_db_policy_repository import VectorDBPolicyRepository
from api.governance.database.db_operations.vector_db_repository import VectorDBRepository


class VectorDBPolicyRequestValidator:
    """
    Validator class for validating Vector DB policy requests.

    Args:
        vector_db_policy_repository (VectorDBPolicyRepository): The repository handling Vector DB database operations.
        vector_db_repository (VectorDBRepository): The repository handling Vector DB database operations.
    """

    def __init__(self, vector_db_policy_repository: VectorDBPolicyRepository = SingletonDepends(VectorDBPolicyRepository), vector_db_repository: VectorDBRepository = SingletonDepends(VectorDBRepository)):
        self.vector_db_policy_repository = vector_db_policy_repository
        self.vector_db_repository = vector_db_repository

    async def validate_create_request(self, request: VectorDBPolicyView):
        """
        Validate a create request for an Vector DB.

        Args:
            request (VectorDBPolicyView): The view object representing the Vector DB to create.
        """
        validate_id(request.vector_db_id, "Vector DB ID")
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_meta_data(request)
        self.validate_actors(request)
        await self.validate_vector_db_exists_by_id(request.vector_db_id)
        vector_db_policy = await self.get_vector_db_policy_by_matching_metadata(request)
        if vector_db_policy:
            raise BadRequestException(get_error_message(
                ERROR_RESOURCE_ALREADY_EXISTS,
                "Vector DB policy", "same meta data key and value",
                f"{vector_db_policy.metadata_key} and {vector_db_policy.metadata_value}"))

    def validate_name(self, name: str):
        """
        Validate the name of an Vector DB.

        Args:
            name (str): The name of the Vector DB.
        """
        validate_string_data(name, "Vector DB Policy name", required=False)

    def validate_description(self, description: str):
        """
        Validate the description of an Vector DB.

        Args:
            description (str): The description of the Vector DB.
        """
        validate_string_data(description, "Vector DB description", required=False, max_length=4000)

    async def validate_vector_db_exists_by_id(self, vector_db_id: int):
        """
        Validate if a Vector DB exists by its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB to check.

        Raises:
            BadRequestException: If the Vector DB does not exist.
        """
        vector_db_filter = VectorDBFilter()
        vector_db_filter.id = vector_db_id
        vector_db_filter.exact_match = True
        records, total_count = await self.vector_db_repository.list_records(filter=vector_db_filter)
        if total_count <= 0:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Vector DB", "ID", vector_db_id))

    def validate_search_request(self, vector_db_id: int):
        """
                Validate a search request for a vector db policies.

                Args:
                    vector_db_id (int): The ID of the AI vector db id to retrieve.
                """
        validate_id(vector_db_id, "Vector DB ID")

    def validate_delete_request(self, vector_db_id, id):
        """
        Validate a delete request for a vector db policy.

        Args:
            vector_db_id (int): The ID of the vector db id to delete.
            id (int): The ID of the vector db policy id to delete.
        """
        self.validate(id, vector_db_id)

    def validate(self, id, vector_db_id):
        validate_id(vector_db_id, "Vector DB ID")
        validate_id(id, "Vector DB policy ID")

    def validate_read_request(self, vector_db_id, id):
        """
        Validate a delete request for a vector db policy.

        Args:
            vector_db_id (int): The ID of the vector db id to delete.
            id (int): The ID of the vector db policy id to delete.
        """
        self.validate(id, vector_db_id)

    async def validate_update_request(self, request: VectorDBPolicyView):
        """
        Validate an update request for an Vector DB policy.

        Args:
           id (int): The ID of the Vector DB policy to update.
           request (VectorDBPolicyView): The updated view object representing the Vector DB policy.

        Raises:
           BadRequestException: If the ID is not a positive integer.
        """
        self.validate(request.id, request.vector_db_id)
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_meta_data(request)
        self.validate_actors(request)
        await self.validate_vector_db_exists_by_id(request.vector_db_id)
        vector_db_policy = await self.get_vector_db_policy_by_matching_metadata(request)
        if vector_db_policy and vector_db_policy.id != request.id:
            raise BadRequestException(get_error_message(
                ERROR_RESOURCE_ALREADY_EXISTS,
                "Vector DB policy", "same meta data key and value",
                f"{vector_db_policy.metadata_key} and {vector_db_policy.metadata_value}"))

    def validate_status(self, status: int):
        """
        Validate the status of a Vector DB policy.

        Args:
            status (int): The status of the Vector DB policy.
        """
        validate_boolean(status, "Vector DB Policy")

    def validate_meta_data(self, request: VectorDBPolicyView):
        """
                Validate the permissions of a Vector DB policy.

                Args:
                    request (AIApplicationPolicyView): The view object representing the Vector DB policy.
                """
        if not request.metadata_key:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Meta data"))

        if not request.metadata_value:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Meta data value"))

        if request.operator != "eq":
            raise BadRequestException(get_error_message(ERROR_ALLOWED_VALUES, "Operator", [request.operator], ["eq"]))

    async def get_vector_db_policy_by_matching_metadata(self, vector_db_policy: VectorDBPolicyView):
        """
        Validate if the Vector DB policy already exists.

        Args:
            vector_db_policy (VectorDBPolicyView): The Vector DB policy to check.

        Raises:
            BadRequestException: If the Vector DB policy already exists.
        """
        if vector_db_policy.status == 0:
            return

        vector_db_policy_filter = VectorDBPolicyFilter()
        vector_db_policy_filter.vector_db_id = vector_db_policy.vector_db_id
        vector_db_policy_filter.status = vector_db_policy.status
        vector_db_policy_filter.metadata_key = vector_db_policy.metadata_key
        vector_db_policy_filter.metadata_value = vector_db_policy.metadata_value
        vector_db_policy_filter.operator = vector_db_policy.operator
        vector_db_policy_filter.exact_match = True

        records, total_count = await self.vector_db_policy_repository.list_records(filter=vector_db_policy_filter)
        if total_count > 0:
            return records[0]
        return None


    def validate_actors(self, request):
        """
        Validate the actors of a Vector DB policy.

        Args:
            request (VectorDBPolicyView): The view object representing the Vector DB policy.
        """
        if not request.allowed_users and not request.allowed_groups and not request.allowed_roles and not request.denied_users and not request.denied_groups and not request.denied_roles:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Users, Groups or Roles in Vector DB policy"))

        if "public" in request.allowed_groups:
            if request.denied_users or request.denied_groups or request.denied_roles:
                raise BadRequestException(get_error_message(ERROR_INVALID_PERMISSION_PUBLIC_ALLOWED))
        else:
            if any(user in request.allowed_users for user in request.denied_users):
                raise BadRequestException(get_error_message(ERROR_SAME_ACTORS_IN_ALLOWED_DENIED))

            if any(group in request.allowed_groups for group in request.denied_groups):
                raise BadRequestException(get_error_message(ERROR_SAME_ACTORS_IN_ALLOWED_DENIED))

            if any(role in request.allowed_roles for role in request.denied_roles):
                raise BadRequestException(get_error_message(ERROR_SAME_ACTORS_IN_ALLOWED_DENIED))


class VectorDBPolicyService(BaseController[VectorDBPolicyModel, VectorDBPolicyView]):
    """
    Service class specifically for handling Vector DB policy entities.

    Args:
        vector_db_policy_repository (VectorDBPolicyRepository): The repository handling Vector DB policy database operations.
        vector_db_policy_request_validator (VectorDBPolicyRequestValidator): The validator for Vector DB policy requests.
    """

    def __init__(self,
                 vector_db_policy_repository: VectorDBPolicyRepository = SingletonDepends(VectorDBPolicyRepository),
                 vector_db_policy_request_validator: VectorDBPolicyRequestValidator = SingletonDepends(VectorDBPolicyRequestValidator)):
        super().__init__(vector_db_policy_repository, VectorDBPolicyModel, VectorDBPolicyView)
        self.vector_db_policy_request_validator = vector_db_policy_request_validator

    def get_repository(self) -> VectorDBPolicyRepository:
        """
        Get the vector db policy repository.

        Returns:
            VectorDBPolicyRepository: The Vector DB repository.
        """
        return self.repository

    async def list_vector_db_policies(self, vector_db_policy_filter: VectorDBPolicyFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Vector DB policies.

        Args:
            vector_db_policy_filter (VectorDBPolicyFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Vector DB policy view objects and metadata.
        """
        return await self.list_records(
            filter=vector_db_policy_filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_vector_db_policy(self, vector_db_id: int, request: VectorDBPolicyView) -> VectorDBPolicyView:
        """
        Create a new Vector DB policy.

        Args:
            vector_db_id (int): The ID of the Vector DB to associate the policy with.
            request (VectorDBPolicyView): The view object representing the Vector DB to create.

        Returns:
            VectorDBPolicyView: The created Vector DB view object.
        """
        request.vector_db_id = vector_db_id
        await self.vector_db_policy_request_validator.validate_create_request(request)
        return await self.create_record(request)

    async def get_vector_db_policy_by_id(self, vector_db_id: int, id: int) -> VectorDBPolicyView:
        """
        Retrieve a Vector DB policy by its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB policy to retrieve.

        Returns:
            VectorDBPolicyView: The Vector DB policy view object corresponding to the ID.
        """
        return await self.get_vector_db_policy_by_id_and_vector_db_id(vector_db_id, id)

    async def get_vector_db_policy_by_id_and_vector_db_id(self, vector_db_id: int, id: int) -> VectorDBPolicyView:
        """
        Retrieve a Vector DB policy by its ID and Vector DB ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB policy to retrieve.

        Returns:
            AIApplicationPolicyModel: The Vector DB policy model corresponding to the ID.
        """
        self.vector_db_policy_request_validator.validate_read_request(vector_db_id, id)
        vector_db_policy_filter = VectorDBPolicyFilter()
        vector_db_policy_filter.vector_db_id = vector_db_id
        vector_db_policy_filter.id = id
        vector_db_policy_filter.exact_match = True
        records, total_count = await self.repository.list_records(filter=vector_db_policy_filter)
        if total_count == 0:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB policy", "Id", [id]))
        return records[0]

    async def delete_vector_db_policy(self, vector_db_id: int, id: int):
        """
        Delete a Vector DB policy by its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB policy to delete.
        """
        self.vector_db_policy_request_validator.validate_delete_request(vector_db_id, id)
        # get the policy by id and vector db id to check if it exists
        await self.get_vector_db_policy_by_id_and_vector_db_id(vector_db_id, id)
        await self.delete_record(id)

    async def update_vector_db_policy(self, vector_db_id: int, id: int, request: VectorDBPolicyView) -> VectorDBPolicyView:
        """
        Update a Vector DB policy identified by its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB policy to update.
            request (AIApplicationPolicyView): The updated view object representing the Vector DB policy.

        Returns:
            AIApplicationPolicyView: The updated Vector DB policy view object.
        """
        request.vector_db_id = vector_db_id
        request.id = id
        # get the policy by id and Vector DB id to check if it exists
        await self.get_vector_db_policy_by_id_and_vector_db_id(vector_db_id, id)
        await self.vector_db_policy_request_validator.validate_update_request(request)
        return await self.update_record(id, request)

    async def list_vector_db_authorization_policies(self, vector_db_id: int, user: str, groups: List[str]) -> List[VectorDBPolicyView]:
        """
        List policies for authorization.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            user (str): The user to authorize.
            groups (List[str]): The groups to authorize.

        Returns:
            List[VectorDBPolicyModel]: The list of Vector DB policies.
        """
        repository = self.get_repository()
        return await repository.list_policies_for_authorization(vector_db_id, user, groups)
