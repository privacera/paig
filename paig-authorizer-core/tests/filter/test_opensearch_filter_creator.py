import json

import pytest
from unittest.mock import Mock
from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import MetadataFilterCriteria
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.filter.opensearch_filter_creator import OpenSearchFilterCreator


@pytest.fixture
def opensearch_filter_creator():
    return OpenSearchFilterCreator()


def test_create_filter_expression_no_filters(opensearch_filter_creator):
    vector_db = Mock(spec=VectorDBData)
    vector_db.user_enforcement = 0
    vector_db.group_enforcement = 0

    user = "testuser"
    groups = ["group1", "group2"]
    filters = {}

    result = opensearch_filter_creator.create_filter_expression(vector_db, user, groups, filters)
    assert result == ""


def test_create_filter_expression_with_filters(opensearch_filter_creator):
    vector_db = Mock(spec=VectorDBData)
    vector_db.user_enforcement = 0
    vector_db.group_enforcement = 0

    user = "testuser"
    groups = ["group1", "group2"]
    filters = {
        "key1": [MetadataFilterCriteria("key1", "'value1'", "==")],
        "key2": [MetadataFilterCriteria("key2", "'value2'", "!=")],
    }

    result = opensearch_filter_creator.create_filter_expression(vector_db, user, groups, filters)
    expected_expression = {
        "bool": {
            "must": [
                {
                    "bool": {
                        "must": [
                            {
                                "bool": {
                                    "should": [
                                        {
                                            "bool": {
                                                "must": [
                                                    {"exists": {"field": "metadata.metadata.key1.keyword"}},
                                                    {"script": {"script": "doc['metadata.metadata.key1.keyword'].value == 'value1'"}},
                                                ]
                                            },
                                        },
                                        {"bool": {"must_not": {"exists": {"field": "metadata.metadata.key1.keyword"}}}},
                                    ]
                                }
                            },
                            {
                                "bool": {
                                    "should": [
                                        {
                                            "bool": {
                                                "must": [
                                                    {"exists": {"field": "metadata.metadata.key2.keyword"}},
                                                    {"script": {"script": "doc['metadata.metadata.key2.keyword'].value != 'value2'"}},
                                                ]
                                            },
                                        },
                                        {"bool": {"must_not": {"exists": {"field": "metadata.metadata.key2.keyword"}}}},
                                    ]
                                }
                            },
                        ]
                    }
                }
            ]
        }
    }
    assert json.loads(result) == expected_expression


def test_get_user_group_enforcement_expression_user_only(opensearch_filter_creator):
    vector_db = Mock(spec=VectorDBData)
    vector_db.user_enforcement = 1
    vector_db.group_enforcement = 0
    user = "testuser"
    groups = ["group1", "group2"]

    result = opensearch_filter_creator.get_user_group_enforcement_expression(vector_db, user, groups)
    expected_expression = {"term": {"metadata.users": "testuser"}}
    assert result == expected_expression


def test_get_user_group_enforcement_expression_group_only(opensearch_filter_creator):
    vector_db = Mock(spec=VectorDBData)
    vector_db.user_enforcement = 0
    vector_db.group_enforcement = 1
    user = "testuser"
    groups = ["group1", "group2"]

    result = opensearch_filter_creator.get_user_group_enforcement_expression(vector_db, user, groups)
    expected_expression = {"terms": {"metadata.groups": groups}}
    assert result == expected_expression


def test_get_metadata_filter_expressions(opensearch_filter_creator):
    filters = {
        "key1": [MetadataFilterCriteria("key1", "'value1'", "==")],
        "key2": [MetadataFilterCriteria("key2", "'value2'", "!=")],
    }

    result = opensearch_filter_creator.get_metadata_filter_expressions(filters)
    expected_expression = {
        "bool": {
            "must": [
                {
                    "bool": {
                        "should": [
                            {
                                "bool": {
                                    "must": [
                                        {"exists": {"field": "metadata.metadata.key1.keyword"}},
                                        {"script": {"script": "doc['metadata.metadata.key1.keyword'].value == 'value1'"}},
                                    ]
                                },
                            },
                            {"bool": {"must_not": {"exists": {"field": "metadata.metadata.key1.keyword"}}}},
                        ]
                    }
                },
                {
                    "bool": {
                        "should": [
                            {
                                "bool": {
                                    "must": [
                                        {"exists": {"field": "metadata.metadata.key2.keyword"}},
                                        {"script": {"script": "doc['metadata.metadata.key2.keyword'].value != 'value2'"}},
                                    ]
                                },
                            },
                            {"bool": {"must_not": {"exists": {"field": "metadata.metadata.key2.keyword"}}}},
                        ]
                    }
                },
            ]
        }
    }
    assert result == expected_expression
