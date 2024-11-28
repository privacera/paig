from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails.api_schemas.gr_connection import GRConnectionView
from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GRConfigView
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails import GuardrailProvider
from api.guardrails.database.db_models.guardrail_model import GRApplicationModel, GRConfigModel, \
    GRApplicationVersionModel, GuardrailModel, GRProviderResponseModel
from api.guardrails.database.db_models.guardrail_view_model import GuardrailViewModel
from api.guardrails.database.db_operations.guardrail_repository import GuardrailRepository, GRConfigRepository, \
    GRProviderResponseRepository, GRApplicationRepository, GRApplicationVersionRepository, GuardrailViewRepository
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
    "version": 1
}

guardrail_config_json = {
    "guardrailProvider": "AWS",
    "guardrailProviderConnectionName": "gr_connection_1",
    "configType": "contentPolicyConfig",
    "configData": {
        "filtersConfig": [
            {
                "inputStrength": "HIGH",
                "outputStrength": "HIGH",
                "type": "VIOLENCE"
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "NONE",
                "type": "PROMPT_ATTACK"
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "HIGH",
                "type": "MISCONDUCT"
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "HIGH",
                "type": "HATE"
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "HIGH",
                "type": "SEXUAL"
            },
            {
                "inputStrength": "HIGH",
                "outputStrength": "HIGH",
                "type": "INSULTS"
            }
        ]
    }
}

guardrail_config_json2 = {
    "guardrailProvider": "AWS",
    "guardrailProviderConnectionName": "gr_connection_1",
    "configType": "wordPolicyConfig",
    "configData": {
        "managedWordListsConfig": [
            {
                "type": "PROFANITY"
            }
        ],
        "wordsConfig": [
            {
                "text": "Fictious Enterprise"
            }
        ]
    }
}

