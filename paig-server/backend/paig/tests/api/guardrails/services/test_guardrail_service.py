import copy
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.encryption.api_schemas.encryption_key import EncryptionKeyView
from api.guardrails.api_schemas.gr_connection import GRConnectionView
from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GRConfigView
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails import GuardrailProvider
from api.guardrails.database.db_models.guardrail_model import GRApplicationVersionModel, GuardrailModel, \
    GRVersionHistoryModel
from api.guardrails.database.db_operations.guardrail_repository import GuardrailRepository, \
    GRApplicationVersionRepository, GRVersionHistoryRepository
from api.guardrails.providers import GuardrailProviderManager
from api.guardrails.services.gr_connections_service import GRConnectionService
from api.guardrails.services.guardrails_service import GuardrailRequestValidator, GuardrailService
from core.exceptions import BadRequestException, NotFoundException, InternalServerError

guardrail_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "mock_guardrail",
    "description": "mock description",
    "version": 1,
    "guardrailConnectionName": "gr_connection_1",
    "guardrailProvider": "AWS"
}

guardrail_config_json = {
    "configType": "CONTENT_MODERATION",
    "configData": {
        "configs": [
            {
                "category": "VIOLENCE",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            },
            {
                "category": "MISCONDUCT",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            },
            {
                "category": "HATE",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "low"
            },
            {
                "category": "SEXUAL",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            },
            {
                "category": "INSULTS",
                "filterStrengthPrompt": "high",
                "filterStrengthResponse": "medium"
            }
        ]
    },
    "responseMessage": "I couldn't respond to that message."
}

guardrail_config_json2 = {
    "configType": "DENIED_TERMS",
    "configData": {
        "configs": [
            {
                "type": "PROFANITY",
                "value": True
            },
            {
                "term": "Violance",
                "keywords": [
                    "Violent Bahaviour",
                    "Physical Assault"
                ]
            }
        ]
    },
    "responseMessage": "I couldn't respond to that message."
}

guardrail_config_json3 = {
    "configType": "OFF_TOPIC",
    "responseMessage": "I couldn't respond to that message.",
    "configData": {
        "configs": [
            {
                "topic": "Sports",
                "definition": "Sports Definition",
                "samplePhrases": [
                    "Who's playing NFL tonight ?",
                    "Who's leading tonight ?"
                ],
                "action": "DENY"
            }
        ]
    }
}

gr_connection_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "gr_connection_1",
    "description": "test description1",
    "guardrailsProvider": "AWS",
    "connectionDetails": {
        "access_key": "mock_access_key",
        "secret_key": "mock_secret_key",
        "session_token": "mock_session_token"
    }
}

gr_connection_view = GRConnectionView(**gr_connection_view_json)

gr_config_view = GRConfigView(**guardrail_config_json)

guardrail_view = GuardrailView(**guardrail_view_json)


@pytest.fixture
def mock_guardrail_repository():
    return AsyncMock(spec=GuardrailRepository)


@pytest.fixture
def mock_guardrail_version_history_repository():
    return AsyncMock(spec=GRVersionHistoryRepository)


@pytest.fixture
def mock_guardrail_app_version_repository():
    return AsyncMock(spec=GRApplicationVersionRepository)


@pytest.fixture
def mock_guardrail_connection_service():
    return AsyncMock(spec=GRConnectionService)


@pytest.fixture
def guardrail_request_validator(mock_guardrail_repository):
    return GuardrailRequestValidator(guardrail_repository=mock_guardrail_repository)


@pytest.fixture
def guardrail_service(mock_guardrail_repository, mock_guardrail_version_history_repository,
                      mock_guardrail_app_version_repository, guardrail_request_validator,
                      mock_guardrail_connection_service):
    return GuardrailService(
        guardrail_repository=mock_guardrail_repository,
        gr_version_history_repository=mock_guardrail_version_history_repository,
        gr_app_version_repository=mock_guardrail_app_version_repository,
        guardrail_request_validator=guardrail_request_validator,
        guardrail_connection_service=mock_guardrail_connection_service
    )


