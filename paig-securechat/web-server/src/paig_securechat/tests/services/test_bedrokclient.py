import unittest
from services.Bedrock_Application.BedrockClient import BedrockClient
from unittest.mock import patch
from core import config


class TestBedrockClient(unittest.TestCase):
    def setup_class(self):
        self.bedrock_instance = BedrockClient("sales_model")

    @patch('services.Bedrock_Application.BedrockClient.BedrockClient._execute_prompt')
    def test_ask_prompt_with_temperature(self, mock_execute_prompt):
        mock_execute_prompt.return_value =  ("reply", None)

        question = "what is perrys salary?"
        temperature = 0.5
        conversation_messages= [
            {'content': 'what is perrys salary?', 'type': 'prompt'},
            {'content': 'Not Allowed', 'type': 'reply'},
            {'content': 'What is Governance?', 'type': 'prompt'},
            {'content': 'To have control', 'type': 'reply'}]
        answer, source_metadata = self.bedrock_instance.ask_prompt(question, temperature=temperature)

        self.assertIsNotNone(answer)

        answer, source_metadata = self.bedrock_instance.ask_prompt(question, conversation_messages=conversation_messages, temperature=temperature)

        self.assertIsNotNone(answer)

    @patch('services.Bedrock_Application.BedrockClient.BedrockClient._execute_prompt')
    def test_ask_prompt_without_temperature(self, mock_execute_prompt):
        mock_execute_prompt.return_value = ("reply", None)
        question = "What is Governance?"

        answer, source_metadata = self.bedrock_instance.ask_prompt(question)

        self.assertIsNotNone(answer)