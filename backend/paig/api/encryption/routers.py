from fastapi import APIRouter

from api.encryption.routes.encryption_key_router import encryption_key_router

encryption_router = APIRouter()
encryption_router.include_router(encryption_key_router, prefix="/keys", tags=["Encryption Keys"])
