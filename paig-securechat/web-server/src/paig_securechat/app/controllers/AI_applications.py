import logging
logger = logging.getLogger(__name__)


class AIApplicationController:
    def __init__(self, llm_AI_application_service):
        self.AI_application_service = llm_AI_application_service

    def get_all_AI_applications(self):
        try:
            return self.AI_application_service.get_AI_applications_for_ui()
        except Exception as err:
            logger.error(f"Error occurred while fetching models {err}")
            return None
