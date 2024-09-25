import pytest
from unittest.mock import Mock

from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import BaseMetadataFilterCriteriaCreator, \
    MetadataFilterCriteria
from paig_authorizer_core.models.data_models import VectorDBPolicyData


@pytest.fixture
def metadata_filter_creator():
    return BaseMetadataFilterCriteriaCreator()


def test_prepare_operator(metadata_filter_creator):
    assert metadata_filter_creator.prepare_operator("ne") == "!="
    assert metadata_filter_creator.prepare_operator("eq") == "=="


def test_reverse_operator(metadata_filter_creator):
    assert metadata_filter_creator.reverse_operator("ne") == "eq"
    assert metadata_filter_creator.reverse_operator("eq") == "ne"


def test_is_integer(metadata_filter_creator):
    assert metadata_filter_creator.is_integer("123")
    assert not metadata_filter_creator.is_integer("123.45")
    assert not metadata_filter_creator.is_integer("abc")


def test_is_float(metadata_filter_creator):
    assert metadata_filter_creator.is_float("123.45")
    assert metadata_filter_creator.is_float("123")
    assert not metadata_filter_creator.is_float("abc")


def test_is_boolean(metadata_filter_creator):
    assert metadata_filter_creator.is_boolean("true")
    assert metadata_filter_creator.is_boolean("false")
    assert not metadata_filter_creator.is_boolean("abc")


def test_prepare_metadata_value(metadata_filter_creator):
    assert metadata_filter_creator.prepare_metadata_value("123") == "123"
    assert metadata_filter_creator.prepare_metadata_value("123.45") == "123.45"
    assert metadata_filter_creator.prepare_metadata_value("true") == "TRUE"
    assert metadata_filter_creator.prepare_metadata_value("some_string") == "'some_string'"


def test_get_metadata_filter(metadata_filter_creator):
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
    assert result.metadata_value == "'value1'"
    assert result.operator_value == "=="


def test_create_metadata_filters(metadata_filter_creator):
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


def test_create_metadata_filters_with_multiple_policies(metadata_filter_creator):
    policy1 = Mock(spec=VectorDBPolicyData)
    policy1.allowed_users = ["user1"]
    policy1.denied_users = []
    policy1.allowed_groups = ["group1"]
    policy1.denied_groups = []
    policy1.operator = "eq"
    policy1.metadata_key = "key1"
    policy1.metadata_value = "value1"

    policy2 = Mock(spec=VectorDBPolicyData)
    policy2.allowed_users = []
    policy2.denied_users = ["user2"]
    policy2.allowed_groups = []
    policy2.denied_groups = ["group2"]
    policy2.operator = "ne"
    policy2.metadata_key = "key2"
    policy2.metadata_value = "value2"

    result = metadata_filter_creator.create_metadata_filters([policy1, policy2], "user1", ["group1"])
    assert "key1" in result
    assert len(result["key1"]) == 1
    assert isinstance(result["key1"][0], MetadataFilterCriteria)

    result = metadata_filter_creator.create_metadata_filters([policy1, policy2], "user2", ["group2"])
    assert "key2" in result
    assert len(result["key2"]) == 1
    assert isinstance(result["key2"][0], MetadataFilterCriteria)