@pytest.mark.asyncio
async def test_list_guardrails(guardrail_service, mock_guardrail_repository):
    mock_filter = GuardrailFilter()
    mock_sort = ["create_time"]
    expected_records = [guardrail_view]
    expected_total_count = 100
    # Patch the list_records method on the repository
    with patch.object(
            mock_guardrail_repository, 'list_records', return_value=(expected_records, expected_total_count)
    ) as mock_list_records:
        # Call the method under test
        result = await guardrail_service.list(filter=mock_filter, page_number=1, size=10, sort=mock_sort)

        # Assertions
        mock_list_records.assert_called_once_with(filter=mock_filter, page_number=1, size=10, sort=mock_sort)
        assert result.content == expected_records
        assert result.totalElements == expected_total_count


@pytest.mark.asyncio
async def test_create_guardrail(guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
                                mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_configs = [gr_config_view]
    create_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(create_guardrail_view.model_dump())

    gr_version_history_model = GRVersionHistoryModel(id=1, guardrail_id=1, version=1)
    gr_connection_model = GRConnectionModel(**gr_connection_view.model_dump(exclude={"encrypt_fields"}))
    gr_app_versions = [GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_model
    ) as mock_guardrail_create_record, patch.object(
            mock_guardrail_repository, 'update_record', return_value=guardrail_model
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_version_history_repository, 'create_record', return_value=gr_version_history_model
    ) as mock_gr_version_history_create_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=gr_app_versions
    ) as mock_gr_version_history_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_model]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        result = await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == create_guardrail_view.name
        assert result.guardrail_configs == create_guardrail_view.guardrail_configs
        assert result.application_keys == create_guardrail_view.application_keys
        assert result.guardrail_provider == create_guardrail_view.guardrail_provider
        assert result.guardrail_connection_name == create_guardrail_view.guardrail_connection_name
        assert mock_guardrail_create_record.called
        assert mock_guardrail_update_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_create_record.called
        assert mock_gr_version_history_get_all.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called


@pytest.mark.asyncio
async def test_create_guardrail_when_guardrail_connection_name_provided_without_guardrail_provider(guardrail_service, mock_guardrail_repository):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_configs = [gr_config_view]
    create_guardrail_view.guardrail_provider = None
    # Call the method under test
    with pytest.raises(BadRequestException) as exc_info:
        await guardrail_service.create(create_guardrail_view)

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Guardrail Provider must be provided"
    assert not mock_guardrail_repository.create_record.called


@pytest.mark.asyncio
async def test_create_guardrail_when_guardrail_connection_name_not_provided(guardrail_service, mock_guardrail_repository):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_configs = [gr_config_view]
    create_guardrail_view.guardrail_connection_name = None
    # Call the method under test
    with pytest.raises(BadRequestException) as exc_info:
        await guardrail_service.create(create_guardrail_view)

    # Assertions
    assert exc_info.type == BadRequestException
    assert exc_info.value.message == "Guardrail Connection Name must be provided"
    assert not mock_guardrail_repository.create_record.called


