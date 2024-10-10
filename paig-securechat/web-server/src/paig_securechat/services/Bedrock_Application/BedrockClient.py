import logging
import sys

import boto3
from langchain_community.llms import Bedrock
from services.langchain_service_intf import LangChainServiceIntf

logger = logging.getLogger(__name__)


class BedrockClient(LangChainServiceIntf):
    def __init__(self, ai_app_name):
        super().__init__(ai_app_name)
        logger.info("Initializing Bedrock model")
        if "bedrock" not in self.config:
            logger.error("Bedrock configuration not found in configuration file")
            sys.exit("Bedrock configuration not found in configuration file. You have to provide bedrock "
                     "configuration in configuration file.")
        bedrock_config = self.config.get("bedrock")

        if "ask_prompt_suffix" in bedrock_config:
            self.ask_prompt_suffix = bedrock_config.get("ask_prompt_suffix")
        if "client_error_msg" in bedrock_config:
            self.client_error_msg = bedrock_config.get("client_error_msg")
        self.temperature = bedrock_config.get("temperature", 0)
        model_name = bedrock_config.get("model")
        region = bedrock_config.get("region")

        logger.info(f"Temperature: {self.temperature}")
        logger.info(f"Ask Prompt Suffix: {self.ask_prompt_suffix}")
        logger.info(f"Conversation History K: {self.conversation_history_k}")
        logger.info(f"Bedrock Model: {model_name}")
        logger.info(f"Disable Conversation Chain: {self.disable_conversation_chain}")

        self.bedrock_client = boto3.client("bedrock-runtime", region_name=region)
        self.langchain_llm = Bedrock(model_id=model_name, client=self.bedrock_client,
                                     model_kwargs={'temperature': self.temperature})


