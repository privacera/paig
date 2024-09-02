from typing import List
from sqlalchemy import or_, and_
from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel


class AIAppPolicyRepository(BaseOperations[AIApplicationPolicyModel]):
    """
    Repository class for handling database operations related to AI application policy models.

    Inherits from BaseOperations[AIApplicationPolicyModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[AIApplicationPolicyModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(AIApplicationPolicyModel)

    async def list_policies_for_authorization(self, application_id: int, traits: List[str], user: str,
                                              groups: List[str]) -> List[AIApplicationPolicyModel]:
        # Get column attribute for the model
        column_application_id = getattr(self.model_class, "application_id")
        column_status = getattr(self.model_class, "status")
        column_traits = getattr(self.model_class, "tags")
        column_users = getattr(self.model_class, "users")
        column_groups = getattr(self.model_class, "groups")

        query = await self._query()

        query_filters = []
        query_filters.append(column_application_id == application_id)
        query_filters.append(column_status == 1)

        # Create a filter for traits (comma-separated values)
        traits_filter = or_(*[column_traits.like(f'%{trait}%') for trait in traits])
        query_filters.append(traits_filter)

        # Create a filter for users and groups (comma-separated values)
        user_filter = column_users.like(f'%{user}%')
        groups_filter = or_(*[column_groups.like(f'%{group}%') for group in groups])
        user_group_filter = or_(user_filter, groups_filter)
        query_filters.append(user_group_filter)

        query = query.filter(and_(*query_filters))

        return await self._all(query)