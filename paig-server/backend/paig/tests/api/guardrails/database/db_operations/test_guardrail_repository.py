from unittest.mock import patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails.database.db_models.gr_connection_model import GuardrailProvider
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRApplicationModel, \
    GRApplicationVersionModel, GRConfigModel, GRProviderResponseModel
from api.guardrails.database.db_models.guardrail_view_model import GuardrailViewModel
from api.guardrails.database.db_operations.guardrail_repository import GuardrailRepository, GRApplicationRepository, \
    GRApplicationVersionRepository, GRConfigRepository, GRProviderResponseRepository, GuardrailViewRepository


@pytest.fixture
def mock_guardrail_repository():
    return GuardrailRepository()


@pytest.mark.asyncio
async def test_get_guardrail(mock_guardrail_repository):
    mock_guardrail = GuardrailModel(
        id=1,
        name="mock_name",
        description="mock_description",
        version=1
    )

    with patch.object(GuardrailRepository, 'get_all', return_value=[mock_guardrail]):
        result = await mock_guardrail_repository.get_all()
        assert len(result) == 1
        assert result[0].name == "mock_name"
        assert result[0].description == "mock_description"
        assert result[0].version == 1


@pytest.mark.asyncio
async def test_get_guardrail_by_id(mock_guardrail_repository):
    key_id = 1
    mock_guardrail = GuardrailModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        version=1
    )

    with patch.object(GuardrailRepository, 'get_record_by_id', return_value=mock_guardrail):
        result = await mock_guardrail_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.version == 1


@pytest.mark.asyncio
async def test_get_guardrail_by_id_not_found(mock_guardrail_repository):
    key_id = 0

    with patch.object(GuardrailRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail(mock_guardrail_repository):
    mock_guardrail = GuardrailModel(
        id=1,
        name="mock_name",
        description="mock_description",
        version=1
    )

    with patch.object(GuardrailRepository, 'create', return_value=mock_guardrail):
        result = await mock_guardrail_repository.create(mock_guardrail)
        assert result.id == 1
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.version == 1


@pytest.mark.asyncio
async def test_update_guardrail(mock_guardrail_repository):
    key_id = 1
    mock_guardrail = GuardrailModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        version=1
    )

    with patch.object(GuardrailRepository, 'update', return_value=mock_guardrail):
        result = await mock_guardrail_repository.update(mock_guardrail)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.version == 1


@pytest.mark.asyncio
async def test_delete_guardrail(mock_guardrail_repository):
    key_id = 1
    mock_guardrail = GuardrailModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        version=1
    )

    with patch.object(GuardrailRepository, 'delete', return_value=None):
        result = await mock_guardrail_repository.delete(mock_guardrail)
        assert result is None


@pytest.fixture
def mock_guardrail_application_repository():
    return GRApplicationRepository()


@pytest.mark.asyncio
async def test_get_guardrail_application(mock_guardrail_application_repository):
    mock_guardrail_application = GRApplicationModel(
        id=1,
        guardrail_id=1,
        application_id=1,
        application_name="mock_app_name",
        application_key="mock_app_key"
    )

    with patch.object(GRApplicationRepository, 'get_all', return_value=[mock_guardrail_application]):
        result = await mock_guardrail_application_repository.get_all()
        assert len(result) == 1
        assert result[0].guardrail_id == 1
        assert result[0].application_name == "mock_app_name"
        assert result[0].application_key == "mock_app_key"


@pytest.mark.asyncio
async def test_get_guardrail_application_by_id(mock_guardrail_application_repository):
    key_id = 1
    mock_guardrail_application = GRApplicationModel(
        id=key_id,
        guardrail_id=1,
        application_id=1,
        application_name="mock_app_name",
        application_key="mock_app_key"
    )

    with patch.object(GRApplicationRepository, 'get_record_by_id', return_value=mock_guardrail_application):
        result = await mock_guardrail_application_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.application_name == "mock_app_name"
        assert result.application_key == "mock_app_key"


@pytest.mark.asyncio
async def test_get_guardrail_application_by_id_not_found(mock_guardrail_application_repository):
    key_id = 0

    with patch.object(GRApplicationRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_application_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail_application(mock_guardrail_application_repository):
    mock_guardrail_application = GRApplicationModel(
        id=1,
        guardrail_id=1,
        application_id=1,
        application_name="mock_app_name",
        application_key="mock_app_key"
    )

    with patch.object(GRApplicationRepository, 'create', return_value=mock_guardrail_application):
        result = await mock_guardrail_application_repository.create(mock_guardrail_application)
        assert result.id == 1
        assert result.guardrail_id == 1
        assert result.application_name == "mock_app_name"
        assert result.application_key == "mock_app_key"


@pytest.mark.asyncio
async def test_update_guardrail_application(mock_guardrail_application_repository):
    key_id = 1
    mock_guardrail_application = GRApplicationModel(
        id=key_id,
        guardrail_id=1,
        application_id=1,
        application_name="mock_app_name",
        application_key="mock_app_key"
    )

    with patch.object(GRApplicationRepository, 'update', return_value=mock_guardrail_application):
        result = await mock_guardrail_application_repository.update(mock_guardrail_application)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.application_name == "mock_app_name"
        assert result.application_key == "mock_app_key"


@pytest.mark.asyncio
async def test_delete_guardrail_application(mock_guardrail_application_repository):
    key_id = 1
    mock_guardrail_application = GRApplicationModel(
        id=key_id,
        guardrail_id=1,
        application_id=1,
        application_name="mock_app_name",
        application_key="mock_app_key"
    )

    with patch.object(GRApplicationRepository, 'delete', return_value=None):
        result = await mock_guardrail_application_repository.delete(mock_guardrail_application)
        assert result is None


@pytest.fixture
def mock_guardrail_application_version_repository():
    return GRApplicationVersionRepository()


@pytest.mark.asyncio
async def test_get_guardrail_application_version(mock_guardrail_application_version_repository):
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=1,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'get_all', return_value=[mock_guardrail_application_version]):
        result = await mock_guardrail_application_version_repository.get_all()
        assert len(result) == 1
        assert result[0].application_key == "mock_app_key"
        assert result[0].version == 1


