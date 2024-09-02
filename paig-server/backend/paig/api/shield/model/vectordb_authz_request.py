from typing import Dict

from api.shield.utils.custom_exceptions import BadRequestException


class AuthorizeVectorDBRequest:
    """
     A class representing a request to authorize access to a vector database.
    """

    def __init__(self, req_data: Dict, user_role: str):
        """
           Initializes an instance of AuthorizeVectorDBRequest.

           Args:
               req_data (Dict): The request data.
               user_role (str): The role of the user.
           """
        # Mandatory fields

        self.userId = str(self.extract_data(req_data, "userId")).lower()
        self.applicationKey = self.extract_data(req_data, "applicationKey")
        self.user_role = user_role

    @staticmethod
    def extract_data(req_data, key):
        """
              Extract data from the request dictionary.

              Args:
                  req_data (dict): The request data.
                  key (str): The key to extract.

              Returns:
                  The value associated with the key.
        """
        data = req_data.get(key)
        if not data:
            raise BadRequestException(f"Missing {key} in request")
        return data

    def to_payload_dict(self):
        """
        Serialize the AuthorizeVectorDBRequest instance to a dictionary.

        Returns:
            dict: The serialized instance.
        """
        return {
            "userId": self.userId,
            "applicationKey": self.applicationKey
        }
