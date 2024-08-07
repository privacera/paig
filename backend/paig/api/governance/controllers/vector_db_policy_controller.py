from typing import List

from api.user.utils.acc_service_validation_util import AccServiceValidationUtil
from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.vector_db_policy import VectorDBPolicyFilter, VectorDBPolicyView
from api.governance.services.vector_db_policy_service import VectorDBPolicyService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends


class VectorDBPolicyController:

    def __init__(self,
                 vector_db_policy_service: VectorDBPolicyService = SingletonDepends(VectorDBPolicyService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil),
                 acc_service_validation_util: AccServiceValidationUtil = SingletonDepends(AccServiceValidationUtil)):
        self.vector_db_policy_service = vector_db_policy_service
        self.gov_service_validation_util = gov_service_validation_util
        self.acc_service_validation_util = acc_service_validation_util

    async def list_vector_db_policies(self, vector_db_policy_filter: VectorDBPolicyFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Vector DB Policies.

        Args:
            vector_db_policy_filter (VectorDBPolicyFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Vector DB view objects and metadata.
        """
        return await self.vector_db_policy_service.list_vector_db_policies(vector_db_policy_filter, page_number, size, sort)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_vector_db_policies(self, vector_db_id: int, request: VectorDBPolicyView) -> VectorDBPolicyView:
        """
        Create a new Vector DB Policy.

        Args:
            vector_db_id (int): The ID of the Vector DB to associate with the policy.
            request (VectorDBPolicyView): The view object representing the Vector DB Policy to create.

        Returns:
            VectorDBPolicyView: The created Vector DB Policy view object.
        """
        # await self.gov_service_validation_util.validate_metadata_exists(request)
        await self.validate_users(request)
        await self.validate_groups(request)
        return await self.vector_db_policy_service.create_vector_db_policy(vector_db_id, request)

    async def get_vector_db_policy_by_id(self, vector_db_id: int, id: int) -> VectorDBPolicyView:
        """
        Retrieve a Vector DB by Policy its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB Policy to retrieve.

        Returns:
            VectorDBPolicyView: The Vector DB Policy view object corresponding to the ID.
        """
        return await self.vector_db_policy_service.get_vector_db_policy_by_id(vector_db_id, id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_vector_db_policy(self, vector_db_id: int, id: int):
        """
        Delete a Vector DB Policy by its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB Policy to delete.
        """
        await self.vector_db_policy_service.delete_vector_db_policy(vector_db_id, id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_vector_db_policy(self, vector_db_id: int, id: int, request: VectorDBPolicyView) -> VectorDBPolicyView:
        """
        Update a Vector DB Policy identified by its ID.

        Args:
            vector_db_id (int): The ID of the Vector DB.
            id (int): The ID of the Vector DB Policy to update.
            request (VectorDBPolicyView): The updated view object representing the Vector DB Policy.

        Returns:
            VectorDBPolicyView: The updated Vector DB Policy view object.
        """
        # Skipping validation for metadata exists as it is not required
        # await self.gov_service_validation_util.validate_metadata_exists(request)
        await self.validate_users(request)
        await self.validate_groups(request)
        return await self.vector_db_policy_service.update_vector_db_policy(vector_db_id, id, request)

    async def validate_users(self, request):
        users = request.allowed_users.copy()
        users.extend(request.denied_users.copy())
        await self.acc_service_validation_util.validate_users_exists(users)

    async def validate_groups(self, request):
        groups = request.allowed_groups.copy()
        groups.extend(request.denied_groups.copy())
        await self.acc_service_validation_util.validate_groups_exists(groups)
