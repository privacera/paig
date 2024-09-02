from pydantic import BaseModel
from typing import List, Optional
from core.factory.database_initiator import BaseAPIFilter
from pydantic import Field, ConfigDict
from fastapi import Query


class BaseAccessAuditView(BaseModel):
    app_key: Optional[str] = Field(None, description="The Application key", alias="applicationKey")
    app_name: Optional[str] = Field(None, description="The Application name", alias="applicationName")
    client_app_key: Optional[str] = Field(None, description="The Client Application key", alias="clientApplicationKey")
    client_app_name: Optional[str] = Field(None, description="The Client Application name",
                                           alias="clientApplicationName")
    client_host_name: Optional[str] = Field(None, description="The Client Host name", alias="clientHostname")
    client_ip: Optional[str] = Field(None, description="The Client IP", alias="clientIp")
    context: Optional[dict] = Field({}, description="The context of the audit")
    event_id: Optional[str] = Field(None, description="The Event ID", alias="eventId")
    event_time: Optional[int] = Field(None, description="The Event time", alias="eventTime")
    masked_traits: Optional[dict] = Field({}, description="The masked traits", alias="maskedTraits")
    messages: Optional[List[dict]] = Field([], description="The messages")
    number_of_tokens: Optional[int] = Field(None, description="The number of tokens", alias="numberOfTokens")
    paig_policy_ids: Optional[List[int]] = Field([], description="The Paige policy IDs", alias="paigPolicyIds")
    request_id: Optional[str] = Field(None, description="The Request ID", alias="requestId")
    request_type: Optional[str] = Field(None, description="The Request type", alias="requestType")
    result: Optional[str] = Field(None, description="The Result")
    tenant_id: Optional[str] = Field(None, description="The Tenant ID", alias="tenantId")
    thread_id: Optional[str] = Field(None, description="The Thread ID", alias="threadId")
    thread_sequence_number: Optional[int] = Field(None, description="The Thread sequence number",
                                                  alias="threadSequenceNumber")
    traits: Optional[List[str]] = Field([], description="The traits")
    user_id: Optional[str] = Field(None, description="The User ID", alias="userId")
    encryption_key_id: Optional[int] = Field(None, description="The Encryption key ID", alias="encryptionKeyId")
    log_time: Optional[int] = Field(None, description="The Log time", alias="logTime")
    transaction_sequence_number: Optional[int] = Field(None, description="The Transaction sequence number",
                                                       alias="transactionSequenceNumber")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class QueryParamsBase(BaseAPIFilter):
    user_id: Optional[str] = Field(None, description="The User ID", alias="userId")
    app_name: Optional[str] = Field(None, description="The Application name", alias="applicationName")
    result: Optional[str] = Field(None, description="The Result", alias="result")
    request_type: Optional[str] = Field(None, description="The Request type", alias="requestType")
    traits: Optional[str] = Field(None, description="The trait", alias="traits")


class IncludeQueryParams(QueryParamsBase):
    thread_id: Optional[str] = Field(None, description="The Thread ID", alias="threadId")
    transaction_sequence_number: Optional[str] = Field(None, description="The Transaction sequence number", alias="transactionSequenceNumber")
    transaction_id: Optional[str] = Field(None, description="The Transaction ID", alias="transactionId")
    object_type: Optional[str] = Field(None, description="The Object type", alias="objectType")
    action: Optional[str] = Field(None, description="The Action", alias="action")


def include_query_params(
        include_query_user_id: Optional[str] = Query(None, alias="includeQuery.userId"),
        include_query_application_name: Optional[str] = Query(None, alias="includeQuery.applicationName"),
        include_query_request_type: Optional[str] = Query(None, alias="includeQuery.requestType"),
        include_query_traits: Optional[str] = Query(None, alias="includeQuery.trait"),
        include_query_result: Optional[str] = Query(None, alias="includeQuery.result"),
        include_query_thread_id: Optional[str] = Query(None, alias="includeQuery.threadId"),
        include_query_transaction_sequence_number: Optional[str] = Query(None,
                                                                         alias="includeQuery.transactionSequenceNumber"),
        include_query_transaction_id: Optional[str] = Query(None, alias="includeQuery.transactionId"),
        include_query_object_type: Optional[str] = Query(None, alias="includeQuery.objectType"),
        include_query_action: Optional[str] = Query(None, alias="includeQuery.action")
) -> IncludeQueryParams:
    return IncludeQueryParams(
        userId=include_query_user_id,
        applicationName=include_query_application_name,
        requestType=include_query_request_type,
        trait=include_query_traits,
        result=include_query_result,
        threadId=include_query_thread_id,
        transactionSequenceNumber=include_query_transaction_sequence_number,
        transactionId=include_query_transaction_id,
        objectType=include_query_object_type,
        action=include_query_action
    )


def exclude_query_params(
        exclude_query_user_id: Optional[str] = Query(None, alias="excludeQuery.userId"),
        exclude_query_application_name: Optional[str] = Query(None, alias="excludeQuery.applicationName"),
        exclude_query_request_type: Optional[str] = Query(None, alias="excludeQuery.requestType"),
        exclude_query_traits: Optional[str] = Query(None, alias="excludeQuery.trait"),
        exclude_query_result: Optional[str] = Query(None, alias="excludeQuery.result")
) -> QueryParamsBase:
    return QueryParamsBase(
        userId=exclude_query_user_id,
        applicationName=exclude_query_application_name,
        requestType=exclude_query_request_type,
        trait=exclude_query_traits,
        result=exclude_query_result
    )


def extract_include_query_params(params):
    params_dict = params.model_dump(exclude=BaseAPIFilter.model_fields.keys(), by_alias=False, exclude_none=True)

    # Extract only the required fields
    filtered_params = {params.model_fields[field].alias: value for field, value in params_dict.items() if
                       value is not None}

    return filtered_params
