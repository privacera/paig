import logging
import sys

from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from core.db_session import session, set_session_context, reset_session_context
from core.exceptions import NotFoundException
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType
from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel
from api.encryption.database.db_operations.encryption_key_repository import EncryptionKeyRepository
from api.encryption.database.db_operations.encryption_master_key_repository import EncryptionMasterKeyRepository
from api.encryption.services.encryption_key_service import EncryptionKeyService, EncryptionKeyRequestValidator
from api.encryption.utils.master_key_generator import MasterKeyGenerator
from api.encryption.utils.secure_encryptor import SecureEncryptor

logger = logging.getLogger(__name__)


async def create_encryption_master_key_if_not_exists():
    try:
        encryption_master_key_repository = EncryptionMasterKeyRepository()

        try:
            await encryption_master_key_repository.get_active_encryption_master_key()
            print("Encryption Master Key already exists")
        except NotFoundException:
            master_key = MasterKeyGenerator.generate_master_key()
            master_key_model = EncryptionMasterKeyModel()
            master_key_model.status = 1
            master_key_model.key = master_key

            session.add(master_key_model)
            await session.commit()

            print("Encryption Master Key created successfully")
    except Exception as e:
        print(f"An error occurred during creating master key: {e}")
        sys.exit(f"An error occurred during creating master key: {e}")


async def create_encryption_keys_if_not_exists(encryption_key_service: EncryptionKeyService, key_type: EncryptionKeyType):
    try:
        try:
            await encryption_key_service.get_active_encryption_key_by_type(key_type)
            print(f"Default {key_type.value} encryption key already exists")
        except NotFoundException:
            await encryption_key_service.create_encryption_key(key_type)
            await session.commit()
            print(f"Default {key_type.value} encryption key created successfully")
    except Exception as e:
        print(f"An error occurred during creating default {key_type.value} "
              f"encryption key: {e}")
        sys.exit(f"An error occurred during creating default {key_type.value} "
                 f"encryption key: {e}")


async def create_default_encryption_keys_if_not_exists():
    encryption_key_service = None
    try:
        encryption_master_key_repository = EncryptionMasterKeyRepository()
        encryption_key_repository = EncryptionKeyRepository()
        secure_encryptor_factory = SecureEncryptorFactory(encryption_master_key_repository=encryption_master_key_repository)

        master_key = await encryption_master_key_repository.get_active_encryption_master_key()
        secure_encryptor = SecureEncryptor(master_key=master_key.key)
        encryption_key_request_validator = EncryptionKeyRequestValidator(
            encryption_key_repository=encryption_key_repository
        )

        encryption_key_service = EncryptionKeyService(
            encryption_key_repository=encryption_key_repository,
            secure_encryptor_factory=secure_encryptor_factory,
            encryption_key_request_validator=encryption_key_request_validator
        )
    except Exception as e:
        print(f"An error occurred during creating encryption_key_service: {e}")
        sys.exit(f"An error occurred during creating encryption_key_service: {e}")

    if encryption_key_service is not None:
        # Create MSG_PROTECT_SHIELD encryption key
        await create_encryption_keys_if_not_exists(encryption_key_service, EncryptionKeyType.MSG_PROTECT_SHIELD)

        # Create MSG_PROTECT_PLUGIN encryption key
        await create_encryption_keys_if_not_exists(encryption_key_service, EncryptionKeyType.MSG_PROTECT_PLUGIN)

        # Create CRDS_PROTECT_GUARDRAIL encryption key
        await create_encryption_keys_if_not_exists(encryption_key_service, EncryptionKeyType.CRDS_PROTECT_GUARDRAIL)


async def create_default_encryption_keys():
    context = set_session_context(session_id="encryption_startup")

    try:
        await create_encryption_master_key_if_not_exists()
        await create_default_encryption_keys_if_not_exists()
        await session.commit()
    except Exception as exception:
        raise exception
    finally:
        await session.remove()
        reset_session_context(context=context)
