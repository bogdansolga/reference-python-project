

class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details or []
        super().__init__(self.message)
