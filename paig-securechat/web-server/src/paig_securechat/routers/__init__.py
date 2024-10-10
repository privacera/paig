from fastapi import APIRouter

from routers.conversations.conversations import conversations_router
from routers.AI_applications.AI_applications import AI_applications_router
from routers.user.user import user_router
from routers.server.server import server_router

from core.constants import BASE_ROUTE

router = APIRouter()
router.include_router(conversations_router, prefix=f"{BASE_ROUTE}/conversations", tags=["Conversations"])
router.include_router(AI_applications_router, prefix=f"{BASE_ROUTE}/ai_applications", tags=["Models"])
router.include_router(user_router, prefix=f"{BASE_ROUTE}/user", tags=["User"])
router.include_router(server_router, prefix=f"{BASE_ROUTE}/server", tags=["Server"])

__all__ = ["router"]
