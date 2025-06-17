import pytest
from unittest.mock import Mock

from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from paig_authorizer_core.filter.snowflake_cortex_metadata_filter_creator import SnowflakeCortexMetadataFilterCreator
from paig_authorizer_core.models.data_models import VectorDBPolicyData


@pytest.fixture
def metadata_filter_creator():
    return SnowflakeCortexMetadataFilterCreator()


def test_prepare_metadata_value_string(metadata_filter_creator):
    """Test that string values are not quoted for Snowflake Cortex."""
    value = metadata_filter_creator.prepare_metadata_value("test_value")
    assert value == "test_value"  # No quotes added


def test_prepare_metadata_value_int(metadata_filter_creator):
    """Test that integer values are passed through as-is."""
    value = metadata_filter_creator.prepare_metadata_value("123")
    assert value == "123"


def test_prepare_metadata_value_float(metadata_filter_creator):
    """Test that float values are passed through as-is."""
    value = metadata_filter_creator.prepare_metadata_value("123.45")
    assert value == "123.45"


def test_prepare_metadata_value_boolean(metadata_filter_creator):
    """Test that boolean values are converted to uppercase."""
    value = metadata_filter_creator.prepare_metadata_value("true")
    assert value == "TRUE"


def test_get_metadata_filter(metadata_filter_creator):
    """Test that the metadata filter is created correctly with unquoted string values."""
    policy = Mock(spec=VectorDBPolicyData)
    policy.allowed_users = ["user1"]
    policy.denied_users = []
    policy.allowed_groups = ["group1"]
    policy.denied_groups = []
    policy.operator = "eq"
    policy.metadata_key = "key1"
    policy.metadata_value = "value1"

    result = metadata_filter_creator.get_metadata_filter(policy, True, "user1", ["group1"])
    assert isinstance(result, MetadataFilterCriteria)
    assert result.metadata_key == "key1"
    assert result.metadata_value == "value1"  # No quotes
    assert result.operator_value == "=="


def test_create_metadata_filters(metadata_filter_creator):
    """Test creating metadata filters with the Snowflake Cortex creator."""
    policy = Mock(spec=VectorDBPolicyData)
    policy.allowed_users = ["user1"]
    policy.denied_users = []
    policy.allowed_groups = ["group1"]
    policy.denied_groups = []
    policy.operator = "eq"
    policy.metadata_key = "key1"
    policy.metadata_value = "value1"

    result = metadata_filter_creator.create_metadata_filters([policy], "user1", ["group1"])
    assert "key1" in result
    assert len(result["key1"]) == 1
    assert isinstance(result["key1"][0], MetadataFilterCriteria)
    assert result["key1"][0].metadata_value == "value1"  # No quotes 