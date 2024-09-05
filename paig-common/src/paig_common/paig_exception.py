class PAIGException(Exception):
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)


class AuditEventQueueFullException(PAIGException):
    def __init__(self, message: str = None):
        super().__init__(message)


class DiskFullException(PAIGException):
    def __init__(self, message: str = None):
        super().__init__(message)
