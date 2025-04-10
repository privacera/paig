import json
from typing import Dict, List

import pytest
from unittest.mock import Mock

from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from paig_authorizer_core.filter.snowflake_cortex_filter_creator import SnowflakeCortexFilterCreator
from paig_authorizer_core.models.data_models import VectorDBData


@pytest.fixture
def filter_creator():
    return SnowflakeCortexFilterCreator()


@pytest.fixture
def vector_db():
    vector_db = Mock(spec=VectorDBData)
    vector_db.user_enforcement = 1
    vector_db.group_enforcement = 1
    return vector_db


def test_get_metadata_filter_expressions_equals(filter_creator):
    """Test generating filter expressions for equal operators."""
    # Create metadata filter criteria for an equality condition
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "category": [MetadataFilterCriteria("category", "news", "==")]
    }

    result = filter_creator.get_metadata_filter_expressions(metadata_filters)
    
    # Should be an OR condition with the value and empty string
    assert "@or" in result
    assert len(result["@or"]) == 2
    assert result["@or"][0] == {"@eq": {"category": "news"}}
    assert result["@or"][1] == {"@eq": {"category": ""}}


def test_get_metadata_filter_expressions_not_equals(filter_creator):
    """Test generating filter expressions for not-equal operators."""
    # Create metadata filter criteria for a not-equal condition
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "category": [MetadataFilterCriteria("category", "archived", "!=")]
    }

    result = filter_creator.get_metadata_filter_expressions(metadata_filters)
    
    # Should be an OR condition with NOT equal and equal to empty string
    assert "@or" in result
    assert len(result["@or"]) == 2
    assert result["@or"][0] == {"@not": {"@eq": {"category": "archived"}}}
    assert result["@or"][1] == {"@eq": {"category": ""}}


def test_get_metadata_filter_expressions_multiple_values_same_field(filter_creator):
    """Test generating filter expressions for multiple values of the same field."""
    # Create metadata filter criteria with multiple values for the same field
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "category": [
            MetadataFilterCriteria("category", "news", "=="),
            MetadataFilterCriteria("category", "sports", "==")
        ]
    }

    result = filter_creator.get_metadata_filter_expressions(metadata_filters)
    
    # Should be an OR of all the conditions since they use == operator
    assert "@or" in result
    assert len(result["@or"]) == 2
    
    # Each condition is an @or itself (value or empty string)
    for item in result["@or"]:
        assert "@or" in item
        assert len(item["@or"]) == 2
        assert item["@or"][1] == {"@eq": {"category": ""}}


def test_get_metadata_filter_expressions_multiple_fields(filter_creator):
    """Test generating filter expressions for multiple different fields."""
    # Create metadata filter criteria for multiple different fields
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "category": [MetadataFilterCriteria("category", "news", "==")],
        "region": [MetadataFilterCriteria("region", "europe", "==")]
    }

    result = filter_creator.get_metadata_filter_expressions(metadata_filters)
    
    # Should be an AND of all fields
    assert "@and" in result
    assert len(result["@and"]) == 2
    
    # Each field condition is an @or (value or empty string)
    for item in result["@and"]:
        assert "@or" in item
        assert len(item["@or"]) == 2


def test_get_metadata_filter_expressions_mixed_operators(filter_creator):
    """Test generating filter expressions with a mix of equals and not-equals operators."""
    # Create metadata filter criteria with a mix of operators
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "category": [
            MetadataFilterCriteria("category", "news", "=="),
            MetadataFilterCriteria("category", "archived", "!=")
        ]
    }

    result = filter_creator.get_metadata_filter_expressions(metadata_filters)
    
    # Should be an AND because there are negative operators
    assert "@and" in result
    assert len(result["@and"]) == 2
    
    # Each condition is an @or (either value matches or empty string)
    for item in result["@and"]:
        assert "@or" in item
        assert len(item["@or"]) == 2


def test_create_filter_expression_with_user_enforcement(filter_creator, vector_db):
    """Test creating a complete filter expression with user enforcement."""
    user = "john"
    groups = ["public"]
    
    # Create metadata filter criteria
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "category": [MetadataFilterCriteria("category", "news", "==")]
    }
    
    result = filter_creator.create_filter_expression(vector_db, user, groups, metadata_filters)
    
    # Convert result to dictionary (from JSON string)
    result_dict = json.loads(result)
    
    # Should be an AND of user/group enforcement and metadata filters
    assert "@and" in result_dict
    assert len(result_dict["@and"]) == 2
    
    # First part should be user/group enforcement
    user_group_part = result_dict["@and"][0]
    assert "@or" in user_group_part
    assert len(user_group_part["@or"]) == 2
    assert {"@contains": {"users": "john"}} in user_group_part["@or"]
    assert {"@contains": {"groups": "public"}} in user_group_part["@or"]
    
    # Second part should be metadata filters
    metadata_part = result_dict["@and"][1]
    assert "@or" in metadata_part
    assert len(metadata_part["@or"]) == 2
    assert metadata_part["@or"][0] == {"@eq": {"category": "news"}}
    assert metadata_part["@or"][1] == {"@eq": {"category": ""}}


def test_create_filter_expression_complex(filter_creator, vector_db):
    """Test creating a complex filter expression with multiple fields and mixed operators."""
    user = "bob"
    groups = ["public"]
    
    # Create complex metadata filter criteria
    metadata_filters: Dict[str, List[MetadataFilterCriteria]] = {
        "plant_location": [MetadataFilterCriteria("plant_location", "be_de", "!=")],
        "security": [
            MetadataFilterCriteria("security", "Confidential", "!="),
            MetadataFilterCriteria("security", "Internal", "!=")
        ]
    }
    
    result = filter_creator.create_filter_expression(vector_db, user, groups, metadata_filters)
    
    # Convert result to dictionary (from JSON string)
    result_dict = json.loads(result)
    
    # Should match the complex structure in the example
    assert "@and" in result_dict
    assert len(result_dict["@and"]) == 2
    
    # Check user enforcement part
    user_group_part = result_dict["@and"][0]
    assert "@or" in user_group_part
    assert {"@contains": {"users": "bob"}} in user_group_part["@or"]
    
    # Check metadata filters part
    metadata_part = result_dict["@and"][1]
    assert "@and" in metadata_part
    assert len(metadata_part["@and"]) == 2
    
    # Check plant_location filter
    plant_location_part = metadata_part["@and"][0]
    assert "@or" in plant_location_part
    assert len(plant_location_part["@or"]) == 2
    assert plant_location_part["@or"][0] == {"@not": {"@eq": {"plant_location": "be_de"}}}
    assert plant_location_part["@or"][1] == {"@eq": {"plant_location": ""}}
    
    # Check security filters (should be an AND of two security conditions)
    security_part = metadata_part["@and"][1]
    assert "@and" in security_part
    assert len(security_part["@and"]) == 2
    
    # Each security condition should be an OR
    for sec_condition in security_part["@and"]:
        assert "@or" in sec_condition
        assert len(sec_condition["@or"]) == 2
        assert sec_condition["@or"][1] == {"@eq": {"security": ""}} 