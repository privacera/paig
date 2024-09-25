from typing import Dict, List, Optional

from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.models.data_models import VectorDBPolicyData


def create_authorize_response(request: AuthzRequest, application_name: str, authorized: bool,
                              masked_traits: Dict[str, str], paig_policy_ids: List[int],
                              reason: str = None) -> AuthzResponse:
    """
    Create an authorization response.

    Args:
        request (AuthzRequest): The authorization request.
        application_name (str): The name of the application.
        authorized (bool): Whether the request is authorized.
        masked_traits (Dict[str, str]): The masked traits.
        paig_policy_ids (List[int]): The PAIG policy IDs.
        reason (str): The reason for the authorization result.

    Returns:
        AuthzResponse: The authorization response.
    """
    status_code: int = 200 if authorized else 403
    status_message: str = "Access is allowed" if authorized else "Access is denied"
    response = AuthzResponse()
    response.authorized = authorized
    response.enforce = True
    response.request_id = request.request_id
    response.request_date_time = request.request_date_time
    response.user_id = request.user_id
    response.application_name = application_name
    response.masked_traits = masked_traits
    response.context = request.context
    response.status_code = status_code
    response.status_message = status_message
    response.reason = reason
    response.paig_policy_ids = paig_policy_ids
    return response


def create_authorize_vector_db_response(request: VectorDBAuthzRequest, vector_db: Optional[VectorDBData],
                                        policies: List[VectorDBPolicyData], filter_expression: str, reason: str = None)\
        -> VectorDBAuthzResponse:
    response = VectorDBAuthzResponse()

    if policies:
        response.vector_db_policy_info = [{"id": policy.id, "version": ""} for policy in policies]

    if vector_db:
        response.vector_db_id = vector_db.id
        response.vector_db_name = vector_db.name
        response.vector_db_type = vector_db.type.name if hasattr(vector_db.type, "name") else vector_db.type
        response.user_enforcement = vector_db.user_enforcement
        response.group_enforcement = vector_db.group_enforcement

    response.filter_expression = filter_expression

    response.reason = reason

    return response
