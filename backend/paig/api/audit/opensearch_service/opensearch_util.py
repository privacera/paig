import copy
from typing import List, Dict, Any, Union, Optional
from collections import defaultdict
import logging

from api.audit.api_schemas.access_audit_schema import extract_include_query_params
from api.audit.opensearch_service.opensearch_client import (
    OBJECT_STATE_PREFIX,
    OBJECT_STATE_PREVIOUS_PREFIX,
    KEYWORD_POSTFIX,
    PARTIAL_MATCH_POSTFIX
)

logger = logging.getLogger(__name__)


def add_equal_query(field_name: str, field_value: Any, output_query_list: List[Dict], is_admin_audit: bool):
    if field_value is None:
        return

    field = field_name
    if not is_admin_audit:
        field = field_name.replace(OBJECT_STATE_PREFIX, "")

    combine_conditions = field_equal_query(field, field_value)

    if is_admin_audit and field.startswith(OBJECT_STATE_PREFIX):
        field = field.replace(OBJECT_STATE_PREFIX, OBJECT_STATE_PREVIOUS_PREFIX)
        combine_conditions += field_equal_query(field, field_value)

    output_query_list.append({
        "bool": {
            "should": combine_conditions
        }
    })


def add_equal_in_list_query(field_name: str, field_value: str, output_query_list: List[Dict], is_admin_audit: bool):
    if not field_value:
        return

    field = field_name + KEYWORD_POSTFIX if is_admin_audit and field_name.startswith(
        OBJECT_STATE_PREFIX) else field_name.replace(OBJECT_STATE_PREFIX, "")
    value = field_value

    combine_conditions = build_query_field_value(field, value)

    if is_admin_audit and field.startswith(OBJECT_STATE_PREFIX):
        field = field.replace(OBJECT_STATE_PREFIX, OBJECT_STATE_PREVIOUS_PREFIX)
        combine_conditions += build_query_field_value(field, value)

    output_query_list.append({
        "bool": {
            "should": combine_conditions
        }
    })


def field_equal_query(field_name: str, field_value: Union[str, bool, int, float]) -> List[Dict]:
    field = field_name
    value = None

    if isinstance(field_value, str):
        value = field_value
        if field_name.startswith(OBJECT_STATE_PREFIX) or field_name.startswith(OBJECT_STATE_PREVIOUS_PREFIX):
            if field_name.endswith(PARTIAL_MATCH_POSTFIX):
                # if field to search by partial match then skip adding .keyword postfix
                field = field_name.replace(PARTIAL_MATCH_POSTFIX, "")
                # partial search works with only lower case values
                value = value.lower()
            else:
                field = field_name + KEYWORD_POSTFIX

        return build_query_field_value(field, value)

    if isinstance(field_value, bool):
        return [boolean_equal_query(field, field_value)]

    if isinstance(field_value, int) or isinstance(field_value, float):
        return [long_equal_query(field, field_value)]

    return []


def boolean_equal_query(field_name: str, field_value: bool) -> Dict:
    return {
        "term": {
            field_name: field_value
        }
    }


def int_equal_query(field_name: str, field_value: int) -> Dict:
    return {
        "term": {
            field_name: field_value
        }
    }


def long_equal_query(field_name: str, field_value: Union[int, float]) -> Dict:
    return {
        "term": {
            field_name: field_value
        }
    }


def build_wildcard_query(field: str, value: str) -> Dict:
    return {
        "wildcard": {
            field: {
                "value": value,
                "case_insensitive": True
            }
        }
    }


def add_range_query(field_name: str, fromTime: Optional[int], toTime: Optional[int]) -> Optional[dict]:
    if fromTime or toTime:
        range_query = {"range": {field_name: {}}}
        if fromTime:
            range_query["range"][field_name]["gte"] = fromTime
        if toTime:
            range_query["range"][field_name]["lte"] = toTime
        return range_query
    return None


def add_message_match_query(field_value: str, output_query_list: List[Dict]):
    if not field_value:
        return

    combine_conditions = field_equal_query("original_message", field_value) + field_equal_query("masked_message",
                                                                                                field_value)
    output_query_list.append({
        "bool": {
            "should": combine_conditions
        }
    })


def add_dynamic_filters(shield_audit_filter_params, conditions, is_admin_audit):
    for key, value in shield_audit_filter_params.items():
        if value is not None:
            add_query_condition(key, value, conditions, is_admin_audit)


