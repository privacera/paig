# Initialize a cache variable for the CryptoService import
_crypto_service = None


def get_crypto_service():
    global _crypto_service

    if _crypto_service is None:
        # Only import the module the first time this function is called
        from .crypto_service import CryptoService
        _crypto_service = CryptoService()

    return _crypto_service