import copy
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.audit.RDS_service.rds_service import RdsService
from api.encryption.api_schemas.encryption_key import EncryptionKeyView
from api.governance.services.ai_app_service import AIAppService
from api.guardrails.api_schemas.gr_connection import GRConnectionView
from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GRConfigView, GRVersionHistoryFilter, \
    GRVersionHistoryView
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRVersionHistoryModel
from api.guardrails.database.db_operations.guardrail_repository import GuardrailRepository, GRVersionHistoryRepository
from api.guardrails.providers import GuardrailProviderManager
from api.guardrails.services.gr_connections_service import GRConnectionService
from api.guardrails.services.guardrails_service import GuardrailRequestValidator, GuardrailService
from core.exceptions import BadRequestException, NotFoundException, InternalServerError
from core.middlewares.request_session_context_middleware import set_user

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

guardrail_version_history_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "mock_guardrail",
    "description": "mock description",
    "version": 1,
    "guardrailConnectionName": "gr_connection_1",
    "guardrailProvider": "AWS",
    "guardrailId": 1
}

gr_connection_view = GRConnectionView(**gr_connection_view_json)

gr_config_view = GRConfigView(**guardrail_config_json)

guardrail_view = GuardrailView(**guardrail_view_json)

guardrail_version_history_view = GRVersionHistoryView(**guardrail_version_history_view_json)


@pytest.fixture
def mock_guardrail_repository():
    return AsyncMock(spec=GuardrailRepository)


@pytest.fixture
def mock_guardrail_version_history_repository():
    return AsyncMock(spec=GRVersionHistoryRepository)


@pytest.fixture
def mock_guardrail_connection_service():
    return AsyncMock(spec=GRConnectionService)


@pytest.fixture
def mock_ai_app_gov_service():
    return AsyncMock(spec=AIAppService)


@pytest.fixture
def guardrail_request_validator(mock_guardrail_repository):
    return GuardrailRequestValidator(guardrail_repository=mock_guardrail_repository)


@pytest.fixture
def mock_data_service():
    return AsyncMock(sepc=RdsService)


@pytest.fixture
def guardrail_service(mock_guardrail_repository, mock_guardrail_version_history_repository,
                      guardrail_request_validator, mock_guardrail_connection_service, mock_ai_app_gov_service, mock_data_service):
    return GuardrailService(
        guardrail_repository=mock_guardrail_repository,
        gr_version_history_repository=mock_guardrail_version_history_repository,
        guardrail_request_validator=guardrail_request_validator,
        guardrail_connection_service=mock_guardrail_connection_service,
        ai_app_governance_service=mock_ai_app_gov_service,
        data_service=mock_data_service
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
async def test_get_guardrail_version_history(guardrail_service, mock_guardrail_version_history_repository):
    guardrail_id = 1
    mock_filter = GRVersionHistoryFilter()
    mock_sort = ["create_time"]
    expected_records = [guardrail_version_history_view]
    expected_total_count = 100
    # Patch the list_records method on the repository
    with patch.object(
            mock_guardrail_version_history_repository, 'list_records', return_value=(expected_records, expected_total_count)
    ) as mock_list_records:
        # Call the method under test
        result = await guardrail_service.get_history(guardrail_id, mock_filter, 1, 10, mock_sort)

        # Assertions
        mock_list_records.assert_called_once_with(filter=mock_filter, page_number=1, size=10, sort=mock_sort)
        assert result.content == expected_records
        assert result.totalElements == expected_total_count


@pytest.mark.asyncio
async def test_create_guardrail(guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
                                mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_configs = [gr_config_view]

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(create_guardrail_view.model_dump())

    gr_version_history_model = GRVersionHistoryModel(id=1, guardrail_id=1, version=1)
    gr_connection_model = GRConnectionModel(**gr_connection_view.model_dump())

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_model
    ) as mock_guardrail_create_record, patch.object(
            mock_guardrail_repository, 'update_record', return_value=guardrail_model
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_version_history_repository, 'create_record', return_value=gr_version_history_model
    ) as mock_gr_version_history_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_model]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_create):
        # set the context user
        set_user({"login_user": {"id": 1, "username": "Test_User"}})
        # Call the method under test
        result = await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == create_guardrail_view.name
        assert result.guardrail_configs == create_guardrail_view.guardrail_configs
        assert result.guardrail_provider == create_guardrail_view.guardrail_provider
        assert result.guardrail_connection_name == create_guardrail_view.guardrail_connection_name
        assert mock_guardrail_create_record.called
        assert mock_guardrail_update_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_create_record.called
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
        mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_view.guardrail_connection_name = "INVALID_CONNECTION"

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
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
        assert mock_gr_connection_get_all.called
        assert not mock_bedrock_guardrail_create.called
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail Connection not found with name: ['INVALID_CONNECTION']"


