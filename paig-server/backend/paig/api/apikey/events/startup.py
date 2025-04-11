import sys
from core.db_session import session, set_session_context, reset_session_context
from core.exceptions import NotFoundException
from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from api.apikey.database.db_operations.paig_level1_encryption_key_repository import PaigLevel1EncryptionKeyRepository
from api.apikey.database.db_operations.paig_level2_encryption_key_repository import PaigLevel2EncryptionKeyRepository


async def create_level1_encryption_keys_if_not_exists():
    try:
        paig_level1_encryption_key_repository = PaigLevel1EncryptionKeyRepository()
        level1_encryption_key_service = PaigLevel1EncryptionKeyService(
            paig_level1_encryption_key_repository=paig_level1_encryption_key_repository
        )
        level1_api_key = await level1_encryption_key_service.get_active_paig_level1_encryption_key()
        if not level1_api_key:
            await level1_encryption_key_service.create_paig_level1_encryption_key()
            await session.commit()
            print("Level1 encryption key created successfully")
        else:
            print("Level1 encryption key already exists")
    except Exception as e:
        print(f"An error occurred during creating Level1 "
              f"encryption key: {e}")
        sys.exit(f"An error occurred during creating Level1 "
                 f"encryption key: {e}")


async def create_level2_encryption_keys_if_not_exists():
    try:
        paig_level2_encryption_key_repository = PaigLevel2EncryptionKeyRepository()
        level2_encryption_key_service = PaigLevel2EncryptionKeyService(
            paig_level2_encryption_key_repository=paig_level2_encryption_key_repository
        )
        level2_api_key = await level2_encryption_key_service.get_active_paig_level2_encryption_key()
        if not level2_api_key:
            await level2_encryption_key_service.create_paig_level2_encryption_key()
            await session.commit()
            print(f"Level2 encryption key created successfully")
        else:
            print(f"Level2 encryption key already exists")
    except Exception as e:
        print(f"An error occurred during creating Level2 "
              f"encryption key: {e}")
        sys.exit(f"An error occurred during creating Level2 "
                 f"encryption key: {e}")
