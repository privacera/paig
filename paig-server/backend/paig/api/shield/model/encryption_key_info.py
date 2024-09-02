class EncryptionKeyInfo:
    """
    A class to represent encryption key information.
    """
    def __init__(self, response_dict):
        """
        Initializes an instance of EncryptionKeyInfo.

        Args:
            response_dict (dict): The response dictionary containing key information.
        """
        self.response_dict = response_dict

        self.id = -1
        self.publicKeyValue = None
        self.privateKeyValue = None
        self.keyStatus = None
        self.keyType = None
        self.tenantId = None

        if "id" in response_dict:
            self.id = response_dict["id"]

        if "publicKeyValue" in response_dict:
            self.publicKeyValue = response_dict["publicKeyValue"]

        if "privateKeyValue" in response_dict:
            self.privateKeyValue = response_dict["privateKeyValue"]

        if "keyStatus" in response_dict:
            self.keyStatus = response_dict["keyStatus"]

        if "keyType" in response_dict:
            self.keyType = response_dict["keyType"]

        if "tenantId" in response_dict:
            self.tenantId = response_dict["tenantId"]

    def to_dict(self):
        """
        Serializes the object to a dictionary.

        Returns:
            dict: The original response dictionary.
        """
        # Serialize the object to a JSON-formatted string
        return self.response_dict