guardrail_config_json3 = {
    "guardrailProvider": "AWS",
    "guardrailProviderConnectionName": "gr_connection_1",
    "configType": "contextualGroundingPolicyConfig",
    "configData": {
        "filtersConfig": [
            {
                "type": "GROUNDING",
                "threshold": 0.2
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
def mock_guardrail_application_repository():
    return AsyncMock(spec=GRApplicationRepository)


@pytest.fixture
def mock_guardrail_app_version_repository():
    return AsyncMock(spec=GRApplicationVersionRepository)


@pytest.fixture
def mock_gr_config_repository():
    return AsyncMock(spec=GRConfigRepository)


@pytest.fixture
def mock_gr_provider_response_repository():
    return AsyncMock(spec=GRProviderResponseRepository)


@pytest.fixture
def mock_guardrail_view_repository():
    return AsyncMock(spec=GuardrailViewRepository)


@pytest.fixture
def mock_guardrail_connection_service():
    return AsyncMock(spec=GRConnectionService)


@pytest.fixture
def guardrail_request_validator(mock_guardrail_repository, mock_gr_config_repository,
                                mock_gr_provider_response_repository):
    return GuardrailRequestValidator(guardrail_repository=mock_guardrail_repository,
                                     gr_config_repository=mock_gr_config_repository,
                                     gr_provider_response_repository=mock_gr_provider_response_repository)


@pytest.fixture
def guardrail_service(mock_guardrail_repository, mock_guardrail_application_repository,
                      mock_guardrail_app_version_repository, mock_gr_config_repository,
                      mock_gr_provider_response_repository, mock_guardrail_view_repository,
                      guardrail_request_validator, mock_guardrail_connection_service):
    return GuardrailService(
        guardrail_repository=mock_guardrail_repository,
        gr_app_repository=mock_guardrail_application_repository,
        gr_app_version_repository=mock_guardrail_app_version_repository,
        gr_config_repository=mock_gr_config_repository,
        gr_provider_response_repository=mock_gr_provider_response_repository,
        gr_view_repository=mock_guardrail_view_repository,
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
async def test_create_guardrail(guardrail_service, mock_guardrail_repository, mock_guardrail_application_repository,
                                mock_guardrail_app_version_repository, mock_gr_config_repository,
                                mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_view.guardrail_configs = [gr_config_view]
    create_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]

    gr_app_model = GRApplicationModel(id=1, guardrail_id=1, application_key="mock_app_key1")
    gr_config_model = GRConfigModel(**gr_config_view.model_dump())
    gr_connection_model = GRConnectionModel(**gr_connection_view.model_dump())
    gr_app_versions = [GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)]

    from api.guardrails.providers.backend.bedrock import BedrockGuardrailProvider
    with (patch.object(
        mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_application_repository, 'create_record', return_value=gr_app_model
    ) as mock_gr_app_create_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=gr_app_versions
    ) as mock_gr_app_version_get_all, patch.object(
        mock_gr_config_repository, 'create_record', return_value=gr_config_model
    ) as mock_gr_config_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_model]
    ) as mock_gr_connection_get_all, patch.object(
        BedrockGuardrailProvider, 'create_guardrail', return_value=(True, {"guardrail_id": 1})
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        result = await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == create_guardrail_view.name
        assert result.guardrail_configs == create_guardrail_view.guardrail_configs
        assert result.application_keys == create_guardrail_view.application_keys
        assert result.guardrail_connections == create_guardrail_view.guardrail_connections
        assert result.guardrail_provider_response == {'AWS': {'response': {'guardrail_id': 1}, 'success': True}}
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_app_create_record.called
        assert mock_gr_app_version_get_all.called
        assert mock_gr_config_create_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called


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
async def test_create_guardrail_when_config_has_different_connections_for_same_provider(guardrail_service,
                                                                                        mock_guardrail_repository):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    gr_config_1 = GRConfigView(**guardrail_config_json)
    gr_config_1.guardrail_provider_connection_name = "gr_connection_1"
    gr_config_2 = GRConfigView(**guardrail_config_json)
    gr_config_2.guardrail_provider_connection_name = "gr_connection_2"

    create_guardrail_view.guardrail_configs = [gr_config_1, gr_config_2]

    with patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail configurations should have same connection for same provider"
        assert not mock_get_by_name.called
        assert not mock_guardrail_repository.create_record.called


@pytest.mark.asyncio
async def test_create_guardrail_when_invalid_connection_name_provided(
        guardrail_service, mock_guardrail_repository, mock_guardrail_application_repository,
        mock_guardrail_app_version_repository, mock_gr_config_repository, mock_guardrail_connection_service):
    create_guardrail_view = GuardrailView(**guardrail_view_json)
    create_guardrail_config_view = GRConfigView(**guardrail_config_json)

    create_guardrail_config_view.guardrail_provider_connection_name = "INVALID_CONNECTION"

    create_guardrail_view.guardrail_configs = [create_guardrail_config_view]
    create_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]

    gr_app_model = GRApplicationModel(id=1, guardrail_id=1, application_key="mock_app_key1")
    gr_config_model = GRConfigModel(**create_guardrail_config_view.model_dump())

    from api.guardrails.providers.backend.bedrock import BedrockGuardrailProvider
    with (patch.object(
        mock_guardrail_repository, 'create_record', return_value=guardrail_view
    ) as mock_guardrail_create_record, patch.object(
        mock_guardrail_repository, 'list_records', return_value=(None, 0)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_application_repository, 'create_record', return_value=gr_app_model
    ) as mock_gr_app_create_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[]
    ) as mock_gr_app_version_get_all, patch.object(
        mock_gr_config_repository, 'create_record', return_value=gr_config_model
    ) as mock_gr_config_create_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[]
    ) as mock_gr_connection_get_all, patch.object(
        BedrockGuardrailProvider, 'create_guardrail', return_value=(True, {"guardrail_id": 1})
    ) as mock_bedrock_guardrail_create):
        # Call the method under test
        with pytest.raises(InternalServerError) as exc_info:
            await guardrail_service.create(create_guardrail_view)

        # Assertions
        assert mock_guardrail_create_record.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_app_create_record.called
        assert mock_gr_app_version_get_all.called
        assert mock_gr_config_create_record.called
        assert mock_gr_connection_get_all.called
        assert not mock_bedrock_guardrail_create.called
        assert exc_info.type == InternalServerError
        assert exc_info.value.message == "Failed to create guardrails. Error - 'AWS'"


