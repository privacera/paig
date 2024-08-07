import json
from typing import List, Dict

from api.authz.authorizer.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from api.authz.authorizer.filter.base_vector_db_filter_creator import BaseVectorDBFilterCreator
from api.governance.api_schemas.vector_db import VectorDBView


class MilvusFilterCreator(BaseVectorDBFilterCreator):
    """
    Creates filter expressions for Milvus based on policies, user, and group information.
    """

    def create_filter_expression(self, vector_db: VectorDBView, user: str, groups: List[str],
                                 filters: Dict[str, List[MetadataFilterCriteria]]) -> str | dict | None:
        """
        Create a filter expression for a vector DB.

        Args:
            vector_db (VectorDBView): The vector DB object.
            user (str): The user requesting the filter expression.
            groups (List[str]): The groups the user belongs to.
            filters (Dict[str, List[MetadataFilterCriteria]]): The metadata filters to apply.

        Returns:
            str | dict: The filter expression.
        """
        final_expressions = []

        user_group_enforcement_expression = self.get_user_group_enforcement_expression(vector_db, user, groups)
        if user_group_enforcement_expression:
            final_expressions.append(user_group_enforcement_expression)

        metadata_filter_expression = self.get_metadata_filter_expressions(filters)
        if metadata_filter_expression:
            final_expressions.append(metadata_filter_expression)

        if final_expressions:
            if len(final_expressions) > 1:
                return f"{' && '.join(final_expressions)}"
            else:
                return final_expressions[0]
        else:
            return ""

    # noinspection PyMethodMayBeStatic
    def get_user_group_enforcement_expression(self, vector_db: VectorDBView, user: str, groups: List[str]) \
            -> str | None:
        """
        Get the user and group enforcement expression for a vector DB.

        Args:
            vector_db (VectorDBView): The vector DB object.
            user (str): The user requesting the filter expression.
            groups (List[str]): The groups the user belongs to.

        Returns:
            str | None: The user and group enforcement expression.
        """
        user_group_filter_expressions = []

        # User enforcement
        if vector_db.user_enforcement == 1:
            user_group_filter_expressions.append(f"array_contains(users, '{user}')")

        # Group enforcement
        if vector_db.group_enforcement == 1:
            if groups and len(groups) > 0:
                converted_groups = json.dumps(groups).replace('"', "'")
                user_group_filter_expressions.append(f"array_contains_any(groups, {converted_groups})")

        if user_group_filter_expressions:
            if len(user_group_filter_expressions) > 1:
                return f"({' || '.join(user_group_filter_expressions)})"
            else:
                return user_group_filter_expressions[0]
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def get_metadata_filter_expressions(self, filters: Dict[str, List[MetadataFilterCriteria]]) -> str | None:
        """
        Get the metadata filter expressions for a vector DB.

        Args:
            filters (Dict[str, List[MetadataFilterCriteria]]): The metadata filters to apply.

        Returns:
            str | None: The metadata filter expressions.
        """
        expressions = []

        for metadata, filter_criteria_list in filters.items():
            filter_expressions = []
            for filter_criteria in filter_criteria_list:
                not_exists_condition = f" || (not exists metadata['{metadata}'])"
                condition = f"(((exists metadata['{metadata}']) && (metadata['{metadata}'] {filter_criteria.operator_value} {filter_criteria.metadata_value})){not_exists_condition})"
                if condition not in filter_expressions:
                    filter_expressions.append(condition)

            negative_expression_present = any("!=" in expression for expression in filter_expressions)
            if len(filter_expressions) > 1:
                operator = " && " if negative_expression_present else " || "
                combined_conditions = f"({operator.join(filter_expressions)})"
                expressions.append(combined_conditions)
            else:
                expressions.append(filter_expressions[0])

        # Combine all filter expressions
        if expressions:
            if len(expressions) > 1:
                return f"({' && '.join(expressions)})"
            else:
                return expressions[0]
        else:
            return None
