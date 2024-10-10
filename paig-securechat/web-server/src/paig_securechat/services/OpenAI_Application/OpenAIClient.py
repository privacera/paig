import logging
import os
import sys
from langchain_openai import OpenAI, ChatOpenAI
from services.langchain_service_intf import LangChainServiceIntf
import openai

logger = logging.getLogger(__name__)


def initialize_openai_llm_client(openai_params):
    model = openai_params.get("model")
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    models_list = client.models.list()
    models = {model.id for model in models_list.data}

    if model not in models:
        logger.error(f"Model: {model} is not in OpenAI supported model list")
        sys.exit(f"Model: {model} is not in OpenAI supported model list, use a supported model name")

    try:
        client.chat.completions.create(
            model=model,
            messages=[
                {"role": "assistant", "content": "Knock knock."},
            ],
            temperature=0.1,
        )
        return ChatOpenAI(**openai_params)
    except Exception as e1:
        try:
            client.completions.create(
                model=model,
                prompt="Knock knock.",
                temperature=0.1,
            )
            return OpenAI(**openai_params)
        except Exception as e2:
            logger.error(f"Failed to initialize ChatOpenAI with error: {e1} and OpenAI with error {e2}")
            sys.exit(f"Failed to initialize ChatOpenAI/OpenAI llm client for model: {model}, "
                     f"use ChatOpenAI/OpenAI supported model name from gpt-3 and gtp-4 models list")


def get_openai_llm_client(openai_params):
    model = openai_params.get("model", None)
    if model in {None, ""}:
        return ChatOpenAI(**openai_params)
    else:
        return initialize_openai_llm_client(openai_params)


class OpenAIClient(LangChainServiceIntf):
    def __init__(self, ai_app_name):
        super().__init__(ai_app_name)
        logger.info("Initializing OPENAI model")
        openai_config = self.config["openai"]
        self.max_input_size = openai_config.get("max_input_size", 4096)
        self.num_outputs = openai_config.get("num_outputs", 512)
        self.temperature = openai_config.get("temperature", 0.1)
        self.openai_model = openai_config.get("model", None)
        if "ask_prompt_suffix" in openai_config:
            self.ask_prompt_suffix = openai_config.get("ask_prompt_suffix")
        if "client_error_msg" in openai_config:
            self.client_error_msg = openai_config.get("client_error_msg")
        logger.info(f"Max Input Size: {self.max_input_size}")
        logger.info(f"Number of Outputs: {self.num_outputs}")
        logger.info(f"Temperature: {self.temperature}")
        logger.info(f"Ask Prompt Suffix: {self.ask_prompt_suffix}")
        logger.info(f"Conversation History K: {self.conversation_history_k}")
        logger.info(f"Open AI Model: {self.openai_model}")
        logger.info(f"Disable Conversation Chain: {self.disable_conversation_chain}")
        openai_params = {"temperature": self.temperature}
        if self.openai_model is not None and self.openai_model != "":
            openai_params["model"] = self.openai_model
        self.langchain_llm = get_openai_llm_client(openai_params)