@pytest.mark.asyncio
async def test_get_guardrail_by_id(guardrail_service, mock_guardrail_view_repository):
    guardrail_view_data = GuardrailView(**guardrail_view_json)
    gr_config_view_data = GRConfigView(**guardrail_config_json)
    gr_view_model = GuardrailViewModel()
    gr_view_model.set_attribute(gr_config_view_data.model_dump())
    gr_view_model.set_attribute(guardrail_view_data.model_dump())
    gr_view_model.application_keys = ["mock_app_key1", "mock_app_key2"]
    gr_view_model.guardrail_id = 1
    with patch.object(
        mock_guardrail_view_repository, 'get_all', return_value=[gr_view_model]
    ) as mock_guardrail_get_all:
        # Call the method under test
        result = await guardrail_service.get_by_id(1)

        # Assertions
        mock_guardrail_get_all.assert_called_once_with(filters={"guardrail_id": 1})
        assert result.id == 1
        assert result.name == guardrail_view_data.name
        assert result.application_keys == gr_view_model.application_keys
        assert result.guardrail_configs[0].config_type == gr_config_view_data.config_type
        assert result.guardrail_configs[0].config_data == gr_config_view_data.config_data


@pytest.mark.asyncio
async def test_get_guardrail_by_id_when_not_found(guardrail_service, mock_guardrail_repository):
    with patch.object(
            mock_guardrail_repository, 'get_record_by_id', side_effect=NoResultFound
    ) as mock_get_record_by_id:
        # Call the method under test
        with pytest.raises(NotFoundException) as exc_info:
            await guardrail_service.get_by_id(1)

        # Assertions
        mock_get_record_by_id.assert_called_once_with(1)
        assert exc_info.type == NotFoundException
        assert exc_info.value.message == "Guardrail not found with ID: [1]"


