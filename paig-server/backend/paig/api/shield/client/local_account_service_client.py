from api.shield.interfaces.account_service_interface import IAccountServiceClient
from core.utils import SingletonDepends


class LocalAccountServiceClient(IAccountServiceClient):
    """
    Local client implementation for fetching encryption keys.

    Methods:
        get_all_encryption_keys(tenant_id):
            Retrieves all encryption keys for the specified tenant from a local data source.
    """

    def __init__(self):
        """
        Initialize the local account service client.
        """
        from api.encryption.services.encryption_key_service import EncryptionKeyService
        self.encryption_key_service: EncryptionKeyService = SingletonDepends(EncryptionKeyService)

    async def get_all_encryption_keys(self, tenant_id):
        """
        Retrieve all encryption keys for a specific tenant from the underlying data source.

        Args:
            tenant_id (str): The identifier of the tenant whose encryption keys are to be fetched.

        Returns:
            List[str]: A list of encryption keys associated with the specified `tenant_id`.
        """
        from api.encryption.api_schemas.encryption_key import EncryptionKeyFilter
        result = await self.encryption_key_service.list_encryption_keys(EncryptionKeyFilter(), 0, 10, [])
        result_list = []
        for key in result.content:
            key_dict = {"id": key.id, "keyStatus": key.key_status, "keyType": key.key_type,
                        "publicKeyValue": key.public_key, "privateKeyValue": key.private_key, "tenantId": tenant_id}
            result_list.append(key_dict)
        # create list of dictionary from result
        return result_list

