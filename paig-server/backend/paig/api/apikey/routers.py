from fastapi import APIRouter
from api.apikey.routes.paig_api_key_router import paig_api_key_router

api_key_router = APIRouter()

api_key_router.include_router(paig_api_key_router)