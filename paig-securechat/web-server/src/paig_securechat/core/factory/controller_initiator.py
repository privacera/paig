from functools import partial
from fastapi import Depends
from app.controllers import AIApplicationController, UserController, ConversationController, HealthController
from app.db_models import User, Messages, Conversations
from app.db_operations import UserRepository, MessageRepository, ConversationRepository
from core.database import get_session
from core.database.session import async_session_factory

from core import llm_constants


class ControllerInitiator:

    user_repository = partial(UserRepository, User)
    message_repository = partial(MessageRepository, Messages)
    conversation_repository = partial(ConversationRepository, Conversations)
    # initiate model controller

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(
            user_repository=self.user_repository(db_session=db_session)
        )

    def get_conversation_controller(self, db_session=Depends(get_session)):
        return ConversationController(
            conversation_repository=self.conversation_repository(db_session=db_session),
            message_repository=self.message_repository(db_session=db_session),
            llm_AI_application_service=llm_constants.AI_application
        )

    def get_AI_application_controller(self):
        return AIApplicationController(llm_AI_application_service=llm_constants.AI_application)

    def get_health_controller(self, db_session=Depends(get_session)):
        return HealthController(db_session=db_session)
