from typing import Dict, List

import pytest
from unittest.mock import Mock
from api.authz.authorizer.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from api.authz.authorizer.filter.base_vector_db_filter_creator import BaseVectorDBFilterCreator
from api.governance.api_schemas.vector_db import VectorDBView


class VectorDBFilterCreatorMock(BaseVectorDBFilterCreator):
    def create_filter_expression(self, vector_db: VectorDBView, user: str, groups: List[str],
                                 filters: Dict[str, List[MetadataFilterCriteria]]) -> str:
        return "mock_filter_expression"


@pytest.fixture
def vector_db_filter_creator():
    return VectorDBFilterCreatorMock()


def test_create_filter_expression(vector_db_filter_creator):
    vector_db = Mock(spec=VectorDBView)
    user = "testuser"
    groups = ["group1", "group2"]
    filters = {"key1": [MetadataFilterCriteria("key1", "value1", "==")]}

    result = vector_db_filter_creator.create_filter_expression(vector_db, user, groups, filters)
    assert result == "mock_filter_expression"


def test_abstract_method_not_implemented():
    with pytest.raises(TypeError):
        instance = BaseVectorDBFilterCreator()