@pytest.mark.asyncio
async def test_create_guardrail_when_name_already_exists(guardrail_service, mock_guardrail_repository):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_configs = [gr_config_view]
    with patch.object(
            mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail already exists with name: ['mock_guardrail']"
        assert mock_get_by_name.called
        assert not mock_guardrail_repository.create_record.called


@pytest.mark.asyncio
async def test_create_guardrail_when_config_not_provided(guardrail_service, mock_guardrail_repository):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_connections = {"AWS": {"connectionName": "mock_connection_name"}}
    create_guardrail_view.guardrail_configs = []
    with patch.object(
            mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail Configurations must be provided"
        assert not mock_get_by_name.called
        assert not mock_guardrail_repository.create_record.called


@pytest.mark.asyncio
async def test_create_guardrail_when_multiple_guardrail_config_with_same_type_provided(
        guardrail_service, mock_guardrail_repository):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_config_2 = GRConfigView(**guardrail_config_json2)
    create_guardrail_view.guardrail_configs = [gr_config_2, gr_config_2]

    with patch.object(
            mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Multiple Guardrail configurations of same type ['DENIED_TERMS'] not allowed"
        assert not mock_get_by_name.called
        assert not mock_guardrail_repository.create_record.called


@pytest.mark.asyncio
async def test_create_guardrail_when_invalid_connection_name_provided(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_view.guardrail_connection_name = "INVALID_CONNECTION"

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]
    create_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[]
    ) as mock_gr_version_history_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_get_all.called
        assert mock_gr_connection_get_all.called
        assert not mock_bedrock_guardrail_create.called
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail Connection not found with name: ['INVALID_CONNECTION']"


@pytest.mark.asyncio
async def test_create_guardrail_when_guardrail_provider_gives_error(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_view.guardrail_connections = {"AWS": {"connectionName": "mock_connection_name"}}

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]
    create_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[]
    ) as mock_gr_version_history_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[GRConnectionModel(**gr_connection_view.model_dump(exclude={"encrypt_fields"}))]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', side_effect=InternalServerError("AWS Error")
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_get_all.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to create guardrails. Error - AWS Error"


@pytest.mark.asyncio
async def test_create_guardrail_when_guardrail_provider_does_not_give_success_as_token_expired(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_view.guardrail_connections = {"AWS": {"connectionName": "mock_connection_name"}}

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]
    create_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[]
    ) as mock_gr_version_history_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[GRConnectionModel(**gr_connection_view.model_dump(exclude={"encrypt_fields"}))]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": False, "response": {"details": {"errorType": "ClientError", "details": "AWS Error ExpiredTokenException"}}}}
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_get_all.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to create guardrail in AWS: The security token included in the connection is expired"


@pytest.mark.asyncio
async def test_get_guardrail_by_id(guardrail_service, mock_guardrail_repository):
    guardrail_view_data = GuardrailView(**guardrail_view_json)
    gr_config_view_data = GRConfigView(**guardrail_config_json)
    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(guardrail_view_data.model_dump())
    guardrail_model.guardrail_configs = [gr_config_view_data.model_dump()]
    guardrail_model.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_model.guardrail_id = 1
    with patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_guardrail_get_record_by_id:
        # Call the method under test
        result = await guardrail_service.get_by_id(1, False)

        # Assertions
        mock_guardrail_get_record_by_id.assert_called()
        assert result.id == 1
        assert result.name == guardrail_view_data.name
        assert result.application_keys == guardrail_model.application_keys
        assert result.guardrail_configs[0].config_type == gr_config_view_data.config_type
        assert result.guardrail_configs[0].config_data == gr_config_view_data.config_data


@pytest.mark.asyncio
async def test_get_guardrail_by_id_when_extended_true_provided(guardrail_service, mock_guardrail_repository,
                                                               mock_guardrail_connection_service):
    guardrail_view_data = GuardrailView(**guardrail_view_json)
    gr_config_view_data = GRConfigView(**guardrail_config_json)
    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(guardrail_view_data.model_dump())
    guardrail_model.guardrail_configs = [gr_config_view_data.model_dump()]
    guardrail_model.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_model.guardrail_id = 1

    mock_encryption_key = EncryptionKeyView(id=3)
    gr_connection_details = copy.deepcopy(gr_connection_view.connection_details)
    gr_connection_details["encryption_key_id"] = 3
    with patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_guardrail_get_record_by_id, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        mock_guardrail_connection_service, 'get_encryption_key', return_value=mock_encryption_key
    ) as mock_gr_connection_get_encryption_key:
        # Call the method under test
        result = await guardrail_service.get_by_id(1, True)

        # Assertions
        mock_guardrail_get_record_by_id.assert_called()
        mock_gr_connection_get_all.assert_called_once()
        mock_gr_connection_get_encryption_key.assert_called_once()
        assert result.id == 1
        assert result.name == guardrail_view_data.name
        assert result.application_keys == guardrail_model.application_keys
        assert result.guardrail_configs[0].config_type == gr_config_view_data.config_type
        assert result.guardrail_configs[0].config_data == gr_config_view_data.config_data
        assert result.guardrail_connection_details == gr_connection_details


