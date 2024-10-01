import json
from typing import List, Dict, Union, Optional

from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from paig_authorizer_core.filter.base_vector_db_filter_creator import BaseVectorDBFilterCreator
from paig_authorizer_core.models.data_models import VectorDBData


class OpenSearchFilterCreator(BaseVectorDBFilterCreator):
    """
    Creates filter expressions for OpenSearch based on policies, user, and group information.
    """

    def create_filter_expression(self, vector_db: VectorDBData, user: str, groups: List[str],
                                 filters: Dict[str, List[MetadataFilterCriteria]]) -> Union[str, dict, None]:
        """
        Create a filter expression for OpenSearch.

        Args:
            vector_db (VectorDBView): The vector DB object.
            user (str): The user requesting the filter expression.
            groups (List[str]): The groups the user belongs to.
            filters (Dict[str, List[MetadataFilterCriteria]]): The metadata filters to apply.

        Returns:
            str | dict | None: The filter expression.
        """
        final_expressions = []

        user_group_enforcement_expression = self.get_user_group_enforcement_expression(vector_db, user, groups)
        if user_group_enforcement_expression:
            final_expressions.append(user_group_enforcement_expression)

        metadata_filter_expression = self.get_metadata_filter_expressions(filters)
        if metadata_filter_expression:
            final_expressions.append(metadata_filter_expression)

        if final_expressions:
            return json.dumps({"bool": {"must": final_expressions}})
        else:
            return ""

    # noinspection PyMethodMayBeStatic
    def get_user_group_enforcement_expression(self, vector_db: VectorDBData, user: str, groups: List[str]) \
            -> Optional[dict]:
        """
        Get the user and group enforcement expression for OpenSearch.

        Args:
            vector_db (VectorDBView): The vector DB object.
            user (str): The user requesting the filter expression.
            groups (List[str]): The groups the user belongs to.

        Returns:
            Optional[dict]: The user and group enforcement expression.
        """
        user_group_filter_expressions = []

        # User enforcement
        if vector_db.user_enforcement == 1:
            user_group_filter_expressions.append({"term": {"metadata.users": user}})

        # Group enforcement
        if vector_db.group_enforcement == 1:
            if groups and len(groups) > 0:
                user_group_filter_expressions.append({"terms": {"metadata.groups": groups}})

        if user_group_filter_expressions:
            if len(user_group_filter_expressions) > 1:
                return {"bool": {"should": user_group_filter_expressions}}
            else:
                return user_group_filter_expressions[0]
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def get_metadata_filter_expressions(self, filters: Dict[str, List[MetadataFilterCriteria]]) -> Optional[dict]:
        """
        Get the metadata filter expressions for OpenSearch.

        Args:
            filters (Dict[str, List[MetadataFilterCriteria]]): The metadata filters to apply.

        Returns:
            Optional[dict]: The metadata filter expressions.
        """
        expressions = []

        for metadata, filter_criteria_list in filters.items():
            filter_expressions = []
            for filter_criteria in filter_criteria_list:
                not_exists_condition = {"bool": {"must_not": {"exists": {"field": f"metadata.metadata.{metadata}.keyword"}}}}
                condition = {
                    "bool": {
                        "should": [
                            {
                                "bool": {
                                    "must": [
                                        {"exists": {"field": f"metadata.metadata.{metadata}.keyword"}},
                                        {"script": {
                                            "script": f"doc['metadata.metadata.{metadata}.keyword'].value {filter_criteria.operator_value} {filter_criteria.metadata_value}"}}
                                    ]
                                },
                            },
                            not_exists_condition
                        ]
                    }
                }
                filter_expressions.append(condition)

            negative_expression_present = any("!=" in json.dumps(expression) for expression in filter_expressions)
            if len(filter_expressions) > 1:
                operator = "must" if negative_expression_present else "should"
                combined_conditions = {"bool": {operator: filter_expressions}}
                expressions.append(combined_conditions)
            else:
                expressions.append(filter_expressions[0])

        if expressions:
            if len(expressions) > 1:
                return {"bool": {"must": expressions}}
            else:
                return expressions[0]
        else:
            return None
