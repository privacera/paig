
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_IN_USE, ERROR_RESOURCE_NOT_FOUND
from api.governance.api_schemas.ai_app_config import AIApplicationConfigFilter
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyFilter
from api.governance.api_schemas.metadata_key import MetadataKeyFilter
from api.governance.api_schemas.metadata_value import MetadataValueFilter
from api.governance.api_schemas.tag import TagFilter
from api.governance.api_schemas.vector_db_policy import VectorDBPolicyFilter, VectorDBPolicyView
from api.governance.services.ai_app_config_service import AIAppConfigService
from api.governance.services.ai_app_policy_service import AIAppPolicyService
from api.governance.services.metadata_value_service import MetadataValueService
from api.governance.services.metadata_key_service import MetadataKeyService
from api.governance.services.tag_service import TagService
from api.governance.services.vector_db_policy_service import VectorDBPolicyService
from core.utils import SingletonDepends


class GovServiceValidationUtil:

    def __init__(
            self,
            ai_app_config_service: AIAppConfigService = SingletonDepends(AIAppConfigService),
            ai_app_policy_service: AIAppPolicyService = SingletonDepends(AIAppPolicyService),
            vector_db_policy_service: VectorDBPolicyService = SingletonDepends(VectorDBPolicyService),
            tag_service: TagService = SingletonDepends(TagService),
            meta_data_service: MetadataKeyService = SingletonDepends(MetadataKeyService),
            meta_data_attr_service: MetadataValueService = SingletonDepends(MetadataValueService)):
        self.ai_app_config_service = ai_app_config_service
        self.ai_app_policy_service = ai_app_policy_service
        self.vector_db_policy_service = vector_db_policy_service
        self.tag_service = tag_service
        self.meta_data_service = meta_data_service
        self.meta_data_attr_service = meta_data_attr_service

    async def validate_entity_is_not_utilized(self, entity_name: str, entity_type: str = "User"):
        ai_app_config_filter = AIApplicationConfigFilter()
        if entity_type == "User":
            ai_app_config_filter.user = entity_name
        elif entity_type == "Group":
            ai_app_config_filter.group = entity_name
        ai_app_config_filter.exact_match = True
        ai_app_configs = await self.ai_app_config_service.list_ai_app_configs(ai_app_config_filter, 0, 10, [])
        if ai_app_configs.totalElements > 0:
            application_ids = [app_config.application_id for app_config in ai_app_configs.content]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, entity_type, "AI Application with Id", list(set(application_ids))))

        ai_app_policy_filter = AIApplicationPolicyFilter()
        if entity_type == "User":
            ai_app_policy_filter.users = entity_name
        elif entity_type == "Group":
            ai_app_policy_filter.groups = entity_name
        ai_app_policy_filter.exact_match = True
        ai_app_policies = await self.ai_app_policy_service.list_ai_application_policies(ai_app_policy_filter, 0, 10, [])
        if ai_app_policies.totalElements > 0:
            application_ids = [policy.application_id for policy in ai_app_policies.content]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, entity_type, "AI Application with Id", list(set(application_ids))))

        vector_db_policy_filter = VectorDBPolicyFilter()
        if entity_type == "User":
            vector_db_policy_filter.user = entity_name
        elif entity_type == "Group":
            vector_db_policy_filter.group = entity_name
        vector_db_policy_filter.exact_match = True
        vector_db_policies = await self.vector_db_policy_service.list_vector_db_policies(vector_db_policy_filter, 0, 10,
                                                                                    [])
        if vector_db_policies.totalElements > 0:
            vector_db_ids = [policy.vector_db_id for policy in vector_db_policies.content]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, entity_type, "Vector DB with Id", list(set(vector_db_ids))))

    async def validate_tag_exists(self, tags: list[str]):
        """
        Validates Tags exists in governance service

        Args:
            tags: The Tas to validate
        """
        if not tags:
            return
        tag_filter = TagFilter()
        tag_filter.name = ",".join(tags)
        existing_tags = set()
        page_number = 0
        page_size = 100
        while True:
            result = await self.tag_service.list_tags(filter=tag_filter,
                                                      page_number=page_number, size=page_size, sort=[])
            existing_tags.update(data.name for data in result.content)
            if result.last:
                break
            page_number += 1
        missing_tags = set(tags) - existing_tags
        if missing_tags:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "Tag", "names", list(missing_tags)))

    async def validate_metadata_exists(self, request: VectorDBPolicyView):
        """
        Validates metadata exists in governance service

        Args:
            request: The request object containing metadata key and value
        """
        metadata_filter = MetadataKeyFilter()
        metadata_filter.name = request.metadata_key
        metadata = await self.meta_data_service.list_metadata(filter=metadata_filter, page_number=0, size=1, sort=[])
        if not metadata.totalElements:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB policy MetaData", "key", [request.metadata_key]))

        metadata_attr_filter = MetadataValueFilter()
        metadata_attr_filter.metadata_id = metadata.content[0].id
        metadata_attr_filter.metadata_value = request.metadata_value
        metadata_attrs = await self.meta_data_attr_service.list_metadata_values(filter=metadata_attr_filter, page_number=0,
                                                                                size=1, sort=[])
        if not metadata_attrs.totalElements:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB policy MetaData attribute", "value",
                                  [request.metadata_value]))

    async def validate_metadata_is_not_utilized(self, metadata_key: str):
        policy_filter = VectorDBPolicyFilter()
        policy_filter.metadata_key = metadata_key
        policy_filter.exact_match = True
        vector_db_policy = await self.vector_db_policy_service.list_vector_db_policies(policy_filter, 0, 10, [])
        if vector_db_policy.totalElements > 0:
            policy_ids = [policy.id for policy in vector_db_policy.content]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, "Metadata", "Vector DB Policy with Id", policy_ids))

    async def validate_metadata_value_not_utilized(self, metadata_key: str, metadata_value: str):
        policy_filter = VectorDBPolicyFilter()
        policy_filter.metadata_key = metadata_key
        policy_filter.metadata_value = metadata_value
        policy_filter.exact_match = True
        vector_db_policy = await self.vector_db_policy_service.list_vector_db_policies(policy_filter, 0, 1, [])
        if vector_db_policy.numberOfElements > 0:
            policy_ids = [policy.id for policy in vector_db_policy.content]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, "Metadata attribute value", "Vector DB Policy with Id", policy_ids))

    async def validate_tag_not_utilized(self, tag: str):
        policy_filter = AIApplicationPolicyFilter()
        policy_filter.tags = tag
        policy_filter.exact_match = True
        ai_app_policy = await self.ai_app_policy_service.list_ai_application_policies(policy_filter, 0, 10, [])
        if ai_app_policy.totalElements > 0:
            policy_ids = [policy.id for policy in ai_app_policy.content]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, "Tag", "AI Application Policy with Id", policy_ids))