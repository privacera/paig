from .factory.crypto_factory import get_crypto_service

crypto_service = get_crypto_service()

async def encrypt_target_creds(headers: dict):
    auth_header, auth_value  = locate_auth_header(headers)
    if auth_header and auth_value:
        headers[auth_header] = await crypto_service.encrypt(auth_value)
    return headers

async def decrypt_target_creds(headers: dict):
    auth_header, auth_value = locate_auth_header(headers)
    if auth_header and auth_value:
        headers[auth_header] = await crypto_service.decrypt(auth_value)
    return headers


def locate_auth_header(headers: dict):
    existing_auth_key = next((key for key in headers.keys() if key.lower() == 'authorization'), None)
    if existing_auth_key:
        return existing_auth_key, headers[existing_auth_key]
    return None, None