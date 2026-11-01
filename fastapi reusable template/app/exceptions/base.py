class AppException(Exception):
    status_code = 400
    message = "Application error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)
