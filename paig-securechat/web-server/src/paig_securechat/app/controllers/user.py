from app.db_operations import UserRepository
from core.exceptions import InternalServerError
import logging
logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login_user(self, user_name):
        try:
            if user_name is None or user_name == "":
                raise InternalServerError("User name is empty")
            user = await self.user_repository.get_user_by_user_name(user_name)
            if user is None:
                user_params = {
                    "user_name": user_name,
                }
                user = await self.user_repository.create_user(user_params)
            return {"user_id": user.user_id, "user_name": user.user_name}
        except Exception as err:
            logging.error(f"Error occurred while logging in user. {err}")
            raise InternalServerError(f"Error occurred while logging in user. {err}")

    async def get_user(self, user):
        user = await self.user_repository.get_user(user_name=user['user_name'], user_id=user['user_id'])
        if user is None:
            return None
        return {"user_id": user.user_id, "user_name": user.user_name}

    async def get_user_by_user_name(self, user):
        user = await self.user_repository.get_user_by_user_name(user_name=user['user_name'])
        if user is None:
            return None
        return {"user_id": user.user_id, "user_name": user.user_name}