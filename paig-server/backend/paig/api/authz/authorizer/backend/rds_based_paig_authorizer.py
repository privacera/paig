from typing import List

from api.authz.utils.config import get_rds_authorizer_cache_expiry_time
from api.user.api_schemas.user_schema import GetUsersFilterRequest
from api.user.services.user_service import UserService
from api.authz.authorizer.base_paig_authorizer import BasePAIGAuthorizer
from api.authz.utils.constants import KEY_APPLICATION_ID
from api.authz.utils.cache_decorator import cache_with_expiration
from core.controllers.paginated_response import Pageable
from core.exceptions import NotFoundException
from api.governance.api_schemas.ai_app import AIApplicationView
from api.governance.api_schemas.ai_app_config import AIApplicationConfigView
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView
from api.governance.api_schemas.vector_db import VectorDBView
from api.governance.api_schemas.vector_db_policy import VectorDBPolicyView
from api.governance.services.ai_app_config_service import AIAppConfigService
from api.governance.services.ai_app_policy_service import AIAppPolicyService
from api.governance.services.ai_app_service import AIAppService
from api.governance.services.vector_db_policy_service import VectorDBPolicyService
from api.governance.services.vector_db_service import VectorDBService
from core.utils import SingletonDepends


class RDSBasedPaigAuthorizer(BasePAIGAuthorizer):
    """
    RDS-based Authorizer class for PAIG.

    Args:
        user_service (UserService): The controller handling user operations.
        ai_app_service (AIAppService): The service handling AI application operations.
        ai_app_config_service (AIAppConfigService): The service handling AI application configuration operations.
        ai_app_policy_service (AIAppPolicyService): The service handling AI application policy operations.
        vector_db_service (VectorDBService): The service handling vector database operations.
        vector_db_policy_service (VectorDBPolicyService): The service handling vector database policy operations.
    """

    def __init__(self, user_service: UserService = SingletonDepends(UserService),
                 ai_app_service: AIAppService = SingletonDepends(AIAppService),
                 ai_app_config_service: AIAppConfigService = SingletonDepends(AIAppConfigService),
                 ai_app_policy_service: AIAppPolicyService = SingletonDepends(AIAppPolicyService),
                 vector_db_service: VectorDBService = SingletonDepends(VectorDBService),
                 vector_db_policy_service: VectorDBPolicyService = SingletonDepends(VectorDBPolicyService)):
        self.user_service = user_service
        self.ai_app_service = ai_app_service
        self.ai_app_config_service = ai_app_config_service
        self.ai_app_policy_service = ai_app_policy_service
        self.vector_db_service = vector_db_service
        self.vector_db_policy_service = vector_db_policy_service

    @cache_with_expiration(get_rds_authorizer_cache_expiry_time("get_user_groups"))
    async def get_user_groups(self, user: str) -> List[str]:
        """
        Get the groups of a user.

        Args:
            user (str): The username of the user.

        Returns:
            List[str]: The list of groups the user belongs to.
        """
        groups = []
        try:
            get_user_filter: GetUsersFilterRequest = GetUsersFilterRequest(username=user, exact_match=True)
            users_list: Pageable = await self.user_service.get_users_with_groups(
                search_filters=get_user_filter,
                page=0,
                size=1,
                sort=[]
            )
            if users_list.totalElements > 0:
                groups = users_list.content[0].get("groups", [])
        except NotFoundException:
            # If the user is not found, return an empty list of groups.
            pass
        return groups

    @cache_with_expiration(get_rds_authorizer_cache_expiry_time("get_application_details"))
    async def get_application_details(self, application_key: str, **kwargs) -> AIApplicationView:
        """
        Get the details of an AI application.

        Args:
            application_key (str): The key of the AI application.
            **kwargs: Additional keyword arguments.

        Returns:
            AIApplicationView: The view of the AI application
        """
        return await self.ai_app_service.get_ai_application_by_application_key(application_key=application_key)

    @cache_with_expiration(get_rds_authorizer_cache_expiry_time("get_application_config"))
    async def get_application_config(self, application_key: str, **kwargs) -> AIApplicationConfigView:
        """
        Get the configuration of an AI application.

        Args:
            application_key (str): The key of the AI application.

        Returns:
            AIApplicationConfigView: The configuration of the AI application.
        """
        app_id = kwargs.get(KEY_APPLICATION_ID)
        return await self.ai_app_config_service.get_ai_app_config(application_id=app_id)

    @cache_with_expiration(get_rds_authorizer_cache_expiry_time("get_application_policies"))
    async def get_application_policies(self, application_key: str, traits: List[str], user: str, groups: List[str],
                                       request_type: str, **kwargs) -> List[AIApplicationPolicyView]:
        """
        Get the policies of an AI application.

        Args:
            application_key (str): The key of the AI application.
            traits (List[str]): The list of traits to check.
            user (str): The username of the user.
            groups (List[str]): The list of groups the user belongs to.
            request_type (str): The type of request.
            **kwargs: Additional keyword arguments.

        Returns:
            List[AIApplicationPolicyView]: The list of AI application policies.
        """
        app_id = kwargs.get(KEY_APPLICATION_ID)
        return await self.ai_app_policy_service.list_ai_application_authorization_policies(app_id=app_id, traits=traits,
                                                                                           user=user, groups=groups)

    @cache_with_expiration(get_rds_authorizer_cache_expiry_time("get_vector_db_details"))
    async def get_vector_db_details(self, vector_db_name: str, **kwargs) -> VectorDBView:
        """
        Get the details of a vector database.

        Args:
            vector_db_name (str): The name of the vector database.
            **kwargs: Additional keyword arguments.

        Returns:
            VectorDBView: The view of the vector database.
        """
        return await self.vector_db_service.get_vector_db_by_name(name=vector_db_name)

    @cache_with_expiration(get_rds_authorizer_cache_expiry_time("get_vector_db_policies"))
    async def get_vector_db_policies(self, vector_db_id: int, user: str, groups: List[str], **kwargs) \
            -> List[VectorDBPolicyView]:
        """
        Get the policies of a vector database.

        Args:
            vector_db_id (int): The ID of the vector database.
            user (str): The username of the user.
            groups (List[str]): The list of groups the user belongs to.
            **kwargs: Additional keyword arguments.

        Returns:
            List[VectorDBPolicyView]: The list of vector database policies.
        """
        return await self.vector_db_policy_service.list_vector_db_authorization_policies(vector_db_id=vector_db_id,
                                                                                         user=user, groups=groups)
