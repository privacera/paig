from api.audit.opensearch_service.opensearch_util import (
    add_equal_query,
    add_equal_in_list_query,
    build_query,
    build_wildcard_query,
    add_range_query,
    build_search_request_with_aggregations,
    extract_search_response_aggregations,
    extract_group_by_aggregations
)
from api.audit.api_schemas.access_audit_schema import IncludeQueryParams


def test_add_equal_query():
    output_query_list = []
    add_equal_query("test_field", "test_value", output_query_list, is_admin_audit=False)
    assert output_query_list == [{"bool": {"should": [{"term": {"test_field": "test_value"}}]}}]


def test_add_equal_query_with_none_value():
    output_query_list = []
    add_equal_query("test_field", None, output_query_list, is_admin_audit=False)
    assert output_query_list == []


def test_add_equal_in_list_query():
    output_query_list = []
    add_equal_in_list_query("test_field", "value1,value2", output_query_list, is_admin_audit=False)
    assert output_query_list == [
        {
            "bool": {
                "should": [
                    {"terms": {"test_field": ["value1", "value2"]}}
                ]
            }
        }
    ]


def test_build_wildcard_query():
    query = build_wildcard_query("test_field", "*value*")
    assert query == {"wildcard": {"test_field": {"value": "*value*", "case_insensitive": True}}}


def test_add_range_query():
    range_query = add_range_query("test_field", 1000, 2000)
    assert range_query == {"range": {"test_field": {"gte": 1000, "lte": 2000}}}


def test_build_query():
    include_query = IncludeQueryParams()
    include_query.user_id = "test1"
    exclude_query = IncludeQueryParams()
    exclude_query.user_id = "test2"
    from_time = 1000
    to_time = 2000
    query = build_query(include_query, exclude_query, from_time, to_time, is_admin_audits=False)
    assert query == {
        "bool": {
            "must": [
                {"bool": {"should": [{"term": {"userId": "test1"}}]}},
                {"range": {"eventTime": {"gte": 1000, "lte": 2000}}}
            ],
            "must_not": [
                {"bool": {"should": [{"term": {"userId": "test2"}}]}}
            ]
        }
    }


def test_build_search_request_with_aggregations():
    search_request = {}
    updated_query = build_search_request_with_aggregations(
        group_by="field1,field2",
        interval="day",
        size=10,
        cardinality=False,
        is_admin_audits=False,
        search_request=search_request
    )

    expected_agg = {
        "date_histogram": {
            "field": "eventTime",
            "interval": "day",
        },
        "aggs": {
            "field1": {
                "terms": {
                    "field": "field1",
                    "size": 10
                },
                "aggregations": {
                    "field2": {
                        "terms": {
                            "field": "field2"
                        }
                    }
                }
            }
        }
    }
    assert updated_query['aggs']['date_histogram'] == expected_agg


def test_extract_search_response_aggregations():
    aggregations = {
        "day": {
            "buckets": [
                {
                    "key": 1609459200000,  # Example timestamp
                    "doc_count": 100,
                    "field1": {
                        "buckets": [
                            {"key": "value1", "doc_count": 50},
                            {"key": "value2", "doc_count": 50}
                        ]
                    }
                }
            ]
        }
    }

    extracted = extract_search_response_aggregations("day", aggregations)
    expected = {
        "day": {
            1609459200000: {
                "field1": {
                    "value1": {"count": 50},
                    "value2": {"count": 50}
                }
            }
        }
    }
    assert extracted == expected


def test_extract_group_by_aggregations():
    aggregations = {
        "field1": {
            "buckets": [
                {"key": "value1", "doc_count": 50},
                {"key": "value2", "doc_count": 50}
            ]
        }
    }

    extracted = extract_group_by_aggregations(aggregations)
    expected = {
        "field1": {
            "value1": {"count": 50},
            "value2": {"count": 50}
        }
    }

    assert extracted == expected