@pytest.mark.asyncio
async def test_get_guardrail_by_app_key(guardrail_service, mock_guardrail_repository,
                                        mock_guardrail_connection_service):
    guardrail_view_data = GuardrailView(**guardrail_view_json)
    gr_config_view_data = GRConfigView(**guardrail_config_json)

    gr_view_model = GuardrailModel()
    gr_view_model.set_attribute(guardrail_view_data.model_dump())
    gr_view_model.guardrail_configs = [gr_config_view_data.model_dump()]
    gr_view_model.application_keys = ["mock_app_key1", "mock_app_key2"]
    gr_view_model.guardrail_id = 1

    mock_encryption_key = EncryptionKeyView(id=3)
    gr_connection_details = copy.deepcopy(gr_connection_view.connection_details)
    gr_connection_details["encryption_key_id"] = 3

    with patch.object(
            mock_guardrail_repository, 'get_all', return_value=[gr_view_model]
    ) as mock_guardrail_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        mock_guardrail_connection_service, 'get_encryption_key', return_value=mock_encryption_key
    ) as mock_gr_connection_get_encryption_key:
        # Call the method under test
        result = await guardrail_service.get_all_by_app_key("mock_app_key1", 0)

        # Assertions
        mock_guardrail_get_all.assert_called_once_with(filters={"application_keys": "mock_app_key1"})
        mock_gr_connection_get_all.assert_called_once()
        mock_gr_connection_get_encryption_key.assert_called_once()
        assert result.app_key == "mock_app_key1"
        assert result.version == 1
        assert result.guardrails[0].id == 1
        assert result.guardrails[0].name == guardrail_view_data.name
        assert result.guardrails[0].guardrail_provider == guardrail_view_data.guardrail_provider
        assert result.guardrails[0].guardrail_connection_name == guardrail_view_data.guardrail_connection_name
        assert result.guardrails[0].guardrail_configs[0].config_type == gr_config_view_data.config_type
        assert result.guardrails[0].guardrail_configs[0].config_data == gr_config_view_data.config_data
        assert result.guardrails[0].guardrail_configs[0].response_message == gr_config_view_data.response_message
        assert result.guardrails[0].guardrail_connection_details == gr_connection_details


@pytest.mark.asyncio
async def test_get_guardrail_by_app_key_when_cache_does_not_have_app_version(
        guardrail_service, mock_guardrail_repository, mock_guardrail_connection_service):
    guardrail_view_data = GuardrailView(**guardrail_view_json)
    gr_config_view_data = GRConfigView(**guardrail_config_json)

    gr_view_model = GuardrailModel()
    gr_view_model.set_attribute(guardrail_view_data.model_dump())
    gr_view_model.guardrail_configs = [gr_config_view_data.model_dump()]
    gr_view_model.application_keys = ["mock_app_key3"]
    gr_view_model.guardrail_id = 1

    with patch.object(
        mock_guardrail_repository, 'get_all', return_value=[gr_view_model]
    ) as mock_guardrail_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all:
        # Call the method under test
        result = await guardrail_service.get_all_by_app_key("mock_app_key3", 0)

        # Assertions
        mock_guardrail_get_all.assert_called_once_with(filters={"application_keys": "mock_app_key3"})
        mock_gr_connection_get_all.assert_called_once()
        assert result.app_key == "mock_app_key3"
        assert result.version == 1
        assert result.guardrails[0].id == 1
        assert result.guardrails[0].name == guardrail_view_data.name
        assert result.guardrails[0].guardrail_provider == guardrail_view_data.guardrail_provider
        assert result.guardrails[0].guardrail_connection_name == guardrail_view_data.guardrail_connection_name
        assert result.guardrails[0].guardrail_configs[0].config_type == gr_config_view_data.config_type
        assert result.guardrails[0].guardrail_configs[0].config_data == gr_config_view_data.config_data
        assert result.guardrails[0].guardrail_configs[0].response_message == gr_config_view_data.response_message
        assert result.guardrails[0].guardrail_connection_details == gr_connection_view.connection_details


