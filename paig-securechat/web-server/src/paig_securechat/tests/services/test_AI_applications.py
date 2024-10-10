import unittest
from services.AI_applications import AIApplications
from services.OpenAI_Application.OpenAIClient import OpenAIClient
from core import config
from unittest.mock import MagicMock, patch


class TestAIApplications(unittest.TestCase):
    impl = None
    AI_application_list = None
    AI_applications = None
    conf = None

    @classmethod
    def setUpClass(cls):
        with patch("services.OpenAI_Application.OpenAIClient.get_openai_llm_client") as mock_openai_llm_client:
            mock_openai_llm_client.return_value = MagicMock()
            cls.conf = config.load_config_file()
            cls.AI_applications = AIApplications(cls.conf)
            cls.impl = cls.AI_applications.impl_map
            cls.AI_application_list = []

    def test_get_AI_applications(self):
        TestAIApplications.AI_application_list = TestAIApplications.AI_applications.get_AI_applications()
        self.assertIsNotNone(TestAIApplications.AI_application_list)
        self.assertIsInstance(TestAIApplications.AI_application_list, list)
        self.assertTrue(len(TestAIApplications.AI_application_list) > 0)
        
    def test_impl_map(self):
        self.assertIsNotNone(TestAIApplications.impl)
        self.assertIsInstance(TestAIApplications.impl, dict)
        self.assertTrue(len(TestAIApplications.impl) > 0)

    def test_get_service(self):
        for AI_application in TestAIApplications.AI_application_list:
            service = TestAIApplications.AI_applications.get_service(AI_application.get('name'))
            service_class = getattr(service, '__class__')
            self.assertIsNotNone(service)
            self.assertNotIsInstance(service_class, OpenAIClient)


if __name__ == '__main__':
    unittest.main()
