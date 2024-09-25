import pytest
from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.filter.milvus_filter_creator import MilvusFilterCreator


@pytest.fixture
def milvus_filter_creator():
    return MilvusFilterCreator()


def create_vector_db(user_enforcement, group_enforcement):
    return VectorDBData(
        name="vector_db_name",
        description="vector_db_description",
        type="MILVUS",
        user_enforcement=user_enforcement,
        group_enforcement=group_enforcement,
        ai_applications=[]
    )


def test_create_filter_expression_no_filters(milvus_filter_creator):
    vector_db = create_vector_db(0, 0)
    user = "testuser"
    groups = ["group1", "group2"]
    filters = {}

    result = milvus_filter_creator.create_filter_expression(vector_db, user, groups, filters)
    assert result == ""


def test_create_filter_expression_with_filters(milvus_filter_creator):
    vector_db = create_vector_db(0, 0)
    user = "testuser"
    groups = ["group1", "group2"]
    filters = {
        "key1": [MetadataFilterCriteria("key1", "'value1'", "==")],
        "key2": [MetadataFilterCriteria("key2", "'value2'", "!=")],
    }

    result = milvus_filter_creator.create_filter_expression(vector_db, user, groups, filters)
    expected_expression = (
        "(((exists metadata['key1']) && (metadata['key1'] == 'value1')) || (not exists metadata['key1'])) && "
        "(((exists metadata['key2']) && (metadata['key2'] != 'value2')) || (not exists metadata['key2']))"
    )
    assert result == f"({expected_expression})"


def test_get_user_group_enforcement_expression_user_only(milvus_filter_creator):
    vector_db = create_vector_db(1, 0)
    vector_db.user_enforcement = 1
    vector_db.group_enforcement = 0
    user = "testuser"
    groups = ["group1", "group2"]

    result = milvus_filter_creator.get_user_group_enforcement_expression(vector_db, user, groups)
    assert result == "array_contains(users, 'testuser')"


def test_get_user_group_enforcement_expression_group_only(milvus_filter_creator):
    vector_db = create_vector_db(0, 1)
    vector_db.user_enforcement = 0
    vector_db.group_enforcement = 1
    user = "testuser"
    groups = ["group1", "group2"]

    result = milvus_filter_creator.get_user_group_enforcement_expression(vector_db, user, groups)
    expected_groups = "['group1', 'group2']".replace('"', "'")
    assert result == f"array_contains_any(groups, {expected_groups})"


def test_get_metadata_filter_expressions(milvus_filter_creator):
    filters = {
        "key1": [MetadataFilterCriteria("key1", "'value1'", "==")],
        "key2": [MetadataFilterCriteria("key2", "'value2'", "!=")],
    }

    result = milvus_filter_creator.get_metadata_filter_expressions(filters)
    expected_expression = (
        "(((exists metadata['key1']) && (metadata['key1'] == 'value1')) || (not exists metadata['key1'])) && "
        "(((exists metadata['key2']) && (metadata['key2'] != 'value2')) || (not exists metadata['key2']))"
    )
    assert result == f"({expected_expression})"
