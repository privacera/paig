from typing import List

from api.user.utils.acc_service_validation_util import AccServiceValidationUtil
from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView, AIApplicationPolicyFilter
from api.governance.services.ai_app_policy_service import AIAppPolicyService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends


class AIAppAPIKeyController:
    """
        Controller class specifically for handling AI application policies.

        Args:
            ai_app_policy_service (AIAppPolicyService): The service class for AI application policies.
        """

    def __init__(self,
                 ai_app_policy_service: AIAppPolicyService = SingletonDepends(AIAppPolicyService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil),
                 acc_service_validation_util: AccServiceValidationUtil = SingletonDepends(AccServiceValidationUtil)):
        self.ai_app_policy_service = ai_app_policy_service
        self.gov_service_validation_util = gov_service_validation_util
        self.acc_service_validation_util = acc_service_validation_util


    def generate_api_key(self):
        pass