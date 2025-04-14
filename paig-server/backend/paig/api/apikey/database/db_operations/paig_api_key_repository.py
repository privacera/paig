from sqlalchemy.exc import NoResultFound
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.factory.database_initiator import BaseOperations
from api.apikey.database.db_models.paig_api_key_model import PaigApiKeyModel
from core.db_session import session
from sqlalchemy.future import select
from core.utils import get_field_name_by_alias
from api.apikey.api_schemas.paig_api_key import PaigApiKeyView
from sqlalchemy import and_
from api.apikey.utils import APIKeyStatus
from core.db_session.transactional import Transactional, Propagation


class PaigApiKeyRepository(BaseOperations[PaigApiKeyModel]):
    """
        Repository class for handling database operations related to encryption key models.

        Inherits from BaseOperations[PaigApiKeyModel], providing generic CRUD operations.

        This class inherits all methods from BaseOperations[PaigApiKeyModel].
        """
    def __init__(self):
        """
        Initialize the ApiKeyRepository.
        """
        super().__init__(PaigApiKeyModel)

    async def create_api_key(self, api_key_params: dict):
        """
        Create a new API key.

        Args:
            api_key_params (dict): The parameters for the new API key.

        Returns:
            PaigApiKeyModel: The newly created API key.
        """
        model = self.model_class()
        model.set_attribute(api_key_params)
        session.add(model)
        await session.flush()
        return model

    async def get_api_key_by_ids(self, key_ids: list):
        """
        Retrieve API keys by their IDs.

        Args:
            key_ids (list): The IDs of the keys.

        Returns:
            List[PaigApiKeyModel]: The keys with the specified IDs.
        """
        try:
            return await self.get_all(filters={"id": key_ids, "key_status": APIKeyStatus.ACTIVE.value}, apply_in_list_filter=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "API Key", "keyIds", key_ids))

    async def get_api_keys_by_application_id(self, application_id, include_filters, page, size, sort, key_status):
        """
        Retrieve API keys by the ID of the application they belong to.

        Args:
            application_id (int): The ID of the application.
            include_filters (dict): The filters to apply to the API keys.
            page (int): The page number to retrieve.
            size (int): The number of items per page.
            sort (str): The sort options.
            key_status (list): The key status options.

        Returns:
            List[PaigApiKeyModel]: The API keys that belong to the specified application.
        """
        try:
            all_filters = list()
            skip = 0 if page is None else (page * size)
            query = select(PaigApiKeyModel)
            query = query.filter(PaigApiKeyModel.application_id == application_id)
            query = self.create_filter(query, include_filters)
            if key_status:
                all_filters.append(PaigApiKeyModel.key_status.in_(key_status))

            if all_filters:
                query = query.filter(and_(*all_filters))

            if sort:
                if not isinstance(sort, list):
                    sort = [sort]
                for sort_option in sort:
                    column_name, sort_type = self.parse_sort_option(sort_option)
                    alias_names = column_name.split(",")
                    field_names = []
                    for alias_name in alias_names:
                        field_names.append(get_field_name_by_alias(model=PaigApiKeyView, alias=alias_name))
                    sort_column_name = ",".join(field_names)
                    query = self.order_by(query, sort_column_name, sort_type)

            query = query.limit(size).offset(skip)
            results = (await session.execute(query)).scalars().all()
            count = (await self.get_count_with_filter(include_filters))
            return results, count


        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "API Key", "applicationId", application_id))

    async def disable_api_key(self, key_id: int):
        """
        Delete an API key by its ID.

        Args:
            key_id (int): The ID of the key to delete.

        Returns:
            None
        """
        try:
            api_key = await self.get_by(filters={"id": key_id}, unique=True)
            api_key.set_attribute({"key_status": APIKeyStatus.DISABLED.value})
            return api_key
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "API Key", "keyId", key_id))

    async def permanent_delete_api_key(self, key_id: int):
        """
        Delete an API key by its ID.

        Args:
            key_id (int): The ID of the key to delete.

        Returns:
            None
        """
        try:
            api_key = await self.get_by(filters={"id": key_id}, unique=True)
            await self.delete(api_key)
            return "API Key deleted successfully"
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "API Key", "keyId", key_id))


    async def get_paig_api_key_by_uuid(self, key_uuid: str):
        """
        Retrieve an API key by its UUID.

        Args:
            key_uuid (str): The UUID of the key.

        Returns:
            PaigApiKeyModel: The API key with the specified UUID.

        Raises:
            NoResultFound: If no API key with the specified UUID is found.
        """
        try:
            return await self.get_by(filters={"key_id": key_uuid, "key_status": APIKeyStatus.ACTIVE.value}, unique=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "API Key", "keyUuid", key_uuid))