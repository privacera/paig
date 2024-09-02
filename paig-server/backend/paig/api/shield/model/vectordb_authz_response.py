from typing import Dict


class AuthorizeVectorDBResponse:
    """
    A class representing a response to an authorization request for a vector database.
    """

    def __init__(self, res_data: Dict):
        """
        Initializes an instance of AuthorizeVectorDBResponse.

        Args:
            res_data (Dict): The response data containing vector database authorization information.
        """
        self.vectorDBPolicyInfo = res_data.get("vectorDBPolicyInfo", [])
        self.vectorDBId = res_data.get("vectorDBId", -1)
        self.vectorDBName = res_data.get("vectorDBName", '')
        self.vectorDBType = res_data.get("vectorDBType", '')
        self.userEnforcement = res_data.get("userEnforcement", -1)
        self.groupEnforcement = res_data.get("groupEnforcement", -1)
        self.filterExpression = res_data.get("filterExpression", '')