@pytest.mark.asyncio
async def test_create_guardrail_when_guardrail_provider_gives_error(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_view.guardrail_connections = {"AWS": {"connectionName": "mock_connection_name"}}

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[GRConnectionModel(**gr_connection_view.model_dump())]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', side_effect=InternalServerError("AWS Error")
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to create guardrails. Error - AWS Error"


@pytest.mark.asyncio
async def test_create_guardrail_when_guardrail_provider_does_not_give_success_as_token_expired(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_view.guardrail_connections = {"AWS": {"connectionName": "mock_connection_name"}}

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]

    with (patch.object(
            mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[GRConnectionModel(**gr_connection_view.model_dump())]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": False, "response": {"details": {"errorType": "ClientError", "details": "AWS Error ExpiredTokenException"}}}}
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to create guardrail: The security token included in the connection is expired."


@pytest.mark.asyncio
async def test_get_guardrail_by_id(guardrail_service, mock_guardrail_repository):
    guardrail_view_data = GuardrailView(**guardrail_view_json)
    gr_config_view_data = GRConfigView(**guardrail_config_json)
    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(guardrail_view_data.model_dump())
    guardrail_model.guardrail_configs = [gr_config_view_data.model_dump()]
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
        assert result.guardrail_configs[0].config_type == gr_config_view_data.config_type
        assert result.guardrail_configs[0].config_data == gr_config_view_data.config_data
        assert result.guardrail_connection_details == gr_connection_details


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
        mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)

    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)

    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())
    guardrail_model.guardrail_configs = [gr_config_view_to_update.model_dump(), gr_config_view_to_delete.model_dump()]

    gr_version_history_model = GRVersionHistoryModel(id=1, guardrail_id=1, version=1)

    with (patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_repository, 'update_record', return_value=update_guardrail_view
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_version_history_repository, 'create_record', return_value=gr_version_history_model
    ) as mock_gr_version_history_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'update_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_update):
        # set the context user
        set_user({"login_user": {"id": 1, "username": "Test_User"}})
        # Call the method under test
        result = await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == update_guardrail_view.name
        assert result.guardrail_configs == update_guardrail_view.guardrail_configs
        assert result.guardrail_provider == update_guardrail_view.guardrail_provider
        assert result.guardrail_connection_name == update_guardrail_view.guardrail_connection_name
        assert result.guardrail_connection_details == update_guardrail_view.guardrail_connection_details
        assert result.guardrail_provider_response is None
        assert mock_guardrail_update_record.called
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_create_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called