@pytest.mark.asyncio
async def test_get_guardrail_application_version_by_id(mock_guardrail_application_version_repository):
    key_id = 1
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=key_id,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'get_record_by_id', return_value=mock_guardrail_application_version):
        result = await mock_guardrail_application_version_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.application_key == "mock_app_key"
        assert result.version == 1


@pytest.mark.asyncio
async def test_get_guardrail_application_version_by_id_not_found(mock_guardrail_application_version_repository):
    key_id = 0

    with patch.object(GRApplicationVersionRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_application_version_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail_application_version(mock_guardrail_application_version_repository):
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=1,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'create', return_value=mock_guardrail_application_version):
        result = await mock_guardrail_application_version_repository.create(mock_guardrail_application_version)
        assert result.id == 1
        assert result.application_key == "mock_app_key"
        assert result.version == 1


@pytest.mark.asyncio
async def test_update_guardrail_application_version(mock_guardrail_application_version_repository):
    key_id = 1
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=key_id,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'update', return_value=mock_guardrail_application_version):
        result = await mock_guardrail_application_version_repository.update(mock_guardrail_application_version)
        assert result.id == key_id
        assert result.application_key == "mock_app_key"
        assert result.version == 1


@pytest.mark.asyncio
async def test_delete_guardrail_application_version(mock_guardrail_application_version_repository):
    key_id = 1
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=key_id,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'delete', return_value=None):
        result = await mock_guardrail_application_version_repository.delete(mock_guardrail_application_version)
        assert result is None


@pytest.fixture
def mock_guardrail_config_repository():
    return GRConfigRepository()