@pytest.mark.asyncio
async def test_get_guardrail_by_app_key_with_last_known_version_same_as_cached_version(guardrail_service):
    result = await guardrail_service.get_all_by_app_key("mock_app_key1", 1)
    assert result.app_key == "mock_app_key1"
    assert result.version == 1
    assert result.guardrails is None


@pytest.mark.asyncio
async def test_get_guardrail_by_app_key_when_not_found(guardrail_service, mock_guardrail_repository):
    with patch.object(
            mock_guardrail_repository, 'get_all', return_value=[]
    ) as mock_guardrail_get_all:
        # Call the method under test
        with pytest.raises(NotFoundException) as exc_info:
            await guardrail_service.get_all_by_app_key("mock_app_key1", 0)

        # Assertions
        mock_guardrail_get_all.assert_called_once_with(filters={"application_keys": "mock_app_key1"})
        assert exc_info.type == NotFoundException
        assert exc_info.value.message == "Guardrail not found with application key: ['mock_app_key1']"


@pytest.mark.asyncio
async def test_get_guardrail_by_id_when_not_found(guardrail_service, mock_guardrail_repository):
    with patch.object(
            mock_guardrail_repository, 'get_record_by_id', side_effect=NoResultFound
    ) as mock_get_record_by_id:
        # Call the method under test
        with pytest.raises(NotFoundException) as exc_info:
            await guardrail_service.get_by_id(1, False)

        # Assertions
        mock_get_record_by_id.assert_called_once_with(1)
        assert exc_info.type == NotFoundException
        assert exc_info.value.message == "Guardrail not found with ID: [1]"


@pytest.mark.asyncio
async def test_update_guardrail(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)

    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)

    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key3"]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())
    guardrail_model.guardrail_configs = [gr_config_view_to_update.model_dump(), gr_config_view_to_delete.model_dump()]

    gr_version_history_model = GRVersionHistoryModel(id=1, guardrail_id=1, version=1)

    gr_app_version_model_to_bump1 = GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)
    gr_app_version_model_to_bump2 = GRApplicationVersionModel(id=2, application_key="mock_app_key2", version=1)
    gr_app_version_model_to_add = GRApplicationVersionModel(id=3, application_key="mock_app_key3", version=1)

    with (patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_repository, 'update_record', return_value=update_guardrail_view
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_version_history_repository, 'create_record', return_value=gr_version_history_model
    ) as mock_gr_version_history_create_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[gr_app_version_model_to_bump1, gr_app_version_model_to_bump2]
    ) as mock_gr_version_history_get_all, patch.object(
        mock_guardrail_app_version_repository, 'create_record', return_value=gr_app_version_model_to_add
    ) as mock_gr_app_version_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'update_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_update):
        # Call the method under test
        result = await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == update_guardrail_view.name
        gr_config_view_to_delete.id = 2
        assert result.guardrail_configs == update_guardrail_view.guardrail_configs
        assert result.application_keys == update_guardrail_view.application_keys
        assert result.guardrail_provider == update_guardrail_view.guardrail_provider
        assert result.guardrail_connection_name == update_guardrail_view.guardrail_connection_name
        assert result.guardrail_connection_details == update_guardrail_view.guardrail_connection_details
        assert result.guardrail_provider_response is None
        assert mock_guardrail_update_record.called
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_create_record.called
        assert mock_gr_version_history_get_all.called
        assert mock_guardrail_app_version_repository.update_record.call_count == 2
        assert mock_gr_app_version_create_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called


