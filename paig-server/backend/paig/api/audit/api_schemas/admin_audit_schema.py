from pydantic import BaseModel
from typing import Optional
from core.factory.database_initiator import BaseAPIFilter
from pydantic import Field, ConfigDict
from fastapi import Query


class BaseAdminAuditView(BaseModel):

    acted_by_user_id: Optional[str] = Field(None, description="The acted by user ID", alias="actedByUserId")
    acted_by_user_name: Optional[str] = Field(None, description="The acted by user name", alias="actedByUsername")
    action: Optional[str] = Field(None, description="The Action performed CREATE/UPDATE/DELETE")
    log_id: Optional[str] = Field(None, description="The Admin audit log ID", alias="logId")
    log_time: Optional[int] = Field(None, description="The Admin audit log time", alias="logTime")
    object_id: Optional[int] = Field(None, description="The Object ID", alias="objectId")
    object_name: Optional[str] = Field(None, description="The Object name", alias="objectName")
    object_type: Optional[str] = Field(None, description="The Object type", alias="objectType")
    object_state: Optional[dict] = Field(None, description="The Object state", alias="objectState")
    object_state_previous: Optional[dict] = Field(None, description="The Object state previous", alias="objectStatePrevious")
    tenant_id: Optional[str] = Field(None, description="The Tenant ID", alias="tenantId")
    transaction_id: Optional[str] = Field(None, description="The Transaction ID", alias="transactionId")
    transaction_sequence_number: Optional[int] = Field(None, description="The Transaction sequence number",
                                                       alias="transactionSequenceNumber")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class QueryParamsBase(BaseAPIFilter):
    acted_by_user_id: Optional[str] = Field(None, description="The acted by User ID", alias="actedByUserId")
    acted_by_user_name: Optional[str] = Field(None, description="The acted by User name", alias="actedByUsername")
    action: Optional[str] = Field(None, description="The Action", alias="action")
    log_id: Optional[str] = Field(None, description="The Admin audit log ID", alias="logId")
    log_time: Optional[int] = Field(None, description="The Admin audit log time", alias="logTime")
    object_id: Optional[int] = Field(None, description="The Object ID", alias="objectId")
    object_type: Optional[str] = Field(None, description="The Object type", alias="objectType")
    object_name: Optional[str] = Field(None, description="The Object name", alias="objectName")
    transaction_id: Optional[str] = Field(None, description="The Transaction ID", alias="transactionId")
    transaction_sequence_number: Optional[str] = Field(None, description="The Transaction sequence number",
                                                       alias="transactionSequenceNumber")


def include_query_params(
        include_query_acted_by_user_id: Optional[str] = Query(None, alias="includeQuery.actedByUserId"),
        include_query_acted_by_user_name: Optional[str] = Query(None, alias="includeQuery.actedByUsername"),
        include_query_action: Optional[str] = Query(None, alias="includeQuery.action"),
        include_query_log_id: Optional[str] = Query(None, alias="includeQuery.logId"),
        include_query_log_time: Optional[int] = Query(None, alias="includeQuery.logTime"),
        include_query_object_id: Optional[int] = Query(None, alias="includeQuery.objectId"),
        include_query_object_type: Optional[str] = Query(None, alias="includeQuery.objectType"),
        include_query_object_name: Optional[str] = Query(None, alias="includeQuery.objectName"),
        include_query_tenant_id: Optional[str] = Query(None, alias="includeQuery.tenantId"),
        include_query_transaction_id: Optional[str] = Query(None, alias="includeQuery.transactionId"),
        include_query_transaction_sequence_number: Optional[str] = Query(None, alias="includeQuery.transactionSequenceNumber")
) -> QueryParamsBase:
    return QueryParamsBase(
        actedByUserId=include_query_acted_by_user_id,
        actedByUsername=include_query_acted_by_user_name,
        action=include_query_action,
        logId=include_query_log_id,
        logTime=include_query_log_time,
        objectId=include_query_object_id,
        objectType=include_query_object_type,
        objectName=include_query_object_name,
        tenant_id=include_query_tenant_id,
        transactionId=include_query_transaction_id,
        transactionSequenceNumber=include_query_transaction_sequence_number
    )


def exclude_query_params(
        exclude_query_acted_by_user_id: Optional[str] = Query(None, alias="excludeQuery.actedByUserId"),
        exclude_query_acted_by_user_name: Optional[str] = Query(None, alias="excludeQuery.actedByUsername"),
        exclude_query_action: Optional[str] = Query(None, alias="excludeQuery.action"),
        exclude_query_log_id: Optional[str] = Query(None, alias="excludeQuery.logId"),
        exclude_query_log_time: Optional[int] = Query(None, alias="excludeQuery.logTime"),
        exclude_query_object_id: Optional[int] = Query(None, alias="excludeQuery.objectId"),
        exclude_query_object_type: Optional[str] = Query(None, alias="excludeQuery.objectType"),
        exclude_query_object_name: Optional[str] = Query(None, alias="excludeQuery.objectName"),
        exclude_query_tenant_id: Optional[str] = Query(None, alias="excludeQuery.tenantId"),
        exclude_query_transaction_id: Optional[str] = Query(None, alias="excludeQuery.transactionId"),
        exclude_query_transaction_sequence_number: Optional[str] = Query(None, alias="excludeQuery.transactionSequenceNumber")
) -> QueryParamsBase:
    return QueryParamsBase(
        actedByUserId=exclude_query_acted_by_user_id,
        actedByUsername=exclude_query_acted_by_user_name,
        action=exclude_query_action,
        logId=exclude_query_log_id,
        logTime=exclude_query_log_time,
        objectId=exclude_query_object_id,
        objectType=exclude_query_object_type,
        objectName=exclude_query_object_name,
        tenantId=exclude_query_tenant_id,
        transactionId=exclude_query_transaction_id,
        transactionSequenceNumber=exclude_query_transaction_sequence_number
    )


def extract_include_query_params(params):
    params_dict = params.model_dump(exclude=BaseAPIFilter.model_fields.keys(), by_alias=False, exclude_none=True)

    # Extract only the required fields
    filtered_params = {params.model_fields[field].alias: value for field, value in params_dict.items() if
                       value is not None}

    return filtered_params
