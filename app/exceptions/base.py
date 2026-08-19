class AppException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int,
        details=None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details

        super().__init__(message)