@pytest.mark.asyncio
async def test_update_guardrail_when_connection_is_updated(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    update_guardrail_view.application_keys = ["mock_app_key1"]
    gr_conf_view = GRConfigView(**guardrail_config_json)
    update_guardrail_view.guardrail_configs = [gr_conf_view]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())

    update_guardrail_view.guardrail_connection_name = "gr_connection_2"

    gr_version_history_model = GRVersionHistoryModel(id=1, guardrail_id=1, version=1)

    gr_connection_view2 = GRConnectionView(**gr_connection_view_json)
    gr_connection_view2.name = "gr_connection_2"

    gr_app_version_model = GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)

    with (patch.object(
            mock_guardrail_repository, 'update_record', return_value=update_guardrail_view
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_version_history_repository, 'create_record', return_value=gr_version_history_model
    ) as mock_gr_version_history_create_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[gr_app_version_model]
    ) as mock_gr_version_history_get_all, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view, gr_connection_view2]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_create, patch.object(
        GuardrailProviderManager, 'delete_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_delete):
        # Call the method under test
        result = await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == update_guardrail_view.name
        assert result.guardrail_configs == update_guardrail_view.guardrail_configs
        assert result.application_keys == update_guardrail_view.application_keys
        assert result.guardrail_provider == update_guardrail_view.guardrail_provider
        assert result.guardrail_connection_name == update_guardrail_view.guardrail_connection_name
        assert result.guardrail_connection_details == update_guardrail_view.guardrail_connection_details
        assert mock_guardrail_update_record.called
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_create_record.called
        assert mock_gr_version_history_get_all.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert mock_bedrock_guardrail_delete.called


@pytest.mark.asyncio
async def test_update_guardrail_when_name_already_exists(guardrail_service, mock_guardrail_repository):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    update_guardrail_view.guardrail_configs = [gr_config_view]
    update_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    with patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=GuardrailView(id=2, guardrail_connections={"AWS": {"connectionName": "mock_connection_name"}})
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_service.update(2, update_guardrail_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail already exists with name: ['mock_guardrail']"
        assert not mock_guardrail_repository.update_record.called
        assert mock_get_record_by_id.called
        assert mock_get_by_name.called


@pytest.mark.asyncio
async def test_update_guardrail_when_guardrail_provider_gives_error(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)
    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key3"]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())
    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    guardrail_model.guardrail_configs = [gr_config_view_to_update.model_dump(), gr_config_view_to_delete.model_dump()]

    gr_app_version_model_to_bump1 = GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)
    gr_app_version_model_to_bump2 = GRApplicationVersionModel(id=2, application_key="mock_app_key2", version=1)
    gr_app_version_model_to_add = GRApplicationVersionModel(id=3, application_key="mock_app_key3", version=1)

    with (patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[gr_app_version_model_to_bump1, gr_app_version_model_to_bump2]
    ) as mock_gr_app_version_get_all, patch.object(
        mock_guardrail_app_version_repository, 'create_record', return_value=gr_app_version_model_to_add
    ) as mock_gr_app_version_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'update_guardrail', side_effect=InternalServerError("AWS Error")
    ) as mock_bedrock_guardrail_update):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to update guardrails. Error - AWS Error"
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_app_version_get_all.called
        assert mock_gr_app_version_create_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called


