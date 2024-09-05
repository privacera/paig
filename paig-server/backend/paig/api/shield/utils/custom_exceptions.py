class BadRequestException(Exception):
    def __init__(self, message="Bad Request"):
        self.message = message
        super().__init__(self.message)


class ShieldException(Exception):
    def __init__(self, message: str = None):
        if message is None:
            message = "Privacera Shield Internal Error. Please contact Privacera Support."
        else:
            message = f"Privacera Shield Internal Error. Please contact Privacera Support. {message}"
        self.message = message
        super().__init__(self.message)


class UnsupportedFileTypeException(Exception):
    def __init__(self, message="Unsupported file type"):
        self.message = message + ". Please check and update with Supported file types."
        super().__init__(self.message)