@pytest.mark.asyncio
async def test_update_guardrail(
        guardrail_service, mock_guardrail_repository, mock_guardrail_application_repository,
        mock_guardrail_app_version_repository, mock_gr_config_repository, mock_guardrail_connection_service,
        mock_gr_provider_response_repository):

    update_guardrail_view = GuardrailView(**guardrail_view_json)

    gr_config_view_to_update = GRConfigView(**guardrail_config_json)
    gr_config_view_to_update.id = 1

    gr_config_view_to_delete = GRConfigView(**guardrail_config_json2)
    gr_config_view_to_delete.id = 2

    gr_config_view_to_add = GRConfigView(**guardrail_config_json3)

    update_guardrail_view.guardrail_configs = [gr_config_view_to_update, gr_config_view_to_add]
    update_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key3"]

    guardrail_model = GuardrailModel(id=1, name="mock_guardrail", description="mock description", version=1)

    gr_app_model_existing = GRApplicationModel(id=1, guardrail_id=1, application_key="mock_app_key1")
    gr_app_model_to_delete = GRApplicationModel(id=2, guardrail_id=1, application_key="mock_app_key2")
    gr_app_model_to_add = GRApplicationModel(id=3, guardrail_id=1, application_key="mock_app_key3")

    gr_config_model_to_update = GRConfigModel(**gr_config_view_to_update.model_dump())
    gr_config_model_to_delete = GRConfigModel(**gr_config_view_to_delete.model_dump())
    gr_config_model_to_add = GRConfigModel(**gr_config_view_to_add.model_dump())
    gr_config_model_to_add.id = 3

    gr_connection_model = GRConnectionModel(**gr_connection_view.model_dump())
    gr_app_version_model_to_bump1 = GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)
    gr_app_version_model_to_bump2 = GRApplicationVersionModel(id=2, application_key="mock_app_key2", version=1)
    gr_app_version_model_to_add = GRApplicationVersionModel(id=3, application_key="mock_app_key3", version=1)

    gr_provider_response_model = GRProviderResponseModel(
        id=1, guardrail_id=1, guardrail_provider=GuardrailProvider.AWS,
        response_data={"AWS": {"success": True, "response": {"guardrail_id": 1}}})

    from api.guardrails.providers.backend.bedrock import BedrockGuardrailProvider
    with (patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name, patch.object(
        mock_guardrail_repository, 'update_record', return_value=update_guardrail_view
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_application_repository, 'get_all', return_value=[gr_app_model_existing,  gr_app_model_to_delete]
    ) as mock_gr_app_get_all_record, patch.object(
        mock_guardrail_application_repository, 'create_record', return_value=gr_app_model_to_add
    ) as mock_gr_app_create_record, patch.object(
        mock_guardrail_application_repository, 'delete_record', return_value=gr_app_model_to_delete
    ) as mock_gr_app_delete_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[gr_app_version_model_to_bump1, gr_app_version_model_to_bump2]
    ) as mock_gr_app_version_get_all, patch.object(
        mock_guardrail_app_version_repository, 'create_record', return_value=gr_app_version_model_to_add
    ) as mock_gr_app_version_create_record, patch.object(
        mock_gr_config_repository, 'get_all', return_value=[gr_config_model_to_update, gr_config_model_to_delete]
    ) as mock_gr_config_get_all,  patch.object(
        mock_gr_config_repository, 'create_record', return_value=gr_config_model_to_add
    ) as mock_gr_config_create_record, patch.object(
        mock_gr_config_repository, 'update_record', return_value=gr_config_model_to_update
    ) as mock_gr_config_update_record, patch.object(
        mock_gr_config_repository, 'delete_record', return_value=gr_config_model_to_delete
    ) as mock_gr_config_delete_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_model]
    ) as mock_gr_connection_get_all, patch.object(
        BedrockGuardrailProvider, 'update_guardrail', return_value=(True, {"updated": True})
    ) as mock_bedrock_guardrail_update, patch.object(
        mock_gr_provider_response_repository, 'get_all', return_value=[gr_provider_response_model]
    ) as mock_gr_provider_response_get_all):
        # Call the method under test
        result = await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == update_guardrail_view.name
        gr_config_view_to_delete.id = 2
        assert result.guardrail_configs == update_guardrail_view.guardrail_configs
        assert result.application_keys == update_guardrail_view.application_keys
        assert result.guardrail_connections == update_guardrail_view.guardrail_connections
        assert result.guardrail_provider_response == update_guardrail_view.guardrail_provider_response
        assert mock_guardrail_update_record.called
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_app_get_all_record.called
        assert mock_gr_app_create_record.called
        assert mock_gr_app_delete_record.called
        assert mock_gr_app_version_get_all.called
        assert mock_guardrail_app_version_repository.update_record.call_count == 2
        assert mock_gr_app_version_create_record.called
        assert mock_gr_config_get_all.called
        assert mock_gr_config_create_record.called
        assert mock_gr_config_update_record.called
        assert mock_gr_config_delete_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_update.called
        assert mock_gr_provider_response_get_all.called