@pytest.mark.asyncio
async def test_update_guardrail_when_connection_is_updated(guardrail_service, mock_guardrail_repository,
                                                           mock_guardrail_version_history_repository,
                                                           mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_conf_view = GRConfigView(**guardrail_config_json)
    update_guardrail_view.guardrail_configs = [gr_conf_view]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())

    update_guardrail_view.guardrail_connection_name = "gr_connection_2"

    gr_version_history_model = GRVersionHistoryModel(id=1, guardrail_id=1, version=1)

    gr_connection_view2 = GRConnectionView(**gr_connection_view_json)
    gr_connection_view2.name = "gr_connection_2"

    with (patch.object(
            mock_guardrail_repository, 'update_record', return_value=update_guardrail_view
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_version_history_repository, 'create_record', return_value=gr_version_history_model
    ) as mock_gr_version_history_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view, gr_connection_view2]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'create_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_create, patch.object(
        GuardrailProviderManager, 'delete_guardrail', return_value={"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}
    ) as mock_bedrock_guardrail_delete):
        # set the context user
        set_user({"login_user": {"id": 1, "username": "Test_User"}})
        # Call the method under test
        result = await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == update_guardrail_view.name
        assert result.guardrail_configs == update_guardrail_view.guardrail_configs
        assert result.guardrail_provider == update_guardrail_view.guardrail_provider
        assert result.guardrail_connection_name == update_guardrail_view.guardrail_connection_name
        assert result.guardrail_connection_details == update_guardrail_view.guardrail_connection_details
        assert mock_guardrail_update_record.called
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_version_history_create_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert mock_bedrock_guardrail_delete.called


@pytest.mark.asyncio
async def test_update_guardrail_when_name_already_exists(guardrail_service, mock_guardrail_repository):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    update_guardrail_view.guardrail_configs = [gr_config_view]
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
async def test_update_guardrail_when_guardrail_provider_gives_error(guardrail_service,
                                                                    mock_guardrail_repository,
                                                                    mock_guardrail_version_history_repository,
                                                                    mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)
    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())
    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    guardrail_model.guardrail_configs = [gr_config_view_to_update.model_dump(), gr_config_view_to_delete.model_dump()]

    with (patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
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
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called


@pytest.mark.asyncio
async def test_update_guardrail_when_guardrail_provider_does_not_gives_success_as_access_secret_key_invalid(
        guardrail_service, mock_guardrail_repository, mock_guardrail_version_history_repository,
        mock_guardrail_connection_service):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)
    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.guardrail_provider_response = {"AWS": {"success": True, "response": {"guardrailId": "mock_aws_gr_1"}}}

    guardrail_model = GuardrailModel()
    guardrail_model.set_attribute(update_guardrail_view.model_dump())
    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    guardrail_model.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_delete]

    with (patch.object(
            mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_view]
    ) as mock_gr_connection_get_all, patch.object(
        GuardrailProviderManager, 'update_guardrail', return_value={"AWS": {"success": False, "response": {"details": {"errorType": "ClientError", "details": "AWS Error UnrecognizedClientException"}}}}
    ) as mock_bedrock_guardrail_update):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to update guardrail: The provided authentication credentials for the associated connection are invalid."
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called


