from sqlalchemy import or_, and_
from core.factory.database_initiator import BaseOperations
from api.governance.database.db_models.vector_db_policy_model import VectorDBPolicyModel


class VectorDBPolicyRepository(BaseOperations[VectorDBPolicyModel]):
    """
    Repository class for handling database operations related to Vector DB models.

    Inherits from BaseOperations[VectorDBModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[VectorDBModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(VectorDBPolicyModel)

    async def list_policies_for_authorization(self, vector_db_id: int, user: str,
                                              groups: list[str]) -> list[VectorDBPolicyModel]:
        # Get column attribute for the model
        column_vector_db_id = getattr(self.model_class, "vector_db_id")
        column_status = getattr(self.model_class, "status")
        column_allowed_users = getattr(self.model_class, "allowed_users")
        column_denied_users = getattr(self.model_class, "denied_users")
        column_allowed_groups = getattr(self.model_class, "allowed_groups")
        column_denied_groups = getattr(self.model_class, "denied_groups")

        query = await self._query()

        query_filters = []
        query_filters.append(column_vector_db_id == vector_db_id)
        query_filters.append(column_status == 1)

        # Create a filter for users
        user_filter = or_(column_allowed_users.like(f'%{user}%'), column_denied_users.like(f'%{user}%'))

        # Create a filter for groups
        groups_allowed_filter = or_(*[column_allowed_groups.like(f'%{group}%') for group in groups])
        groups_denied_filter = or_(*[column_denied_groups.like(f'%{group}%') for group in groups])
        groups_filter = or_(groups_allowed_filter, groups_denied_filter)

        user_groups_filter = or_(user_filter, groups_filter)
        query_filters.append(user_groups_filter)

        query = query.filter(and_(*query_filters))

        return await self._all(query)
