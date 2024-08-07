from privacera_shield_common.encryption import DataEncryptor
import base64


class DataProtectController:
    async def decrypt_list_messages(self, encryption_service, params):
        encryption_key = params.encryptionKeyId
        messages = params.encryptedDataList
        keys = await encryption_service.get_encryption_key_by_id(encryption_key)
        encryptor = DataEncryptor(public_key=keys.public_key, private_key=keys.private_key)
        resp = dict()
        resp['status'] = 0
        decrypted_data = list()
        for i in messages:
            encoded_data = base64.b64encode((encryptor.decrypt_data(i)).encode("ascii"))
            decrypted_data.append(encoded_data)
        resp['decryptedDataList'] = decrypted_data
        return resp