@pytest.mark.asyncio
async def test_delete_guardrail(guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
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
        # set the context user
        set_user({"login_user": {"id": 1, "username": "Test_User"}})
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
        assert exc_info.value.message == "Failed to delete guardrail"
        assert exc_info.value.details == {"errorType": "InternalFailure", "details": "AWS Error (InternalFailure)"}
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called


@pytest.mark.asyncio
async def test_delete_guardrail_when_guardrail_provider_does_not_gives_success_when_access_denied(
        guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
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
        assert exc_info.value.message == "Failed to delete guardrail: Access Denied for the associated connection."
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called


@pytest.mark.asyncio
async def test_delete_guardrail_when_guardrail_provider_does_not_have_resource(
        guardrail_service, mock_guardrail_connection_service, mock_guardrail_repository):
    response_data = {"success": True, "response": {"guardrailId": 1}}
    guardrail_view.guardrail_configs = [gr_config_view]
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
        # set the context user
        set_user({"login_user": {"id": 1, "username": "Test_User"}})
        # Call the method under test
        await guardrail_service.delete(1)

        # Assertions
        assert mock_get_record_by_id.called
        assert mock_guardrail_provider_manager.called
        assert mock_gr_connection_get_all.called


@pytest.mark.asyncio
async def test_validate_name_valid_cases(guardrail_request_validator):
    # Test valid names
    valid_names = [
        "valid_name",
        "valid-name",
        "valid_name_123",
        "valid-name-123",
        "a" * 50  # Max length
    ]

    for name in valid_names:
        # Should not raise any exception
        guardrail_request_validator.validate_name(name)


@pytest.mark.asyncio
async def test_validate_name_invalid_cases(guardrail_request_validator):
    # Test invalid names
    invalid_cases = [
        ("", "Guardrail name must be provided"),  # Empty string
        ("a" * 51, "Guardrail name must be less than or equal to 50 characters"),  # Too long
        ("invalid name", "Guardrail name can only contain alphabets, numbers, underscore (_) and hyphen (-)"),  # Space
        ("invalid@name", "Guardrail name can only contain alphabets, numbers, underscore (_) and hyphen (-)"),  # Special char
        ("invalid/name", "Guardrail name can only contain alphabets, numbers, underscore (_) and hyphen (-)"),  # Special char
        (None, "Guardrail name must be provided"),  # None value
    ]

    for name, expected_error in invalid_cases:
        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_name(name)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_description_valid_cases(guardrail_request_validator):
    # Test valid descriptions
    valid_descriptions = [
        None,  # Optional field
        "",  # Empty string is allowed
        "Valid description",
        "Valid description with numbers 123",
        "Valid description with special chars !@#$%^&*()",
        "a" * 200  # Max length
    ]

    for description in valid_descriptions:
        # Should not raise any exception
        guardrail_request_validator.validate_description(description)


@pytest.mark.asyncio
async def test_validate_description_invalid_cases(guardrail_request_validator):
    # Test invalid descriptions
    invalid_cases = [
        ("a" * 201, "Guardrail description must be less than or equal to 200 characters"),  # Too long
    ]

    for description, expected_error in invalid_cases:
        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_description(description)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_configs_empty_configs(guardrail_request_validator):
    # Test when no configs are provided
    guardrail_view = GuardrailView(**guardrail_view_json)
    guardrail_view.guardrail_configs = []

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert str(exc_info.value) == "Guardrail Configurations must be provided"


@pytest.mark.asyncio
async def test_validate_configs_duplicate_config_types(guardrail_request_validator):
    # Test when duplicate config types are provided
    guardrail_view = GuardrailView(**guardrail_view_json)
    duplicate_config = GRConfigView(**guardrail_config_json)
    guardrail_view.guardrail_configs = [gr_config_view, duplicate_config]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert str(exc_info.value) == "Multiple Guardrail configurations of same type ['CONTENT_MODERATION'] not allowed"


@pytest.mark.asyncio
async def test_validate_configs_valid_off_topic(guardrail_request_validator):
    # Test valid OFF_TOPIC config
    guardrail_view = GuardrailView(**guardrail_view_json)
    off_topic_config = GRConfigView(**guardrail_config_json3)
    guardrail_view.guardrail_configs = [off_topic_config]

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_topic_name_regex_valid_cases(guardrail_request_validator):
    # Test valid topic names
    valid_topic_names = [
        "valid_topic",
        "valid-topic",
        "valid topic",
        "valid.topic",
        "valid!topic",
        "valid?topic",
        "valid_topic_123",
        "valid-topic-123",
        "valid topic 123",
        "valid.topic.123",
        "valid!topic!123",
        "valid?topic?123",
        "a" * 100  # Max length
    ]

    for topic_name in valid_topic_names:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = copy.deepcopy(guardrail_config_json3)
        config['configData']['configs'][0]['topic'] = topic_name
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        # Should not raise any exception
        guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_topic_name_regex_invalid_cases(guardrail_request_validator):
    # Test invalid topic names
    invalid_cases = [
        ("", "Topic name for topic 1 must be provided"),  # Empty string
        ("a" * 101, "Topic name for topic 1 must be less than or equal to 100 characters"),  # Too long
        ("invalid@topic", "Topic name can only contain alphabets, numbers, underscore (_), hyphen (-), space, exclamation point (!), question mark (?), and period (.)"),  # Special char
        ("invalid/topic", "Topic name can only contain alphabets, numbers, underscore (_), hyphen (-), space, exclamation point (!), question mark (?), and period (.)"),  # Special char
        ("invalid#topic", "Topic name can only contain alphabets, numbers, underscore (_), hyphen (-), space, exclamation point (!), question mark (?), and period (.)"),  # Special char
        ("invalid$topic", "Topic name can only contain alphabets, numbers, underscore (_), hyphen (-), space, exclamation point (!), question mark (?), and period (.)"),  # Special char
        (None, "Topic name for topic 1 must be provided"),  # None value
    ]

    for topic_name, expected_error in invalid_cases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = copy.deepcopy(guardrail_config_json3)
        config['configData']['configs'][0]['topic'] = topic_name
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_configs(guardrail_view)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_topic_definition_valid_cases(guardrail_request_validator):
    # Test valid topic definitions
    valid_definitions = [
        "Valid definition",
        "Valid definition with numbers 123",
        "Valid definition with special chars !@#$%^&*()",
        "a" * 200  # Max length
    ]

    for definition in valid_definitions:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = copy.deepcopy(guardrail_config_json3)
        config['configData']['configs'][0]['definition'] = definition
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        # Should not raise any exception
        guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_topic_definition_invalid_cases(guardrail_request_validator):
    # Test invalid topic definitions
    invalid_cases = [
        ("", "Topic definition for topic 1 must be provided"),  # Empty string
        ("a" * 201, "Topic definition for topic 1 must be less than or equal to 200 characters"),  # Too long
        (None, "Topic definition for topic 1 must be provided"),  # None value
    ]

    for definition, expected_error in invalid_cases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = copy.deepcopy(guardrail_config_json3)
        config['configData']['configs'][0]['definition'] = definition
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_configs(guardrail_view)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_sample_phrases_valid_cases(guardrail_request_validator):
    # Test valid sample phrases
    valid_phrases = [
        "Valid sample phrase",
        "Valid phrase with numbers 123",
        "Valid phrase with special chars !@#$%^&*()",
        "a" * 100  # Max length
    ]

    for phrase in valid_phrases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = copy.deepcopy(guardrail_config_json3)
        config['configData']['configs'][0]['samplePhrases'] = [phrase]
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        # Should not raise any exception
        guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_sample_phrases_invalid_cases(guardrail_request_validator):
    # Test invalid sample phrases
    invalid_cases = [
        ("", "Sample phrase 1 for topic 1 must be provided"),  # Empty string
        ("a" * 101, "Sample phrase 1 for topic 1 must be less than or equal to 100 characters"),  # Too long
        (None, "Sample phrase 1 for topic 1 must be provided"),  # None value
    ]

    for phrase, expected_error in invalid_cases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = copy.deepcopy(guardrail_config_json3)
        config['configData']['configs'][0]['samplePhrases'] = [phrase]
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_configs(guardrail_view)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_sample_phrases_multiple_phrases(guardrail_request_validator):
    # Test multiple valid sample phrases
    valid_phrases = [
        "First valid phrase",
        "Second valid phrase",
        "Third valid phrase",
        "Fourth valid phrase",
        "Fifth valid phrase"
    ]

    guardrail_view = GuardrailView(**guardrail_view_json)
    config = copy.deepcopy(guardrail_config_json3)
    config['configData']['configs'][0]['samplePhrases'] = valid_phrases
    guardrail_view.guardrail_configs = [GRConfigView(**config)]

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_sample_phrases_too_many_phrases(guardrail_request_validator):
    # Test when too many sample phrases are provided
    too_many_phrases = [
        "First phrase",
        "Second phrase",
        "Third phrase",
        "Fourth phrase",
        "Fifth phrase",
        "Sixth phrase"  # This exceeds the limit of 5
    ]

    guardrail_view = GuardrailView(**guardrail_view_json)
    config = copy.deepcopy(guardrail_config_json3)
    config['configData']['configs'][0]['samplePhrases'] = too_many_phrases
    guardrail_view.guardrail_configs = [GRConfigView(**config)]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Maximum 5 sample phrases are allowed per topic" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_sample_phrases_mixed_validity(guardrail_request_validator):
    # Test when some phrases are valid and others are invalid
    mixed_phrases = [
        "Valid phrase",
        "",  # Invalid empty string
        "Another valid phrase"
    ]

    guardrail_view = GuardrailView(**guardrail_view_json)
    config = copy.deepcopy(guardrail_config_json3)
    config['configData']['configs'][0]['samplePhrases'] = mixed_phrases
    guardrail_view.guardrail_configs = [GRConfigView(**config)]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Sample phrase 2 for topic 1 must be provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_configs_valid_denied_terms(guardrail_request_validator):
    # Test valid DENIED_TERMS config
    guardrail_view = GuardrailView(**guardrail_view_json)
    denied_terms_config = GRConfigView(**guardrail_config_json2)
    guardrail_view.guardrail_configs = [denied_terms_config]

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_configs_invalid_denied_terms(guardrail_request_validator):
    # Test invalid DENIED_TERMS config with duplicate keywords
    guardrail_view = GuardrailView(**guardrail_view_json)
    invalid_config = copy.deepcopy(guardrail_config_json2)
    invalid_config['configData']['configs'][1]['keywords'] = ['duplicate', 'duplicate']
    denied_terms_config = GRConfigView(**invalid_config)
    guardrail_view.guardrail_configs = [denied_terms_config]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Repeated keyword" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_denied_terms_max_limit(guardrail_request_validator):
    # Test when total number of keywords exceeds 10000
    guardrail_view = GuardrailView(**guardrail_view_json)
    invalid_config = copy.deepcopy(guardrail_config_json2)

    # Create 10001 keywords (exceeding the limit)
    invalid_config['configData']['configs'][1]['keywords'] = [f"keyword_{i}" for i in range(10001)]
    denied_terms_config = GRConfigView(**invalid_config)
    guardrail_view.guardrail_configs = [denied_terms_config]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Maximum 10000 phrases or keywords are allowed in Denied terms" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_denied_terms_multiple_configs_total_limit(guardrail_request_validator):
    # Test when total keywords across multiple configs exceeds 10000
    guardrail_view = GuardrailView(**guardrail_view_json)

    # Create multiple configs with keywords that sum to more than 10000
    configs = []
    for i in range(5):  # 5 configs with 2001 keywords each = 10005 total
        config = copy.deepcopy(guardrail_config_json2)
        config['configData']['configs'][1]['keywords'] = [f"keyword_{i}_{j}" for j in range(2001)]
        configs.append(GRConfigView(**config))

    guardrail_view.guardrail_configs = configs

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Maximum 10000 phrases or keywords are allowed in Denied terms" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_denied_terms_exact_limit(guardrail_request_validator):
    # Test when total number of keywords is exactly 10000
    guardrail_view = GuardrailView(**guardrail_view_json)
    valid_config = copy.deepcopy(guardrail_config_json2)

    # Create exactly 10000 keywords
    valid_config['configData']['configs'][1]['keywords'] = [f"keyword_{i}" for i in range(10000)]
    denied_terms_config = GRConfigView(**valid_config)
    guardrail_view.guardrail_configs = [denied_terms_config]

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_denied_terms_multiple_configs_under_limit(guardrail_request_validator):
    # Test when total keywords across multiple configs is under 10000
    guardrail_view = GuardrailView(**guardrail_view_json)

    # Create multiple configs with keywords that sum to less than 10000
    configs = []
    for i in range(5):  # 5 configs with 1000 keywords each = 5000 total
        config = copy.deepcopy(guardrail_config_json2)
        config['configData']['configs'][1]['keywords'] = [f"keyword_{i}_{j}" for j in range(1000)]
        configs.append(GRConfigView(**config))

    guardrail_view.guardrail_configs = configs

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_denied_terms_keyword_length(guardrail_request_validator):
    # Test when keyword length exceeds 100 characters
    guardrail_view = GuardrailView(**guardrail_view_json)
    invalid_config = copy.deepcopy(guardrail_config_json2)

    # Create a keyword that's 101 characters long
    invalid_config['configData']['configs'][1]['keywords'] = ["a" * 101]
    denied_terms_config = GRConfigView(**invalid_config)
    guardrail_view.guardrail_configs = [denied_terms_config]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Phrase or Keyword" in str(exc_info.value)
    assert "must be less than or equal to 100 characters" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_denied_terms_keyword_required(guardrail_request_validator):
    # Test when keyword is empty or None
    guardrail_view = GuardrailView(**guardrail_view_json)
    invalid_config = copy.deepcopy(guardrail_config_json2)

    # Test empty string
    invalid_config['configData']['configs'][1]['keywords'] = [""]
    denied_terms_config = GRConfigView(**invalid_config)
    guardrail_view.guardrail_configs = [denied_terms_config]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Phrase or Keyword" in str(exc_info.value)
    assert "must be provided" in str(exc_info.value)

    # Test None value
    invalid_config['configData']['configs'][1]['keywords'] = [None]
    denied_terms_config = GRConfigView(**invalid_config)
    guardrail_view.guardrail_configs = [denied_terms_config]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Phrase or Keyword" in str(exc_info.value)
    assert "must be provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_configs_valid_sensitive_data(guardrail_request_validator):
    # Test valid SENSITIVE_DATA config
    guardrail_view = GuardrailView(**guardrail_view_json)
    sensitive_data_config = {
        "configType": "SENSITIVE_DATA",
        "configData": {
            "configs": [
                {
                    "type": "REGEX",
                    "name": "test_regex",
                    "description": "test description",
                    "pattern": "test.*pattern"
                }
            ]
        }
    }
    guardrail_view.guardrail_configs = [GRConfigView(**sensitive_data_config)]

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_configs_invalid_sensitive_data(guardrail_request_validator):
    # Test invalid SENSITIVE_DATA config with missing required fields
    guardrail_view = GuardrailView(**guardrail_view_json)
    invalid_config = {
        "configType": "SENSITIVE_DATA",
        "configData": {
            "configs": [
                {
                    "type": "REGEX",
                    "name": "test_regex"
                    # Missing required fields: description and pattern
                }
            ]
        }
    }
    guardrail_view.guardrail_configs = [GRConfigView(**invalid_config)]

    with pytest.raises(BadRequestException) as exc_info:
        guardrail_request_validator.validate_configs(guardrail_view)
    assert "Regex pattern from Regex 1 must be provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_name_valid_cases(guardrail_request_validator):
    # Test valid regex names
    valid_names = [
        "valid_regex_name",
        "valid-regex-name",
        "valid_regex_name_123",
        "valid-regex-name-123",
        "a" * 100  # Max length
    ]

    for name in valid_names:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = {
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "type": "REGEX",
                        "name": name,
                        "description": "test description",
                        "pattern": "test.*pattern"
                    }
                ]
            }
        }
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        # Should not raise any exception
        guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_name_invalid_cases(guardrail_request_validator):
    # Test invalid regex names
    invalid_cases = [
        ("", "Name from Regex 1 must be provided"),  # Empty string
        ("a" * 101, "Name from Regex 1 must be less than or equal to 100 characters"),  # Too long
        (None, "Name from Regex 1 must be provided"),  # None value
    ]

    for name, expected_error in invalid_cases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = {
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "type": "REGEX",
                        "name": name,
                        "description": "test description",
                        "pattern": "test.*pattern"
                    }
                ]
            }
        }
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_configs(guardrail_view)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_description_valid_cases(guardrail_request_validator):
    # Test valid regex descriptions
    valid_descriptions = [
        None,  # Optional field
        "",  # Empty string is allowed
        "Valid description",
        "Valid description with numbers 123",
        "Valid description with special chars !@#$%^&*()",
        "a" * 1000  # Max length
    ]

    for description in valid_descriptions:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = {
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "type": "REGEX",
                        "name": "test_regex",
                        "description": description,
                        "pattern": "test.*pattern"
                    }
                ]
            }
        }
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        # Should not raise any exception
        guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_description_invalid_cases(guardrail_request_validator):
    # Test invalid regex descriptions
    invalid_cases = [
        ("a" * 1001, "Description from Regex 1 must be less than or equal to 1000 characters"),  # Too long
    ]

    for description, expected_error in invalid_cases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = {
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "type": "REGEX",
                        "name": "test_regex",
                        "description": description,
                        "pattern": "test.*pattern"
                    }
                ]
            }
        }
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_configs(guardrail_view)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_pattern_valid_cases(guardrail_request_validator):
    # Test valid regex patterns
    valid_patterns = [
        "test.*pattern",
        "[0-9]+",
        "[a-zA-Z]+",
        "\\d{3}-\\d{3}-\\d{4}",  # Phone number pattern
        "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",  # Email pattern
        "a" * 500  # Max length
    ]

    for pattern in valid_patterns:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = {
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "type": "REGEX",
                        "name": "test_regex",
                        "description": "test description",
                        "pattern": pattern
                    }
                ]
            }
        }
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        # Should not raise any exception
        guardrail_request_validator.validate_configs(guardrail_view)


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_pattern_invalid_cases(guardrail_request_validator):
    # Test invalid regex patterns
    invalid_cases = [
        ("", "Regex pattern from Regex 1 must be provided"),  # Empty string
        ("a" * 501, "Regex pattern from Regex 1 must be less than or equal to 500 characters"),  # Too long
        (None, "Regex pattern from Regex 1 must be provided"),  # None value
    ]

    for pattern, expected_error in invalid_cases:
        guardrail_view = GuardrailView(**guardrail_view_json)
        config = {
            "configType": "SENSITIVE_DATA",
            "configData": {
                "configs": [
                    {
                        "type": "REGEX",
                        "name": "test_regex",
                        "description": "test description",
                        "pattern": pattern
                    }
                ]
            }
        }
        guardrail_view.guardrail_configs = [GRConfigView(**config)]

        with pytest.raises(BadRequestException) as exc_info:
            guardrail_request_validator.validate_configs(guardrail_view)
        assert str(exc_info.value) == expected_error


@pytest.mark.asyncio
async def test_validate_sensitive_data_regex_multiple_configs(guardrail_request_validator):
    # Test multiple regex configs
    guardrail_view = GuardrailView(**guardrail_view_json)
    config = {
        "configType": "SENSITIVE_DATA",
        "configData": {
            "configs": [
                {
                    "type": "REGEX",
                    "name": "first_regex",
                    "description": "first description",
                    "pattern": "first.*pattern"
                },
                {
                    "type": "REGEX",
                    "name": "second_regex",
                    "description": "second description",
                    "pattern": "second.*pattern"
                }
            ]
        }
    }
    guardrail_view.guardrail_configs = [GRConfigView(**config)]

    # Should not raise any exception
    guardrail_request_validator.validate_configs(guardrail_view)