@pytest.mark.asyncio
async def test_get_guardrail_config(mock_guardrail_config_repository):
    mock_guardrail_config = GRConfigModel(
        id=1,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_provider_connection_name="mock_connection_name",
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"}
    )

    with patch.object(GRConfigRepository, 'get_all', return_value=[mock_guardrail_config]):
        result = await mock_guardrail_config_repository.get_all()
        assert len(result) == 1
        assert result[0].guardrail_id == 1
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].guardrail_provider_connection_name == "mock_connection_name"
        assert result[0].config_type == "mock_config_type"
        assert result[0].config_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_config_by_id(mock_guardrail_config_repository):
    key_id = 1
    mock_guardrail_config = GRConfigModel(
        id=key_id,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_provider_connection_name="mock_connection_name",
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"}
    )

    with patch.object(GRConfigRepository, 'get_record_by_id', return_value=mock_guardrail_config):
        result = await mock_guardrail_config_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_provider_connection_name == "mock_connection_name"
        assert result.config_type == "mock_config_type"
        assert result.config_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_config_by_id_not_found(mock_guardrail_config_repository):
    key_id = 0

    with patch.object(GRConfigRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_config_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail_config(mock_guardrail_config_repository):
    mock_guardrail_config = GRConfigModel(
        id=1,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_provider_connection_name="mock_connection_name",
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"}
    )

    with patch.object(GRConfigRepository, 'create', return_value=mock_guardrail_config):
        result = await mock_guardrail_config_repository.create(mock_guardrail_config)
        assert result.id == 1
        assert result.guardrail_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_provider_connection_name == "mock_connection_name"
        assert result.config_type == "mock_config_type"
        assert result.config_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_update_guardrail_config(mock_guardrail_config_repository):
    key_id = 1
    mock_guardrail_config = GRConfigModel(
        id=key_id,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_provider_connection_name="mock_connection_name",
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"}
    )

    with patch.object(GRConfigRepository, 'update', return_value=mock_guardrail_config):
        result = await mock_guardrail_config_repository.update(mock_guardrail_config)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_provider_connection_name == "mock_connection_name"
        assert result.config_type == "mock_config_type"
        assert result.config_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_delete_guardrail_config(mock_guardrail_config_repository):
    key_id = 1
    mock_guardrail_config = GRConfigModel(
        id=key_id,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_provider_connection_name="mock_connection_name",
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"}
    )

    with patch.object(GRConfigRepository, 'delete', return_value=None):
        result = await mock_guardrail_config_repository.delete(mock_guardrail_config)
        assert result is None


@pytest.fixture
def mock_guardrail_provider_response_repository():
    return GRProviderResponseRepository()


@pytest.mark.asyncio
async def test_get_guardrail_provider_response(mock_guardrail_provider_response_repository):
    mock_guardrail_provider_response = GRProviderResponseModel(
        id=1,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        response_data={"mock_key": "mock_value"}
    )

    with patch.object(GRProviderResponseRepository, 'get_all', return_value=[mock_guardrail_provider_response]):
        result = await mock_guardrail_provider_response_repository.get_all()
        assert len(result) == 1
        assert result[0].guardrail_id == 1
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].response_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_provider_response_by_id(mock_guardrail_provider_response_repository):
    key_id = 1
    mock_guardrail_provider_response = GRProviderResponseModel(
        id=key_id,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        response_data={"mock_key": "mock_value"}
    )

    with patch.object(GRProviderResponseRepository, 'get_record_by_id', return_value=mock_guardrail_provider_response):
        result = await mock_guardrail_provider_response_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.response_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_provider_response_by_id_not_found(mock_guardrail_provider_response_repository):
    key_id = 0

    with patch.object(GRProviderResponseRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_provider_response_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail_provider_response(mock_guardrail_provider_response_repository):
    mock_guardrail_provider_response = GRProviderResponseModel(
        id=1,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        response_data={"mock_key": "mock_value"}
    )

    with patch.object(GRProviderResponseRepository, 'create', return_value=mock_guardrail_provider_response):
        result = await mock_guardrail_provider_response_repository.create(mock_guardrail_provider_response)
        assert result.id == 1
        assert result.guardrail_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.response_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_update_guardrail_provider_response(mock_guardrail_provider_response_repository):
    key_id = 1
    mock_guardrail_provider_response = GRProviderResponseModel(
        id=key_id,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        response_data={"mock_key": "mock_value"}
    )

    with patch.object(GRProviderResponseRepository, 'update', return_value=mock_guardrail_provider_response):
        result = await mock_guardrail_provider_response_repository.update(mock_guardrail_provider_response)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.response_data == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_delete_guardrail_provider_response(mock_guardrail_provider_response_repository):
    key_id = 1
    mock_guardrail_provider_response = GRProviderResponseModel(
        id=key_id,
        guardrail_id=1,
        guardrail_provider=GuardrailProvider.AWS,
        response_data={"mock_key": "mock_value"}
    )

    with patch.object(GRProviderResponseRepository, 'delete', return_value=None):
        result = await mock_guardrail_provider_response_repository.delete(mock_guardrail_provider_response)
        assert result is None


@pytest.fixture
def mock_guardrail_view_repository():
    return GuardrailViewRepository()


@pytest.mark.asyncio
async def test_get_guardrail_view(mock_guardrail_view_repository):
    mock_guardrail_view = GuardrailViewModel(
        id=1,
        name="mock_name",
        description="mock_description",
        version=1,
        application_keys="mock_application_key1,mock_application_key2",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_id=1,
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"},
        guardrail_provider_connection_name="mock_connection_name",
        guardrail_connection={"mock_key": "mock_value"},
        guardrail_provider_response={"mock_key": "mock_value"}
    )

    with patch.object(GuardrailViewRepository, 'get_all', return_value=[mock_guardrail_view]):
        result = await mock_guardrail_view_repository.get_all()
        assert len(result) == 1
        assert result[0].name == "mock_name"
        assert result[0].description == "mock_description"
        assert result[0].version == 1
        assert result[0].application_keys == "mock_application_key1,mock_application_key2"
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].guardrail_id == 1
        assert result[0].config_type == "mock_config_type"
        assert result[0].config_data == {"mock_key": "mock_value"}
        assert result[0].guardrail_provider_connection_name == "mock_connection_name"
        assert result[0].guardrail_connection == {"mock_key": "mock_value"}
        assert result[0].guardrail_provider_response == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_view_by_id(mock_guardrail_view_repository):
    key_id = 1
    mock_guardrail_view = GuardrailViewModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        version=1,
        application_keys="mock_application_key1,mock_application_key2",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_id=1,
        config_type="mock_config_type",
        config_data={"mock_key": "mock_value"},
        guardrail_provider_connection_name="mock_connection_name",
        guardrail_connection={"mock_key": "mock_value"},
        guardrail_provider_response={"mock_key": "mock_value"}
    )

    with patch.object(GuardrailViewRepository, 'get_record_by_id', return_value=mock_guardrail_view):
        result = await mock_guardrail_view_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.version == 1
        assert result.application_keys == "mock_application_key1,mock_application_key2"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_id == 1
        assert result.config_type == "mock_config_type"
        assert result.config_data == {"mock_key": "mock_value"}
        assert result.guardrail_provider_connection_name == "mock_connection_name"
        assert result.guardrail_connection == {"mock_key": "mock_value"}
        assert result.guardrail_provider_response == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_view_by_id_not_found(mock_guardrail_view_repository):
    key_id = 0

    with patch.object(GuardrailViewRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_view_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound
