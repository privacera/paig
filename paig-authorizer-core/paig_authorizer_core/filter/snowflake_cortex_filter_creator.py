import json
from typing import Dict, List

from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from paig_authorizer_core.filter.base_vector_db_filter_creator import BaseVectorDBFilterCreator
from paig_authorizer_core.models.data_models import VectorDBData


class SnowflakeCortexFilterCreator(BaseVectorDBFilterCreator):
    """
    Creates filter expressions for Snowflake Cortex based on policies, user, and group information.
    """

    def create_filter_expression(self, vector_db: VectorDBData, user: str, groups: List[str],
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
            return json.dumps({"@and": final_expressions})
        else:
            return ""

    # noinspection PyMethodMayBeStatic
    def get_user_group_enforcement_expression(self, vector_db: VectorDBData, user: str, groups: List[str]) -> str | None:
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
            user_group_filter_expressions.append({"@contains": {"users": user}})

        # Group enforcement
        if vector_db.group_enforcement == 1:
            if groups and len(groups) > 0:
                group_expressions = []
                for group in groups:
                    group_expressions.append({"@contains": {"groups": group}})
                if len(group_expressions) > 1:
                    user_group_filter_expressions.append({"@or": group_expressions})
                else:
                    user_group_filter_expressions.append(group_expressions[0])

        if user_group_filter_expressions:
            if len(user_group_filter_expressions) > 1:
                return {"@or": user_group_filter_expressions}
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
            field_expressions = []
            for filter_criteria in filter_criteria_list:
                # Convert operator and value into Snowflake Cortex syntax
                operator = filter_criteria.operator_value
                value = filter_criteria.metadata_value
                
                # Handle different operators
                if "==" in operator:
                    field_expressions.append({"@eq": {metadata: value}})
                elif "!=" in operator:
                    field_expressions.append({"@ne": {metadata: value}})
                else:
                    raise ValueError(f"Unsupported operator for Snowflake Cortex: {operator}")
            
            # Combine expressions for this metadata field
            if len(field_expressions) > 1:
                # If there are multiple criteria for the same field, combine with @or or @and depending on operators
                has_negative_operator = any("@ne" in str(expr) for expr in field_expressions)
                if has_negative_operator:
                    expressions.append({"@and": field_expressions})
                else:
                    expressions.append({"@or": field_expressions})
            elif field_expressions:
                expressions.append(field_expressions[0])

        # Combine all metadata field expressions
        if expressions:
            if len(expressions) > 1:
                return {"@and": expressions}
            else:
                return expressions[0]
        else:
            return None