@pytest.mark.asyncio
async def test_update_guardrail_when_connection_is_updated(
        guardrail_service, mock_guardrail_repository, mock_guardrail_application_repository,
        mock_guardrail_app_version_repository, mock_gr_config_repository, mock_guardrail_connection_service,
        mock_gr_provider_response_repository):

    update_guardrail_view = GuardrailView(**guardrail_view_json)

    gr_config_view = GRConfigView(**guardrail_config_json)
    gr_config_view.id = 1
    gr_config_view.guardrail_provider_connection_name = "gr_connection_2"

    update_guardrail_view.guardrail_configs = [gr_config_view]
    update_guardrail_view.application_keys = ["mock_app_key1"]

    guardrail_model = GuardrailModel(id=1, name="mock_guardrail", description="mock description", version=1)
    gr_app_model = GRApplicationModel(id=1, guardrail_id=1, application_key="mock_app_key1")

    gr_config_model_updated_with_new_connection = GRConfigModel(**gr_config_view.model_dump())
    gr_config_model_existing_with_old_connection = GRConfigModel(**gr_config_view.model_dump())
    gr_config_model_existing_with_old_connection.guardrail_provider_connection_name = "gr_connection_1"

    gr_connection_model_to_detach = GRConnectionModel(**gr_connection_view.model_dump())
    gr_connection_model_to_attach = GRConnectionModel(**gr_connection_view.model_dump())
    gr_connection_model_to_attach.id = 2
    gr_connection_model_to_attach.name = "gr_connection_2"

    gr_app_version_model = GRApplicationVersionModel(id=1, application_key="mock_app_key1", version=1)

    gr_provider_response_model = GRProviderResponseModel(
        id=1, guardrail_id=1, guardrail_provider=GuardrailProvider.AWS,
        response_data={"AWS": {"success": True, "response": {"guardrail_id": 1}}})

    from api.guardrails.providers.backend.bedrock import BedrockGuardrailProvider
    with (patch.object(
        mock_guardrail_repository, 'update_record', return_value=update_guardrail_view
    ) as mock_guardrail_update_record, patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=guardrail_model
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_repository, 'list_records', return_value=([guardrail_view], 1)
    ) as mock_guardrail_get_by_name,patch.object(
        mock_guardrail_application_repository, 'get_all', return_value=[gr_app_model]
    ) as mock_gr_app_get_all_record, patch.object(
        mock_guardrail_app_version_repository, 'get_all', return_value=[gr_app_version_model]
    ) as mock_gr_app_version_get_all, patch.object(
        mock_gr_config_repository, 'get_all', return_value=[gr_config_model_existing_with_old_connection]
    ) as mock_gr_config_get_all, patch.object(
        mock_gr_config_repository, 'update_record', return_value=gr_config_model_updated_with_new_connection
    ) as mock_gr_config_update_record, patch.object(
        mock_guardrail_connection_service, 'get_all', return_value=[gr_connection_model_to_detach, gr_connection_model_to_attach]
    ) as mock_gr_connection_get_all, patch.object(
        BedrockGuardrailProvider, 'create_guardrail', return_value=(True, {"guardrail_id": 1})
    ) as mock_bedrock_guardrail_create, patch.object(
        BedrockGuardrailProvider, 'delete_guardrail', return_value=(True, {"deleted": True})
    ) as mock_bedrock_guardrail_delete, patch.object(
        mock_gr_provider_response_repository, 'get_all', return_value=[gr_provider_response_model]
    ) as mock_gr_provider_response_get_all):
        # Call the method under test
        result = await guardrail_service.update(1, update_guardrail_view)

        # Assertions
        assert result.id == 1
        assert result.name == update_guardrail_view.name
        assert result.guardrail_configs == update_guardrail_view.guardrail_configs
        assert result.application_keys == update_guardrail_view.application_keys
        assert result.guardrail_connections == update_guardrail_view.guardrail_connections
        assert result.guardrail_provider_response == update_guardrail_view.guardrail_provider_response
        assert mock_guardrail_update_record.called
        assert mock_get_record_by_id.called
        assert mock_guardrail_get_by_name.called
        assert mock_gr_app_get_all_record.called
        assert mock_gr_app_version_get_all.called
        assert mock_gr_config_get_all.called
        assert mock_gr_config_update_record.called
        assert mock_gr_connection_get_all.called
        assert mock_bedrock_guardrail_create.called
        assert mock_bedrock_guardrail_delete.called
        assert mock_gr_provider_response_get_all.called


@pytest.mark.asyncio
async def test_update_guardrail_when_name_already_exists(guardrail_service, mock_guardrail_repository):
    update_guardrail_view = GuardrailView(**guardrail_view_json)
    update_guardrail_view.guardrail_configs = [gr_config_view]
    update_guardrail_view.application_keys = ["mock_app_key1", "mock_app_key2"]
    with patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=GuardrailView(id=2)
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
async def test_delete_guardrail_connection(guardrail_service, mock_guardrail_repository):
    with patch.object(
            mock_guardrail_repository, 'delete_record', return_value=None
    ) as mock_delete_record, patch.object(
        mock_guardrail_repository, 'get_record_by_id', return_value=GuardrailView()
    ) as mock_get_record_by_id:
        # Call the method under test
        await guardrail_service.delete(1)

        # Assertions
        assert mock_delete_record.called
        assert mock_get_record_by_id.called
