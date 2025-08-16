class PermissionException(BaseException):
    """
    Exception raised for custom error scenarios.

    Attributes:
        message -- explanation of the error
        value -- optional value associated with the error
    """
    def __init__(self, message, value=None):
        self.message = message
        self.value = value
        super().__init__(self.message)