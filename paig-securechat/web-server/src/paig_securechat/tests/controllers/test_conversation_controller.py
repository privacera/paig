import pytest
from unittest.mock import AsyncMock, MagicMock
from app.controllers.conversation import ConversationController, NotFoundException, NoResultFound

@pytest.fixture
def conversation_controller():
    conversation_repository_mock = AsyncMock()
    message_repository_mock = AsyncMock()
    AI_application_service_mock = AsyncMock()
    return ConversationController(conversation_repository_mock, message_repository_mock, AI_application_service_mock)

@pytest.mark.asyncio
async def test_get_conversations(conversation_controller):
    conversation_repository_mock = conversation_controller.conversation_repository
    conversation_repository_mock.get_conversations_count.return_value = 3
    conversation_repository_mock.get_conversations.return_value = [{'id': 1, 'title': 'Conversation 1'}, {'id': 2, 'title': 'Conversation 2'}]

    result = await conversation_controller.get_conversations(user_id=123, skip=0, limit=2)

    assert result['total'] == 3
    assert result['limit'] == 2
    assert len(result['items']) == 2

@pytest.mark.asyncio
async def test_get_conversations_not_found(conversation_controller):
    conversation_repository_mock = conversation_controller.conversation_repository
    conversation_repository_mock.get_conversations_count.side_effect = NoResultFound

    with pytest.raises(NotFoundException):
        await conversation_controller.get_conversations(user_id=123, skip=0, limit=2)

@pytest.mark.asyncio
async def test_create_conversation(conversation_controller):
    conversation_repository_mock = conversation_controller.conversation_repository
    message_repository_mock = conversation_controller.message_repository

    # Mocking dependencies
    conversation_repository_mock.create_conversation.return_value = MagicMock(
        conversation_uuid='12345', ai_application_name='TestApp', created_on='2022-01-01', title='Test Title'
    )
    message_repository_mock.create_message.side_effect = [
        MagicMock(message_uuid='67890', content='Prompt message'),
        MagicMock(message_uuid='ABCDE', content='Reply message')
    ]

    # Test case
    result = await conversation_controller.create_conversation(user_id=1, prompt='Test prompt', ai_application_name='TestApp')

    assert result['conversation_uuid'] == '12345'
    assert result['ai_application_name'] == 'TestApp'
    assert result['created_on'] == '2022-01-01'
    assert result['title'] == 'Test Title'