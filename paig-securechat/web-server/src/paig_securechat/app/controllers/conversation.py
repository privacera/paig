from app.db_operations import ConversationRepository
from app.db_operations import MessageRepository
from core.utils import get_uuid, generate_title
import logging
from core.exceptions import NotFoundException, InternalServerError
from sqlalchemy.orm.exc import NoResultFound
from core.config import load_config_file
logger = logging.getLogger(__name__)


class ConversationController:
    def __init__(self, conversation_repository: ConversationRepository, message_repository: MessageRepository, llm_AI_application_service):
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.AI_application_service = llm_AI_application_service
        self.config = load_config_file()

    async def get_conversations(self, user_id, skip, limit):
        res = dict()
        skip = 0 if skip is None else skip
        res['offset'] = skip
        try:
            total = await self.conversation_repository.get_conversations_count(user_id=user_id)
            limit = total if limit is None else limit
            items = await self.conversation_repository.get_conversations(user_id=user_id, skip=skip, limit=limit)
            res['items'] = items
            res['total'] = total
            res['limit'] = limit
            return res
        except NoResultFound:
            logger.error(f"Conversations with user id {user_id} not found")
            raise NotFoundException(f"Conversations with user id {user_id} not found")
        except Exception as err:
            logger.error(f"Error occurred while fetching conversations {err}")
            raise InternalServerError(f"Error occurred while fetching conversations {err}")

    async def delete_conversation(self, conversation_uuid: str):
        try:
            await self.conversation_repository.delete_conversation(conversation_uuid=conversation_uuid)
            return f"Conversation with id {conversation_uuid} deleted successfully"
        except NoResultFound:
            logger.error(f"No active conversation with uuid {conversation_uuid} found")
            raise NotFoundException(f"No active conversation with uuid {conversation_uuid} found")
        except Exception as err:
            logger.error(f"Error occurred while deleting conversation {err}")
            raise InternalServerError(f"Error occurred while deleting conversation {err}")

    async def get_messages_by_conversation_uuid(self, user_id, conversation_uuid: str, skip: int = 0, limit: int = 100):

        try:
            conversation_info = await self.conversation_repository.get_conversation_by_uuid(
                conversation_uuid=conversation_uuid, user_id=user_id)
            conversation_id = conversation_info.id
            ai_application_name = conversation_info.ai_application_name
        except NoResultFound:
            logger.error(f"No active conversation with uuid {conversation_uuid} found")
            raise NotFoundException(f"No active conversation with uuid {conversation_uuid} found")

        res = dict()
        skip = 0 if skip is None else skip
        res['offset'] = skip
        try:
            total = await self.message_repository.get_messages_count(conversation_id=conversation_id)
            limit = total if limit is None else limit
            messages = await self.message_repository.get_messages_by_conversation_id(conversation_id=conversation_id, skip=skip, limit=limit)
            res['limit'] = limit
            res['total'] = total
            res['conversation_uuid'] = conversation_uuid
            res['messages'] = messages
            res['ai_application_name'] = ai_application_name
            return res
        except NoResultFound:
            logger.error(f"Messages with conversation_uuid {conversation_uuid} not found")
            raise NotFoundException(f"Messages with conversation_uuid {conversation_uuid} not found")
        except Exception as err:
            logger.error(f"Error occurred while fetching messages {err}")
            raise InternalServerError(f"Error occurred while fetching messages {err}")

    async def create_conversation(self, user_id: int, prompt: str, ai_application_name: str):
        conversation_uuid = get_uuid()
        conversation_params = {
            "ai_application_name": ai_application_name,
            "user_id": user_id,
            "conversation_uuid": conversation_uuid,
            "title": generate_title([prompt])
        }
        resp = dict()
        resp['messages'] = list()
        try:
            new_conversation_resp = await self.conversation_repository.create_conversation(conversation_params)
            resp['conversation_uuid'] = new_conversation_resp.conversation_uuid
            resp['ai_application_name'] = new_conversation_resp.ai_application_name
            resp['created_on'] = new_conversation_resp.created_on
            resp['title'] = new_conversation_resp.title
        except Exception as err:
            logger.error(f"Error occurred while creating new conversation {err}")
            raise InternalServerError(f"Error occurred while creating new conversation {err}")
        try:
            ask_prompt_resp = await self.ask_prompt(user_id, conversation_uuid, prompt)
            resp['messages'] = ask_prompt_resp
        except Exception as err:
            logger.error(f"Error occurred while asking prompt {err}")
        return resp

    async def ask_prompt(self, user_id, conversation_uuid: str, prompt: str):
        resp = list()
        try:
            conversation_info = await self.conversation_repository.get_conversation_by_uuid(
                conversation_uuid=conversation_uuid, user_id=user_id)
            ai_application_name = conversation_info.ai_application_name
            conversation_id = conversation_info.id
            user_name = conversation_info.user.user_name
        except NoResultFound:
            logger.error(f"No active conversation with uuid {conversation_uuid} found")
            raise NotFoundException(f"No active conversation with uuid {conversation_uuid} found")
        except Exception as err:
            logger.error(f"Error occurred while fetching conversation info {err}")
            raise InternalServerError(f"Error occurred while fetching conversation info {err}")

        prompt_uuid = get_uuid()
        prompt_params = {
            "conversation_id": conversation_id,
            "content": prompt,
            "type": "prompt",
            "message_uuid": prompt_uuid,
            "prompt_id": None
        }
        # insert prompt message
        try:
            create_prompt_resp = await self.message_repository.create_message(prompt_params)
            resp.append(create_prompt_resp.__dict__)
        except Exception as err:
            logger.error(f"Error occurred while creating prompt message {err}")
            raise InternalServerError(f"Error occurred while creating prompt message {err}")

        history_limit = 5
        if (ai_application_name in self.config['AI_applications'] and 'conversation_history_k' in self.config['AI_applications'][ai_application_name]):
            history_limit = int(self.config['AI_applications'][ai_application_name].get('conversation_history_k'))
        try:
            conversation_messages = await self.message_repository.get_messages_by_conversation_id(
                conversation_id=conversation_id,
                limit=history_limit
                )
            conversation_messages = list(map(lambda x: {'content': x.content, 'type': x.type}, conversation_messages))
            conversation_messages.reverse()
        except:
            conversation_messages = None
        reply = self.send_prompt(prompt, ai_application_name, conversation_messages, user_name)

        reply_uuid = get_uuid()
        reply_params = {
            "conversation_id": conversation_id,
            "content": reply,
            "type": "reply",
            "message_uuid": reply_uuid,
            "prompt_id": prompt_uuid
        }
        try:
            create_reply_resp = await self.message_repository.create_message(reply_params)
            resp.append(create_reply_resp.__dict__)
        except Exception as err:
            logger.error(f"Error occurred while creating reply message {err}")

        return resp

    def send_prompt(self, prompt, ai_application_name, conversation_messages=None, user_name=None):
        AI_application_service = self.AI_application_service.get_service(ai_application_name)
        response = AI_application_service.ask_prompt(prompt=prompt, conversation_messages=conversation_messages, user_name=user_name)
        return response
