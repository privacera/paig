from typing import Dict


class AuthzServiceResponse:
    """
    A class to represent a response from the authorization service.
    """

    def __init__(self, res_data: Dict):
        """
        Initializes an instance of AuthzServiceResponse.

        Args:
            res_data (Dict): The response data from the authorization service.
        """
        self.authorized = res_data.get("authorized")
        self.enforce = res_data.get("enforce")
        self.request_id = res_data.get("requestId")
        self.audit_id = res_data.get("auditId")
        self.application_name = res_data.get("applicationName")
        self.masked_traits = res_data.get("maskedTraits")
        self.context = res_data.get("context")
        self.ranger_audit_ids = res_data.get("rangerAuditIds")
        self.ranger_policy_ids = res_data.get("rangerPolicyIds")
        self.paig_policy_ids = res_data.get("paigPolicyIds")
        self.status_code = res_data.get("statusCode")
        self.status_message = res_data.get("statusMessage")
        self.user_id = res_data.get("userId")
