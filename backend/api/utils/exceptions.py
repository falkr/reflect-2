class OpenAIRequestError(Exception):
    """Exception raised when an OpenAI API request fails."""

    def __init__(self, message: str):
        self.message = message


class DataProcessingError(Exception):
    """Exception raised for errors in processing the data."""

    def __init__(self, message: str):
        self.message = message
