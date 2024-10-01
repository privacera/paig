from typing import List, Optional, Dict
from paig_authorizer_core.models.data_models import VectorDBPolicyData


class MetadataFilterCriteria:
    """
    Represents criteria for filtering metadata.

    Args:
        metadata_key (str): The key of the metadata to filter.
        metadata_value (str): The value of the metadata to filter.
        operator_value (str): The operator to use for filtering.
    """

    def __init__(self, metadata_key: str, metadata_value: str, operator_value: str):
        """
        Initializes a MetadataFilterCriteria instance.

        Args:
            metadata_key (str): The key of the metadata to filter.
            metadata_value (str): The value of the metadata to filter.
            operator_value (str): The operator to use for filtering.
        """
        self.metadata_key = metadata_key
        self.metadata_value = metadata_value
        self.operator_value = operator_value


class BaseMetadataFilterCriteriaCreator:
    """
    Creates metadata filter criteria based on policies and user information.
    """

    # noinspection PyMethodMayBeStatic
    def prepare_operator(self, operator: str) -> str:
        """
        Prepares the operator for filtering.

        Args:
            operator (str): The input operator.

        Returns:
            str: The corresponding operator for filtering.
        """
        return {
            "ne": "!=",
        }.get(operator, "==")

    # noinspection PyMethodMayBeStatic
    def reverse_operator(self, operator: str) -> str:
        """
        Reverses the operator for filtering.

        Args:
            operator (str): The input operator.

        Returns:
            str: The corresponding reversed operator for filtering.
        """
        return {
            "ne": "eq",
        }.get(operator, "ne")

    def create_metadata_filters(self, policies: List[VectorDBPolicyData], request_user: str,
                                request_groups: List[str]) -> Dict[str, List[MetadataFilterCriteria]]:
        """
        Creates a list of MetadataFilterCriteria based on the given policies and user information.

        Args:
            policies (List[VectorDBPolicyView]): The list of policies.
            request_user (str): The user making the request.
            request_groups (List[str]): The groups the user belongs to.

        Returns:
            List[MetadataFilterCriteria]: The list of created MetadataFilterCriteria.
        """
        metadata_wise_filters: Dict[str, List[MetadataFilterCriteria]] = {}
        filters: List[MetadataFilterCriteria] = []

        sorted_policies = sorted(policies, key=lambda x: (x.metadata_key.lower(), x.metadata_value.lower()))

        for policy in sorted_policies:
            allowed_filter = self.get_metadata_filter(policy, True, request_user, request_groups)
            if allowed_filter:
                filters.append(allowed_filter)

            if not allowed_filter:
                denied_filter = self.get_metadata_filter(policy, False, request_user, request_groups)
                if denied_filter:
                    filters.append(denied_filter)

        for filter_item in filters:
            if metadata_wise_filters.get(filter_item.metadata_key):
                metadata_wise_filters[filter_item.metadata_key].append(filter_item)
            else:
                metadata_wise_filters[filter_item.metadata_key] = [filter_item]

        return metadata_wise_filters

    def get_metadata_filter(self, policy: VectorDBPolicyData, is_allowed: bool, request_user: str,
                            request_groups: List[str]) -> Optional[MetadataFilterCriteria]:
        """
        Gets a MetadataFilterCriteria based on a policy, user information, and whether the filter is for allowed or
        denied access.

        Args:
            policy (VectorDBPolicyView): The policy.
            is_allowed (bool): Whether the filter is for allowed access.
            request_user (str): The user making the request.
            request_groups (List[str]): The groups the user belongs to.

        Returns:
            Optional[MetadataFilterCriteria]: The created MetadataFilterCriteria or None if no filter is created.
        """
        users = policy.allowed_users if is_allowed else policy.denied_users
        groups = policy.allowed_groups if is_allowed else policy.denied_groups

        if users and request_user in users or groups and any(group in groups for group in request_groups):
            operator = policy.operator if is_allowed else self.reverse_operator(policy.operator)
            updated_operator = self.prepare_operator(operator)
            metadata_value = self.prepare_metadata_value(policy.metadata_value)

            return MetadataFilterCriteria(policy.metadata_key, metadata_value, updated_operator)

        return None

    def prepare_metadata_value(self, metadata_value: str) -> str:
        """
        Prepares the metadata value for filtering.

        Args:
            metadata_value (str): The metadata value.

        Returns:
            str: The prepared metadata value.
        """
        if self.is_integer(metadata_value) or self.is_float(metadata_value):
            return metadata_value
        elif self.is_boolean(metadata_value):
            return metadata_value.upper()
        else:
            return f"'{metadata_value}'"

    # noinspection PyMethodMayBeStatic
    def is_integer(self, value: str) -> bool:
        """
        Checks if the given value is an integer.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if the value is an integer, False otherwise.
        """
        try:
            int(value)
            return True
        except ValueError:
            return False

    # noinspection PyMethodMayBeStatic
    def is_float(self, value: str) -> bool:
        """
        Checks if the given value is a float.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if the value is a float, False otherwise.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    # noinspection PyMethodMayBeStatic
    def is_boolean(self, value: str) -> bool:
        """
        Checks if the given value is a boolean.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if the value is a boolean, False otherwise.
        """
        return value.lower() in ["true", "false"]
