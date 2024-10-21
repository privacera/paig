import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from unittest.mock import patch, MagicMock
from sqlalchemy.orm.exc import NoResultFound
from core.security.authentication import get_auth_user


from core.constants import BASE_ROUTE

@patch('app.controllers.conversation.ConversationController.send_prompt', MagicMock(return_value=('yes', None)))
class TestConversationRouter:

    def setup_class(self):
        # Initialize the FastAPI test client
        # Define data that will be shared across test functions
        self.user_id = 1
        self.user_name = 'test'
        self.ai_application_name = "hr_confidential"
        self.prompt = "I need to test"
        self.create_conversation_data = {
            "prompt": self.prompt,
            "ai_application_name": self.ai_application_name
        }

    async def create_conversation(self, client: AsyncClient, app: FastAPI):
        dic = {
            "user_name": self.user_name
        }
        response = await client.post(f"{BASE_ROUTE}/user/login", data=json.dumps(dic))
        self.user_id = response.json()['user_id']
        app.dependency_overrides[get_auth_user] = lambda: {"user_id": self.user_id}
        url = f"{BASE_ROUTE}/conversations/prompt"
        response = await client.post(
            url, data=json.dumps(self.create_conversation_data)
        )
        return response

    @pytest.mark.asyncio
    async def test_create_conversation(self, client: AsyncClient, app: FastAPI):
        dic = {
            "user_name": self.user_name
        }
        response = await client.post(f"{BASE_ROUTE}/user/login", data=json.dumps(dic))
        self.user_id = response.json()['user_id']
        app.dependency_overrides[get_auth_user] = lambda: {"user_id": self.user_id}
        url = f"{BASE_ROUTE}/conversations/prompt"
        response = await client.post(
            url, data=json.dumps(self.create_conversation_data)
        )
        assert response.json()['ai_application_name'] == "hr_confidential"
        assert len(response.json()['messages']) != 0

    @pytest.mark.asyncio
    async def test_get_conversations(self, client: AsyncClient, app: FastAPI):
        response = await self.create_conversation(client, app)
        create_response = response.json()
        conversation_uuid = create_response['conversation_uuid']
        url = f"{BASE_ROUTE}/conversations?user_id={str(self.user_id)}"
        response = await client.get(
            url,
        )
        response = response.json()
        assert response['items'][0]['conversation_uuid'] == conversation_uuid

        with patch('core.factory.database_initiator.BaseOperations.get_all',
                   side_effect=Exception("Something went wrong")):
            url = f"{BASE_ROUTE}/conversations?user_id={str(self.user_id)}"
            response = await client.get(url,)
            assert response.status_code == 500

        with patch('core.factory.database_initiator.BaseOperations.get_all',
                   side_effect=NoResultFound("Not Found")):
            url = f"{BASE_ROUTE}/conversations?user_id={str(self.user_id)}&imit=1"
            response = await client.get(url,)
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_messages_by_conversation_id(self, client: AsyncClient, app: FastAPI):
        response = await self.create_conversation(client, app)
        create_response = response.json()
        messages_length = len(create_response['messages'])
        conversation_uuid = create_response['conversation_uuid']
        response = await client.get(
            f"{BASE_ROUTE}/conversations/{conversation_uuid}",
        )
        response = response.json()
        assert len(response['messages']) == messages_length

        response = await client.get(
            f"{BASE_ROUTE}/conversations/random-string",
        )
        assert response.status_code == 404

        with patch('app.db_operations.message_repository.MessageRepository.get_messages_count',
                   side_effect=Exception("Something went wrong")):
            response = await client.get(
                f"{BASE_ROUTE}/conversations/{conversation_uuid}",
            )
        assert response.status_code == 500

        with patch('app.db_operations.message_repository.MessageRepository.get_messages_count',
                   side_effect=NoResultFound("Not Found")):
            response = await client.get(
                f"{BASE_ROUTE}/conversations/{conversation_uuid}",
            )
        assert response.status_code == 404



    @pytest.mark.asyncio
    async def test_delete_conversation(self, client: AsyncClient, app: FastAPI):
        response = await self.create_conversation(client, app)
        create_response = response.json()
        conversation_uuid = create_response['conversation_uuid']
        response = await client.delete(
            f"{BASE_ROUTE}/conversations/{conversation_uuid}",
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{BASE_ROUTE}/conversations/{conversation_uuid}",
        )
        assert response.status_code == 404

        response = await client.delete(
            f"{BASE_ROUTE}/conversations/123-123",
        )
        assert response.status_code == 404

        with patch('app.db_operations.conversation_repository.ConversationRepository.delete_conversation',
                   side_effect=Exception("Something went wrong")):
            response = await client.delete(
                f"{BASE_ROUTE}/conversations/{conversation_uuid}",
            )
        assert response.status_code == 500


    @pytest.mark.asyncio
    async def test_ask_prompt(self, client: AsyncClient, app: FastAPI):
        response = await self.create_conversation(client, app)
        create_response = response.json()
        conversation_uuid = create_response['conversation_uuid']
        url = f"{BASE_ROUTE}/conversations/{conversation_uuid}/prompt"
        response = await client.post(
            url, data=json.dumps(self.create_conversation_data)
        )
        response = response.json()
        assert len(response) == 2

        url = f"{BASE_ROUTE}/conversations/random_string/prompt"
        response = await client.post(
            url, data=json.dumps(self.create_conversation_data)
        )
        assert response.status_code == 404

        url = f"{BASE_ROUTE}/conversations/{conversation_uuid}/prompt"
        with patch('app.db_operations.message_repository.MessageRepository.create_message',
                   side_effect=Exception("Something went wrong")):
            response = await client.post(
                url, data=json.dumps(self.create_conversation_data)
            )
        assert response.status_code == 500

        url = f"{BASE_ROUTE}/conversations/{conversation_uuid}/prompt"
        with patch('app.db_operations.conversation_repository.ConversationRepository.get_conversation_by_uuid',
                   side_effect=Exception("Something went wrong")):
            response = await client.post(
                url, data=json.dumps(self.create_conversation_data)
            )
        assert response.status_code == 500

        with patch('app.db_operations.conversation_repository.ConversationRepository.get_conversation_by_uuid',
                   side_effect=NoResultFound("Not Found")):
            response = await client.post(
                url, data=json.dumps(self.create_conversation_data)
            )
        assert response.status_code == 404
