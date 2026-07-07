class ValidationException(Exception):
    def __init__(self, status_code : int ,error_messages : str | list ):
        super().__init__(str(error_messages))
        self.status_code = status_code
        self.error_messages = error_messages
        