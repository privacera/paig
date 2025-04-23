from typing import List

from sqlalchemy.exc import NoResultFound

from api.guardrails import ResponseTemplateType
from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND
from core.utils import validate_id, validate_string_data, SingletonDepends
from api.guardrails.api_schemas.response_template import ResponseTemplateView, ResponseTemplateFilter
from api.guardrails.database.db_models.response_template_model import ResponseTemplateModel
from api.guardrails.database.db_operations.response_template_repository import ResponseTemplateRepository


class ResponseTemplateRequestValidator:
    """
    Validator class for validating ResponseTemplate requests.

    Args:
        response_template_repository (ResponseTemplateRepository): The repository handling Response Template table database operations.
    """

    def __init__(self, response_template_repository: ResponseTemplateRepository = SingletonDepends(ResponseTemplateRepository)):
        self.response_template_repository = response_template_repository

    async def validate_create_request(self, request: ResponseTemplateView):
        """
        Validate a create request for ResponseTemplate.

        Args:
            request (ResponseTemplateView): The view object representing the ResponseTemplate to create.
        """
        self.validate_type(request)
        self.validate_response(request.response)
        self.validate_description(request.description)
        await self.validate_response_template_exists_by_response(request.response)

    def validate_read_request(self, id: int):
        """
        Validate a read request for ResponseTemplate.

        Args:
            id (int): The ID of the ResponseTemplate to retrieve.
        """
        validate_id(id, "Response Template ID")

    async def validate_update_request(self, id: int, request: ResponseTemplateView):
        """
        Validate an update request for ResponseTemplate.

        Args:
            id (int): The ID of the ResponseTemplate to update.
            request (ResponseTemplateView): The updated view object representing the ResponseTemplate.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        self.validate_type(request)
        validate_id(id, "Response Template ID")
        self.validate_response(request.response)
        self.validate_description(request.description)

        await self.validate_response_templated_is_not_system_generated(id)

        response_template = await self.get_response_template_by_response(request.response)
        if response_template is not None and response_template.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Response Template", "response",
                                                        [request.response]))

    def validate_type(self, request: ResponseTemplateView):
        """
        Validate the type of the request.

        Args:
            request (ResponseTemplateView): The view object representing the ResponseTemplate to update.

        Raises:
            BadRequestException: If the type is not a valid ResponseTemplateView.
        """
        if request.type == ResponseTemplateType.SYSTEM_DEFINED:
            raise BadRequestException("System-generated Response templates cannot be added, updated or deleted")

    async def validate_delete_request(self, id: int):
        """
        Validate a delete request for ResponseTemplate.

        Args:
            id (int): The ID of the ResponseTemplate to delete.
        """
        validate_id(id, "Response Template ID")
        await self.validate_response_templated_is_not_system_generated(id)

    async def validate_response_templated_is_not_system_generated(self, id):
        """
        Validate if the ResponseTemplate is not a system generated template.

        Args:
            id (int): The ID of the ResponseTemplate to validate.

        Raises:
            BadRequestException: If the ResponseTemplate is a system generated template.
        """
        response_template = await self.response_template_repository.get_response_templates_by_id(id)
        self.validate_type(response_template)

    def validate_response(self, response: str):
        """
        Validate the response of ResponseTemplate.

        Args:
            response (str): The response of the ResponseTemplate.
        """
        validate_string_data(response, "Response Template response")

    def validate_description(self, description: str):
        """
        Validate the description of the ResponseTemplate.

        Args:
            description (str): The description of the ResponseTemplate.
        """
        validate_string_data(description, "Response Template description", required=False, max_length=4000)

    async def validate_response_template_exists_by_response(self, response: str):
        """
        Check if a ResponseTemplate already exists by its response.

        Args:
            response (str): The response of the ResponseTemplate.

        Raises:
            BadRequestException: If the ResponseTemplate with the same response already exists.
        """
        response_template = await self.get_response_template_by_response(response)
        if response_template is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Response Template", "response", [response]))

    async def get_response_template_by_response(self, response: str):
        """
        Retrieve ResponseTemplate by its response.

        Args:
            response (str): The response of the ResponseTemplate.

        Returns:
            ResponseTemplateModel: The ResponseTemplate model corresponding to the response.
        """
        response_template_filter = ResponseTemplateFilter()
        response_template_filter.response = response
        response_template_filter.exact_match = True
        response_template_filter.value_with_comma = True
        response_template_filter.type = ResponseTemplateType.SYSTEM_DEFINED
        response_template_filter.or_column_list = "tenant_id,type"
        records, total_count = await self.response_template_repository.list_records(filter=response_template_filter)
        if total_count > 0:
            return records[0]
        return None


class ResponseTemplateService(BaseController[ResponseTemplateModel, ResponseTemplateView]):

    def __init__(self, response_template_repository: ResponseTemplateRepository = SingletonDepends(ResponseTemplateRepository),
                 response_template_request_validator: ResponseTemplateRequestValidator = SingletonDepends(ResponseTemplateRequestValidator)):
        """
        Initialize the ResponseTemplateService.

        Args:
            response_template_repository (ResponseTemplateRepository): The repository handling ResponseTemplate database operations.
            response_template_request_validator (ResponseTemplateRequestValidator): The validator for validating ResponseTemplate requests.
        """
        super().__init__(
            response_template_repository,
            ResponseTemplateModel,
            ResponseTemplateView
        )
        self.response_template_request_validator = response_template_request_validator

    def get_repository(self) -> ResponseTemplateRepository:
        """
        Get the ResponseTemplate repository.

        Returns:
            ResponseTemplateRepository: The ResponseTemplate repository.
        """
        return self.repository

    async def list_response_templates(self, filter: ResponseTemplateFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of ResponseTemplate.

        Args:
            filter (ResponseTemplateFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing ResponseTemplate view objects and other fields.
        """
        # To find records by tenant id or by SYSTEM_DEFINED type, set the or_column_list filter
        filter.type = filter.type or ResponseTemplateType.SYSTEM_DEFINED

        if filter.type == ResponseTemplateType.SYSTEM_DEFINED:
            filter.or_column_list = "tenant_id,type"

        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_response_template(self, request: ResponseTemplateView) -> ResponseTemplateView:
        """
        Create a new ResponseTemplate.

        Args:
            request (ResponseTemplateView): The view object representing the ResponseTemplate to create.

        Returns:
            ResponseTemplateView: The created ResponseTemplate view object.
        """
        await self.response_template_request_validator.validate_create_request(request)
        return await self.create_record(request)

    async def get_response_template_by_id(self, id: int) -> ResponseTemplateView:
        """
        Retrieve ResponseTemplate by its ID.

        Args:
            id (int): The ID of the ResponseTemplate to retrieve.

        Returns:
            ResponseTemplateView: The ResponseTemplate view object corresponding to the ID.
        """
        self.response_template_request_validator.validate_read_request(id)
        return await self.get_repository().get_response_templates_by_id(id)

    async def update_response_template(self, id: int, request: ResponseTemplateView) -> ResponseTemplateView:
        """
        Update ResponseTemplate identified by its ID.

        Args:
            id (int): The ID of the ResponseTemplate to update.
            request (ResponseTemplateView): The updated view object representing the ResponseTemplate.

        Returns:
            ResponseTemplateView: The updated ResponseTemplate view object.
        """
        await self.response_template_request_validator.validate_update_request(id, request)
        return await self.update_record(id, request)

    async def delete_response_template(self, id: int):
        """
        Delete ResponseTemplate by its ID.

        Args:
            id (int): The ID of the ResponseTemplate to delete.
        """
        await self.response_template_request_validator.validate_delete_request(id)
        await self.delete_record(id)