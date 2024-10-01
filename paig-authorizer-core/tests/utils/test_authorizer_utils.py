import pytest

from paig_authorizer_core.constants import PermissionType
from paig_authorizer_core.models.request_models import AuthzRequest
from paig_authorizer_core.utils.authorizer_utils import check_explicit_application_access, find_first_deny_policy, \
    get_authorization_and_masked_traits
from paig_authorizer_core.models.data_models import AIApplicationConfigData
from paig_authorizer_core.models.data_models import AIApplicationPolicyData


@pytest.fixture
def authz_request():
    return AuthzRequest(
        request_id="1234",
        request_date_time="2024-07-10T10:00:00Z",
        user_id="test_user",
        context={"key": "value"},
        traits=["trait1", "trait2"],
        request_type="prompt"
    )


@pytest.fixture
def app_config():
    return AIApplicationConfigData(
        allowed_users={"test_user"},
        allowed_groups={"group1"},
        denied_users={"denied_user"},
        denied_groups={"denied_group"}
    )


@pytest.fixture
def app_policies():
    return [
        AIApplicationPolicyData(
            id=1,
            tags=["trait1"],
            description="Policy 1",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.ALLOW,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        ),
        AIApplicationPolicyData(
            id=2,
            read=PermissionType.DENY,
            tags=["trait2"],
            description="Policy 2",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.DENY,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        ),
        AIApplicationPolicyData(
            id=3,
            read=PermissionType.REDACT,
            tags=["trait2"],
            description="Policy 3",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.REDACT,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        )
    ]


def test_allowed_access_for_user(authz_request, app_config):
    authz_request.user_id = "test_user"
    user_groups = ["some_other_group"]
    access_type = "allowed"

    result = check_explicit_application_access(authz_request, app_config, user_groups, access_type)
    assert result is True


def test_denied_access_for_user(authz_request, app_config):
    authz_request.user_id = "denied_user"
    user_groups = ["some_other_group"]
    access_type = "denied"

    result = check_explicit_application_access(authz_request, app_config, user_groups, access_type)
    assert result is True


def test_allowed_access_for_group(authz_request, app_config):
    authz_request.user_id = "some_other_user"
    user_groups = ["group1"]
    access_type = "allowed"

    result = check_explicit_application_access(authz_request, app_config, user_groups, access_type)

    assert result is True


def test_denied_access_for_group(authz_request, app_config):
    authz_request.user_id = "some_other_user"
    user_groups = ["denied_group"]
    access_type = "denied"

    result = check_explicit_application_access(authz_request, app_config, user_groups, access_type)

    assert result is True


def test_allowed_access_for_invalid_user_and_group(authz_request, app_config):
    authz_request.user_id = "some_other_user"
    user_groups = ["some_other_group"]
    access_type = "allowed"

    result = check_explicit_application_access(authz_request, app_config, user_groups, access_type)

    assert result is False


def test_denied_access_denied_for_invalid_user_and_group(authz_request, app_config):
    authz_request.user_id = "some_other_user"
    user_groups = ["some_other_group"]
    access_type = "denied"

    result = check_explicit_application_access(authz_request, app_config, user_groups, access_type)

    assert result is False


def test_find_first_deny_policy(authz_request, app_policies):
    authz_request.request_type = "prompt"
    result = find_first_deny_policy(app_policies, authz_request)

    assert result is not None
    assert result.id == 2


def test_find_first_deny_policy_none(authz_request):
    app_policies = [
        AIApplicationPolicyData(
            id=1,
            tags=["trait1"],
            description="Policy 1",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.ALLOW,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        )
    ]

    authz_request.request_type = "prompt"
    result = find_first_deny_policy(app_policies, authz_request)

    assert result is None


def test_get_authorization_and_masked_traits(authz_request, app_policies):
    authz_request.request_type = "prompt"
    authorized, masked_traits, audit_policy_ids_set = get_authorization_and_masked_traits(app_policies, authz_request)

    assert authorized is True
    assert masked_traits == {"trait2": "<<trait2>>"}
    assert audit_policy_ids_set == {1, 3}


def test_get_authorization_and_masked_traits_no_redactions(authz_request):
    app_policies = [
        AIApplicationPolicyData(
            id=1,
            tags=["trait1"],
            description="Policy 1",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.ALLOW,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        )
    ]

    authz_request.request_type = "prompt"
    authorized, masked_traits, audit_policy_ids_set = get_authorization_and_masked_traits(app_policies, authz_request)

    assert authorized is True
    assert masked_traits == {}
    assert audit_policy_ids_set == {1}