@pytest.mark.asyncio
async def test_update_guardrail_when_guardrail_provider_does_not_gives_success_as_access_secret_key_invalid(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_app_version_repository, mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)
    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key3"]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())
    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    guardrail_model.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_delete]

    gr_app_version_model_to_bump1 = GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)
    gr_app_version_model_to_bump2 = GRApplicationVersionModel(id=2, application_key="mock_app_key2", version=1)
    gr_app_version_model_to_add = GRApplicationVersionModel(id=3, application_key="mock_app_key3", version=1)
    with (patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[gr_app_version_model_to_bump1, gr_app_version_model_to_bump2]
    ) as mock_gr_app_version_get_all, patch.object(
        mock_guardrail_app_version_repository, 'create_record', return_value=gr_app_version_model_to_add
    ) as mock_gr_app_version_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'update_guardrail', return_value={"AWS": {"success": False, "response": {"details": {"errorType": "ClientError", "details": "AWS Error UnrecognizedClientException"}}}}
    ) as mock_bedrock_guardrail_update):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to update guardrail in AWS: The associated connection details(AWS Secret Access Key) are invalid"
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_app_version_get_all.called
        assert mock_gr_app_version_create_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called


@pytest.mark.asyncio
async def test_delete_guardrail(guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
    guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_view.guardrail_provider_response = {"AWS": response_data}

    with patch.object(
            mock_guardrail_repository, 'delete_record', return_value=None
    ) as mock_delete_record, patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_view
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'delete_guardrail', return_value={"AWS": response_data}
    ) as mock_bedrock_guardrail_delete:
        # Call the method under test
        await guardrail_service.delete(1)

        # Assertions
        assert mock_delete_record.called
        assert mock_get_record_by_id.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_delete.called


@pytest.mark.asyncio
async def test_delete_guardrail_when_guardrail_provider_gives_error(
        guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
    guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_view.guardrail_provider_response = {"AWS": response_data}

    with patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_view
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'delete_guardrail', side_effect=InternalServerError("AWS Error")
    ) as mock_guardrail_provider_manager:
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.delete(1)

        # Assertions
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to delete guardrails. Error - AWS Error"
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called


@pytest.mark.asyncio
async def test_delete_guardrail_when_guardrail_provider_does_not_gives_success_when_internal_failure(
        guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
    guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_view.guardrail_provider_response = {"AWS": response_data}

    with patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_view
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'delete_guardrail',
        return_value={"AWS": {"success": False, "response": {
            "details": {"errorType": "InternalFailure", "details": "AWS Error (InternalFailure)"}
        }}}
    ) as mock_guardrail_provider_manager:
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.delete(1)

        # Assertions
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to delete guardrail in AWS"
        assert exc_info.value.details == {"errorType": "InternalFailure", "details": "AWS Error (InternalFailure)"}
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called


@pytest.mark.asyncio
async def test_delete_guardrail_when_guardrail_provider_does_not_gives_success_when_access_denied(
        guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
    guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_view.guardrail_provider_response = {"AWS": response_data}

    with patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_view
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'delete_guardrail',
        return_value={"AWS": {"success": False, "response": {
            "message": "Access denied. Please ensure you have the correct permissions.",
            "details": {"errorType": "AccessDeniedException", "details": "AWS Error (AccessDeniedException)"}
        }}}
    ) as mock_guardrail_provider_manager:
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.delete(1)

        # Assertions
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to delete guardrail in AWS: Access Denied for the associated connection"
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called


@pytest.mark.asyncio
async def test_delete_guardrail_when_guardrail_provider_does_not_have_resource(
        guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
    guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    guardrail_view.guardrail_provider_response = {"AWS": response_data}

    with patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_view
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'delete_guardrail',
        return_value={"AWS": {"success": False, "response": {
            "details": {"errorType": "ResourceNotFoundException", "details": "AWS Error (ResourceNotFoundException)"}
        }}}
    ) as mock_guardrail_provider_manager:
        # Call the method under test
        await guardrail_service.delete(1)

        # Assertions
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called
