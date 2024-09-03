class ConversationType:
    PROMPT = "prompt"
    ENRICHED_PROMPT = "enriched_prompt"
    REPLY = "reply"
    RAG = "rag"


class ResponseMessage:
    def __init__(self, response_message):
        """
        Initialize a ResponseMessage instance.

        Args:
            response_message (dict): A dictionary containing response message data.
        """
        self.response_text = response_message

    def get_response_text(self):
        """
        Get the 'response_text' attribute value.

        Returns:
            str: The response text.
        """
        return self.response_text
