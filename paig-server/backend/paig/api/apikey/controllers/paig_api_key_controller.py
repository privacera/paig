from api.apikey.services.paig_api_key_service import PaigApiKeyService
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.controllers.paginated_response import create_pageable_response
from api.apikey.api_schemas.paig_api_key import GenerateApiKeyResponse

class PaigApiKeyController:
    """
    Controller class for handling API key operations.

    This class contains methods for interacting with the PaigApiKeyService.
    """

    def __init__(self):
        """
        Initialize the PaigApiKeyController.
        """
        self._api_key_service = PaigApiKeyService()

    async def get_api_keys_by_application_id_with_filters(self, application_id, include_filters, page, size, sort, key_status):
        """
        Retrieve API keys by their application ID.

        Args:
            application_id (int): The ID of the application to retrieve API keys for.
            include_filters (dict): The filters to apply to the API keys.
            page (int): The page number to retrieve.
            size (int): The number of items per page.
            sort (str): The sort options.
            key_status (list): The key status options.
        """
        if include_filters.api_key_name:
            include_filters.api_key_name = include_filters.api_key_name.strip("*")
        if include_filters.description:
            include_filters.description = include_filters.description.strip("*")
        # return await self._api_key_service.get_api_keys_by_application_id(application_id, include_filters, page, size, sort, key_status)
        api_key_results, total_count = await self._api_key_service.get_api_keys_by_application_id(application_id, include_filters, page, size, sort, key_status)
        if api_key_results is None:
            raise NotFoundException("No results found")
        api_key_results_list = [ api_key_result.to_ui_dict() for api_key_result in api_key_results]
        return create_pageable_response(api_key_results_list, total_count, page, size, [sort])



    async def get_api_key_by_ids(self, api_key_ids: list):
        """
        Retrieve API keys by their IDs.

        Args:
            api_key_ids (list): The IDs of the API keys to retrieve.
        """
        return await self._api_key_service.get_api_key_by_ids(api_key_ids)

    async def create_api_key(self, request: dict):
        """
        Create a new API key.

        Args:
            request (dict): The request object containing the API key and description.
        """
        return await self._api_key_service.create_api_key(request)


    async def disable_api_key(self, api_key_id: int):
        """
        Delete an API key by its ID.

        Args:
            api_key_id (int): The ID of the API key to delete.
        """
        return await self._api_key_service.disable_api_key(api_key_id)

    async def permanent_delete_api_key(self, api_key_id: int):
        """
        Permanently delete an API key by its ID.

        Args:
            api_key_id (int): The ID of the API key to permanently delete.
        """
        return await self._api_key_service.permanent_delete_api_key(api_key_id)