def add_query_condition(field_name, value, conditions, is_admin_audit):
    if isinstance(value, list) or "," in value:
        add_equal_in_list_query(field_name, value, conditions, is_admin_audit)
    else:
        add_equal_query(field_name, value, conditions, is_admin_audit)


def build_conditions(shield_audit_filter_params, is_admin_audit):
    conditions = []

    if shield_audit_filter_params is None:
        return conditions

    add_dynamic_filters(extract_include_query_params(shield_audit_filter_params), conditions, is_admin_audit)

    return conditions


def build_query(include_query, exclude_query, from_time, to_time, is_admin_audits) -> dict:
    include_conditions = build_conditions(include_query, is_admin_audits)
    exclude_conditions = build_conditions(exclude_query, is_admin_audits)

    exclude_not_equal_conditions = []
    for query in exclude_conditions:
        exclude_not_equal_conditions.append(query)

    sort_column = "logTime" if is_admin_audits else "eventTime"
    if OBJECT_STATE_PREFIX in sort_column:
        sort_column = sort_column.replace(OBJECT_STATE_PREFIX, "")

    range_query = add_range_query(sort_column, from_time, to_time)

    bool_query = {
        "bool": {
            "must": include_conditions,
            "must_not": exclude_not_equal_conditions,
        }
    }

    if range_query:
        bool_query["bool"]["must"].append(range_query)

    return bool_query


def build_query_field_value(field: str, value: str) -> List[Dict]:
    if "*" in value and "," in value:
        field_values = [val.strip() for val in value.split(",")]
        return [build_wildcard_query(field, val) for val in field_values]

    if "*" in value:
        return [build_wildcard_query(field, value)]

    if "," in value:
        field_values = [val.strip() for val in value.split(",")]
        return [{
            "terms": {
                field: field_values
            }
        }]

    return [{
        "term": {
            field: value
        }
    }]


def convert_to_sorted_dict(data):
    if len(data) == 0:
        return []
    # Split the string by commas to get individual elements
    elements = data[0].split(',')

    # The last element is the order
    order = elements[-1]

    # The rest are the fields
    fields = elements[:-1]

    # Create the desired list of dictionaries
    sort = [{field: {"order": order}} for field in fields]

    return sort


# Example utility functions that need to be defined as per your logic
def get_list_from_comma_separated_string(value: str) -> List[str]:
    return value.split(',')


def get_group_by_aggregation(group_by_list: List[str], size, cardinality, is_admin_audits) -> dict:
    aggregation_builder = get_aggregation_builder(group_by_list[0], group_by_list, size, cardinality, is_admin_audits)

    if len(group_by_list) == 1:
        return {group_by_list[0]: aggregation_builder}
    elif len(group_by_list) == 2:
        return {group_by_list[0]: {**aggregation_builder, "aggregations": {group_by_list[1]: get_aggregation_builder(group_by_list[1], group_by_list, size, cardinality, is_admin_audits)}}}
    else:
        return {group_by_list[0]: {**aggregation_builder, "aggregations": {group_by_list[1]: get_group_by_aggregation(group_by_list[1:], size, cardinality, is_admin_audits)}}}


def get_aggregation_builder(current_group_by_field: str, group_by_list, size, is_cardinality, is_admin_audits) -> dict:
    field = current_group_by_field
    if (is_admin_audits and
            (current_group_by_field.startswith(OBJECT_STATE_PREFIX) or current_group_by_field.startswith(OBJECT_STATE_PREVIOUS_PREFIX)) and
            not current_group_by_field.endswith(KEYWORD_POSTFIX)):
        field += KEYWORD_POSTFIX

    term_aggregation = {"field": field}
    is_first_group_by_field = False
    is_last_group_by_field = False

    if len(group_by_list) > 0:
        is_first_group_by_field = group_by_list[0] == field
        is_last_group_by_field = group_by_list[-1] == field

    if is_cardinality:
        if is_first_group_by_field and not is_last_group_by_field and size:
            term_aggregation["size"] = size
            # populate_sort_order_list(term_aggregation, pageable, current_group_by_field, True, is_cardinality)

        if is_last_group_by_field:
            return {"cardinality": {"field": field}}
    else:
        if is_first_group_by_field and size:
            term_aggregation["size"] = size
        # populate_sort_order_list(term_aggregation, pageable, current_group_by_field, is_first_group_by_field, is_cardinality)

    return {"terms": term_aggregation}


