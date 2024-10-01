from typing import Set, Dict, List, Optional

from paig_authorizer_core.constants import PermissionType
from paig_authorizer_core.models.request_models import AuthzRequest
from paig_authorizer_core.models.data_models import AIApplicationConfigData
from paig_authorizer_core.models.data_models import AIApplicationPolicyData


def check_explicit_application_access(request: AuthzRequest, app_config: AIApplicationConfigData,
                                      user_groups: List[str], accessType: str) -> bool:
    """
    Checks if the request is explicitly allowed or denied based on application configuration.

    Args:
        request (AuthzRequest): The authorization request object.
        app_config (AIApplicationConfigData): The application configuration object.
        user_groups (List[str]): The user groups associated with the request.
        accessType (str): The access type to check for (allowed or denied).

    Returns:
        bool: True if the request is explicitly allowed or denied, False otherwise.
    """
    if accessType == "allowed":
        return app_config.allowed_users and request.user_id in app_config.allowed_users or \
            app_config.allowed_groups and any(group in app_config.allowed_groups for group in user_groups)
    elif accessType == "denied":
        return app_config.denied_users and request.user_id in app_config.denied_users or \
            app_config.denied_groups and any(group in app_config.denied_groups for group in user_groups)
    return False


def find_first_deny_policy(application_policies: List[AIApplicationPolicyData], request: AuthzRequest) -> \
        Optional[AIApplicationPolicyData]:
    """
    Finds the first policy that denies the request type in the list of application policies.

    Args:
        application_policies (List[AIApplicationPolicyData]): The list of application policies.
        request (AuthzRequest): The authorization request object.

    Returns:
        Optional[AIApplicationPolicyData]: The first policy that denies the request type,
                                           or None if no such policy is found.
    """
    return next(
        (policy for policy in application_policies if getattr(policy, request.request_type) == PermissionType.DENY),
        None)


def get_authorization_and_masked_traits(application_policies: List[AIApplicationPolicyData],
                                        request: AuthzRequest) \
        -> tuple[bool, Dict[str, str], Set[int]]:
    """
    Authorizes a request based on application policies and redacts traits if necessary.

    Args:
        application_policies (List[AIApplicationPolicyData]): The list of application policies.
        request (AuthzRequest): The authorization request object.

    Returns:
        tuple[bool, Dict[str, str]]: A tuple containing:
                                     - bool: True if the request is authorized, False otherwise.
                                     - Dict[str, str]: A dictionary mapping redacted traits to masked values.
                                     - Set[int]: A set of policy IDs for audit purposes.
    """
    authorized = True
    masked_traits = {}
    redact_policies = [policy for policy in application_policies if
                       getattr(policy, request.request_type) == PermissionType.REDACT]
    redacted_traits = set()
    audit_policy_ids_set: Set[int] = set()

    # Find redacted traits and mask them
    for trait in request.traits:
        for policy in redact_policies:
            if trait in policy.tags:
                redacted_traits.add(trait)
                audit_policy_ids_set.add(policy.id)
                break

    for trait in redacted_traits:
        masked_traits[trait] = f"<<{trait}>>"

    # Find first policy ID for allowed traits
    allowed_traits = set(request.traits) - redacted_traits
    for trait in allowed_traits:
        for policy in application_policies:
            if trait in policy.tags:
                audit_policy_ids_set.add(policy.id)
                break

    return authorized, masked_traits, audit_policy_ids_set
