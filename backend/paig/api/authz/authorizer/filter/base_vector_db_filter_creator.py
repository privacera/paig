from abc import ABC, abstractmethod
from typing import List, Dict

from api.authz.authorizer.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from api.governance.api_schemas.vector_db import VectorDBView


class BaseVectorDBFilterCreator(ABC):
    """
    Abstract class for creating filter expressions for vector DBs.
    """

    @abstractmethod
    def create_filter_expression(self, vector_db: VectorDBView, user: str, groups: List[str], filters: Dict[str, List[MetadataFilterCriteria]]) -> str | dict:
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
        pass