def get_aggregation_builder_with_date_histogram(interval, is_admin_audits) -> Dict[str, Any]:
    # Placeholder for your logic to build date histogram aggregation
    # return date_histogram(field="timestamp", interval=interval)

    aggregation = {
        "date_histogram": {
            "field": "logTime" if is_admin_audits else "eventTime",
            "interval": interval
        }
    }
    return aggregation


# Method to build the search request with aggregations
def build_search_request_with_aggregations(group_by, interval, size, cardinality, is_admin_audits, search_request: Dict[str, Any]):
    updated_search_request = copy.deepcopy(search_request)
    if group_by:
        group_by_list = get_list_from_comma_separated_string(group_by)
        if group_by_list:
            # Get group by aggregation
            group_by_aggregation = get_group_by_aggregation(group_by_list, size, cardinality, is_admin_audits)
            aggregation = {}
            if interval:
                # Get date histogram aggregation builder
                aggregation_builder = get_aggregation_builder_with_date_histogram(interval, is_admin_audits)
                # Add group by aggregation to date histogram aggregation builder
                aggregation_builder["aggs"] = group_by_aggregation
                # Build the aggregation
                aggregation["date_histogram"] = aggregation_builder
            else:
                # Add group by aggregation to aggregation
                aggregation = group_by_aggregation

            # Add aggregation to search request
            updated_search_request["aggs"] = aggregation
    return updated_search_request


def extract_search_response_aggregations(interval, aggregations: Dict[str, Any]) -> Dict[str, Any]:
    if interval:
        return extract_date_histogram_aggregations(interval, aggregations)
    else:
        return extract_group_by_aggregations(aggregations)


def find_nested_structure_with_buckets(data):
    for key, value in data.items():
        if isinstance(value, dict) and "buckets" in value:
            return {key: value}
    return None


def find_nested_value(d: Dict[str, Any]) -> Optional[Any]:
    """
    Recursively searches for nested dictionaries containing a key 'value' and returns its value.

    Args:
    d (Dict[str, Any]): The dictionary to search in.

    Returns:
    Optional[Any]: The value associated with the key 'value', if found. None otherwise.
    """
    for key, value in d.items():
        if isinstance(value, dict):  # Check if the value is a dictionary
            if 'value' in value:  # Check if the dictionary has a key 'value'
                return {key: {"count": value["value"]}}
            else:  # Recursively search in the nested dictionary
                nested_value = find_nested_value(value)
                if nested_value is not None:
                    return nested_value
    return None


def extract_date_histogram_aggregations(interval: str, aggregations: Dict[str, Any]) -> Dict[str, Any]:
    aggregation_entry = next(iter(aggregations.items()), None)
    if not aggregation_entry:
        return {}

    aggregation_result = aggregation_entry[1]
    shield_aggregation_result = defaultdict(dict)

    for bucket in aggregation_result["buckets"]:
        bucket_result = {}
        aggregations = find_nested_structure_with_buckets(bucket)
        if aggregations:
            bucket_result.update(extract_group_by_aggregations(aggregations))
        shield_aggregation_result[bucket["key"]] = bucket_result

    return {interval: shield_aggregation_result}


def extract_group_by_aggregations(aggregations: Dict[str, Any]) -> Dict[str, Any]:
    if not aggregations:
        return {}

    aggregation = next(iter(aggregations.items()), None)
    if not aggregation:
        return {}

    shield_aggregation_result = defaultdict(dict)
    aggregate = aggregation[1]

    if 'buckets' in aggregate:
        for bucket in aggregate['buckets']:
            populate_shield_aggregation_result(shield_aggregation_result, bucket)
    elif 'value' in aggregate:
        shield_aggregation_result['count'] = aggregate['value']

    return {aggregation[0]: shield_aggregation_result}


def populate_shield_aggregation_result(shield_aggregation_result: Dict[str, Any], bucket: Dict[str, Any]):
    bucket_result = {"count": bucket.get("doc_count", 0)}

    aggregations = find_nested_structure_with_buckets(bucket)
    if aggregations:
        bucket_result.update(extract_group_by_aggregations(aggregations))
    else:
        value = find_nested_value(bucket)
        if value:
            bucket_result.update(value)

    shield_aggregation_result[bucket["key"]] = bucket_result