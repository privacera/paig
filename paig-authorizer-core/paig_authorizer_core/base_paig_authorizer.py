from abc import abstractmethod, ABC
from typing import Dict, List

from paig_authorizer_core.paig_authorizer import PAIGAuthorizer
from paig_authorizer_core.constants import VectorDBType, GROUP_PUBLIC
from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria, \
    BaseMetadataFilterCriteriaCreator
from paig_authorizer_core.filter.base_vector_db_filter_creator import BaseVectorDBFilterCreator
from paig_authorizer_core.filter.milvus_filter_creator import MilvusFilterCreator
from paig_authorizer_core.filter.opensearch_filter_creator import OpenSearchFilterCreator
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from paig_authorizer_core.utils.authorizer_response_utils import create_authorize_response, \
    create_authorize_vector_db_response
from paig_authorizer_core.utils.authorizer_utils import get_authorization_and_masked_traits, \
    find_first_deny_policy, \
    check_explicit_application_access
from paig_authorizer_core.models.data_models import AIApplicationData
from paig_authorizer_core.models.data_models import AIApplicationConfigData
from paig_authorizer_core.models.data_models import AIApplicationPolicyData
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.models.data_models import VectorDBPolicyData


class BasePAIGAuthorizer(PAIGAuthorizer, ABC):

    @abstractmethod
    def get_user_id_by_email(self, email: str) -> str | None:
        """
        Retrieves the user ID by email.

        Args:
            email (str): The email of the user.

        Returns:
            str: The user ID.
        """
        pass

    @abstractmethod
    def get_user_groups(self, user: str) -> List[str]:
        """
        Retrieves the groups associated with a user.

        Args:
            user (str): The user ID.

        Returns:
            List[str]: The list of groups the user belongs to.
        """
        pass

    @abstractmethod
    def get_application_details(self, application_key: str, **kwargs) -> AIApplicationData:
        """
        Retrieves the details of an AI application.

        Args:
            application_key (str): The key of the AI application.
            **kwargs: Additional keyword arguments.

        Returns:
            AIApplicationData: The view of the AI application.
        """
        pass

    @abstractmethod
    def get_application_config(self, application_key: str, **kwargs) -> AIApplicationConfigData:
        """
        Retrieves the configuration of an AI application.

        Args:
            application_key (str): The key of the AI application.
            **kwargs: Additional keyword arguments.

        Returns:
            AIApplicationConfigData: The configuration of the AI application.
        """
        pass

    @abstractmethod
    def get_application_policies(self, application_key: str, traits: List[str], user: str, groups: List[str],
                                       request_type: str, **kwargs) -> List[AIApplicationPolicyData]:
        """
        Retrieves the policies of an AI application.

        Args:
            application_key (str): The key of the AI application.
            traits (List[str]): The list of traits to check.
            user (str): The username of the user.
            groups (List[str]): The list of groups the user belongs to.
            request_type (str): The type of request.
            **kwargs: Additional keyword arguments.

        Returns:
            List[AIApplicationPolicyData]: The list of AI application policies.
        """
        pass

    @abstractmethod
    def get_vector_db_details(self, vector_db_id: int, **kwargs) -> VectorDBData:
        """
        Retrieves the details of a vector database.

        Args:
            vector_db_id (int): The ID of the vector database.
            **kwargs: Additional keyword arguments.

        Returns:
            VectorDBData: The view of the vector database.
        """
        pass

    @abstractmethod
    def get_vector_db_policies(self, vector_db_id: int, user: str, groups: List[str], **kwargs) \
            -> List[VectorDBPolicyData]:
        """
        Retrieves the policies of a vector database.

        Args:
            vector_db_id (int): The ID of the vector database.
            user (str): The username of the user.
            groups (List[str]): The list of groups the user belongs to.
            **kwargs: Additional keyword arguments.

        Returns:
            List[VectorDBPolicyData]: The list of vector database policies.
        """
        pass

    def enrich_authorization_request(self, request: AuthzRequest | VectorDBAuthzRequest) \
            -> AuthzRequest | VectorDBAuthzRequest:
        """
        Enriches the authorization request with additional details.

        Args:
            request (AuthzRequest | VectorDBAuthzRequest): The authorization request.

        Returns:
            AuthzRequest | VectorDBAuthzRequest: The enriched authorization request.
        """
        # First check if user provided is email or not
        user_id = request.user_id
        if "@" in user_id:
            user_id_from_email = self.get_user_id_by_email(user_id.lower())
            if not user_id_from_email:
                user_id_from_email = user_id.split("@")[0]
            return request.model_copy(update={'user_id': user_id_from_email}, deep=True)

        return request

    def authorize(self, authz_request: AuthzRequest) -> AuthzResponse:
        """
        Authorizes a request based on user groups, application details, policies, and configurations.

        Args: authz_request (AuthzRequest): The authorization request object containing user details, application key,
        traits, and request type.

        Returns:
            AuthzResponse: The authorization response object indicating whether the request is authorized,
                          masked traits, and audit policy IDs.
        """
        # Enrich the authorization request
        request = self.enrich_authorization_request(authz_request)

        # Step 1: Retrieve application details and configuration
        app_details: AIApplicationData = self.get_application_details(request.application_key)
        application_id = app_details.id

        # Initialize variables for response construction
        application_name = app_details.name
        authorized = False
        masked_traits = {}
        audit_policy_ids_set = set()

        if app_details.status == 0:
            # Application is disabled
            return create_authorize_response(request, application_name, authorized, masked_traits,
                                             list(audit_policy_ids_set), reason="Application is disabled")

        if (not request.traits) or len(request.traits) == 0:
            # No traits provided, default to unauthorized
            return create_authorize_response(request, application_name, True, masked_traits,
                                             list(audit_policy_ids_set), reason="No traits provided")

        # Retrieve application configuration
        app_config: AIApplicationConfigData = self.get_application_config(request.application_key,
                                                                                application_id=application_id)

        # Step 2: Retrieve user groups including 'public' if not already present
        user_groups = self.get_user_groups(request.user_id)
        if GROUP_PUBLIC not in user_groups:
            user_groups.append(GROUP_PUBLIC)

        # Step 3: Check for explicit deny in application config
        if check_explicit_application_access(request, app_config, user_groups, "denied"):
            audit_policy_ids_set.add(app_config.id)
            return create_authorize_response(request, application_name, authorized, masked_traits,
                                             list(audit_policy_ids_set), reason="Explicit deny access to Application")

        # Step 4: Check for explicit allow in application config
        explicit_application_access_allowed = check_explicit_application_access(
            request,
            app_config,
            user_groups,
            "allowed"
        )

        if not explicit_application_access_allowed:
            audit_policy_ids_set.add(app_config.id)
            return create_authorize_response(request, application_name, authorized, masked_traits,
                                             list(audit_policy_ids_set), reason="No Access to Application")

        # Step 4a: Retrieve application policies matching request traits, user, groups, and request type
        application_policies = self.get_application_policies(request.application_key, request.traits,
                                                                   request.user_id, user_groups,
                                                                   request.request_type,
                                                                   application_id=application_id)
        if application_policies:
            # Step 4b: Check if any explicit deny policy is present
            first_deny_policy = find_first_deny_policy(application_policies, request)
            if first_deny_policy:
                # Step 4c: Handle deny policy
                audit_policy_ids_set.add(first_deny_policy.id)
                return create_authorize_response(request, application_name, authorized, masked_traits,
                                                 list(audit_policy_ids_set))
            else:
                # Step 4d: Process allowed traits and redact policies
                authorized, masked_traits, policy_ids = get_authorization_and_masked_traits(application_policies,
                                                                                            request)
                audit_policy_ids_set.update(policy_ids)
                return create_authorize_response(request, application_name, authorized, masked_traits,
                                                 list(audit_policy_ids_set))
        else:
            # Step 4e: No matching policies, default to authorized with no masked traits
            authorized = True if explicit_application_access_allowed else False
            audit_policy_ids_set.add(app_config.id)
            return create_authorize_response(request, application_name, authorized, masked_traits,
                                             list(audit_policy_ids_set))

    def authorize_vector_db(self, authz_request: VectorDBAuthzRequest) -> VectorDBAuthzResponse:
        """
        Authorizes a request to access a vector DB based on user groups, application details, and policies.

        Args: authz_request (VectorDBAuthzRequest): The authorization request object containing user details and
        application key.

        Returns:
            VectorDBAuthzResponse: The authorization response object containing vector DB details and filter expression.
        """
        # Enrich the authorization request
        request = self.enrich_authorization_request(authz_request)

        # Step 1: Retrieve application details and configuration
        app_details: AIApplicationData = self.get_application_details(request.application_key)

        # Initialize variables for response construction
        vector_db = None
        policies = []
        filter_expression = ""

        # Step 2: Perform basic validations

        # Check if application is disabled
        if app_details.status == 0:
            # Application is disabled
            return create_authorize_vector_db_response(request, vector_db, policies, filter_expression,
                                                       reason="Application is disabled")

        # Check if vector DB is assigned to application
        vector_db_id = app_details.vector_db_id
        if not vector_db_id:
            # No vector db is assigned to application
            return create_authorize_vector_db_response(request, vector_db, policies, filter_expression,
                                                       reason="No Vector DB assigned to application")

        # Retrieve vector DB details
        vector_db = self.get_vector_db_details(vector_db_id)
        if vector_db.status == 0:
            # Vector DB is disabled
            return create_authorize_vector_db_response(request, vector_db, policies, filter_expression,
                                                       reason="Vector DB is disabled")

        # Step 3: Retrieve user groups including 'public' if not already present
        user_groups = self.get_user_groups(request.user_id)
        if GROUP_PUBLIC not in user_groups:
            user_groups.append(GROUP_PUBLIC)

        policies = self.get_vector_db_policies(vector_db_id, request.user_id, user_groups)

        # Step 4: Create filter expression based on metadata filters
        filter_criteria_creator: BaseMetadataFilterCriteriaCreator = BaseMetadataFilterCriteriaCreator()
        metadata_wise_filters: Dict[
            str, List[MetadataFilterCriteria]] = filter_criteria_creator.create_metadata_filters(policies,
                                                                                                 request.user_id,
                                                                                                 user_groups)
        filter_expression = self.create_vector_db_filter_expression(vector_db, request.user_id, user_groups,
                                                                    metadata_wise_filters)

        return create_authorize_vector_db_response(request, vector_db, policies, filter_expression)

    # noinspection PyMethodMayBeStatic
    def create_vector_db_filter_expression(self, vector_db: VectorDBData, user: str, groups: List[str],
                                           metadata_wise_filters: Dict[
                                               str, List[MetadataFilterCriteria]]) -> str | dict | None:
        """
        Creates a filter expression for a vector DB based on user groups, metadata filters, and policies.

        Args:
            vector_db (VectorDBData): The vector DB object.
            user (str): The user requesting the filter expression.
            groups (List[str]): The groups the user belongs to.
            metadata_wise_filters (Dict[str, List[MetadataFilterCriteria]]): The metadata filters to apply.

        Returns:
            str | dict | None: The filter expression.
        """
        filter_creator: BaseVectorDBFilterCreator | None = None
        if vector_db.type == VectorDBType.MILVUS:
            filter_creator = MilvusFilterCreator()
        elif vector_db.type == VectorDBType.OPENSEARCH:
            filter_creator = OpenSearchFilterCreator()

        if filter_creator:
            return filter_creator.create_filter_expression(vector_db, user, groups, metadata_wise_filters)

        return None

    def update_application_policies(self, application_id: int, application_key: str,
                                    application_policies: List[AIApplicationPolicyData]):
        """
        Updates the policies of an AI application.

        Args:
            application_id (int): The ID of the AI application.
            application_key (str): The key of the AI application.
            application_policies (List[AIApplicationPolicyData]): The list of AI application policies.
        """
        pass

    def update_user_group_mapping(self, user_group_mapping: Dict[str, List[str]]):
        """
        Updates the mapping of users to groups.

        Args:
            user_group_mapping (Dict[str, List[str]]): The mapping of users to groups.
        """
        pass
