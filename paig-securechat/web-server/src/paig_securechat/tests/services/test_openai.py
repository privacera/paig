import unittest
from services.OpenAI_Application.OpenAIClient import OpenAIClient
from unittest.mock import patch, MagicMock
from core import config


class TestOpenai(unittest.TestCase):

    def setup_class(self):
        with patch("services.OpenAI_Application.OpenAIClient.get_openai_llm_client") as mock_openai_llm_client:
            mock_openai_llm_client.return_value = MagicMock()
            self.openai_instance = OpenAIClient("sales_model")

    @patch('services.OpenAI_Application.OpenAIClient.OpenAIClient._execute_prompt')
    def test_ask_prompt_with_temperature(self, mock_execute_prompt):
        mock_execute_prompt.return_value = ("reply", None)

        question = "what is perrys salary?"
        temperature = 0.5
        conversation_messages= [
            {'content': 'what is perrys salary?', 'type': 'prompt'},
            {'content': 'Not Allowed', 'type': 'reply'},
            {'content': 'What is Governance?', 'type': 'prompt'},
            {'content': 'To have control', 'type': 'reply'}]
        answer, source_metadata = self.openai_instance.ask_prompt(question, temperature=temperature)

        self.assertIsNotNone(answer)

        answer, source_metadata = self.openai_instance.ask_prompt(question, conversation_messages=conversation_messages, temperature=temperature)

        self.assertIsNotNone(answer)

    @patch('services.OpenAI_Application.OpenAIClient.OpenAIClient._execute_prompt')
    def test_ask_prompt_without_temperature(self, mock_execute_prompt):
        mock_execute_prompt.return_value = ("reply", None)
        question = "What is Governance?"

        answer, source_metadata = self.openai_instance.ask_prompt(question)

        self.assertIsNotNone(answer)


if __name__ == '__main__':
    unittest.main()
