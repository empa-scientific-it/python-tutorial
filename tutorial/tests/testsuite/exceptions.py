from dataclasses import dataclass


class FunctionNotFoundError(Exception):
    """Custom exception raised when the solution code cannot be parsed"""

    def __init__(self) -> None:
        super().__init__("No functions to test defined in the cell")


class InstanceNotFoundError(Exception):
    """Custom exception raised when an instance cannot be found"""

    def __init__(self, name: str) -> None:
        super().__init__(f"Could not get {name} instance")


class TestModuleNotFoundError(Exception):
    """Custom exception raised when the test module cannot be found"""

    def __init__(self) -> None:
        super().__init__("Test module is not defined")


class PytestInteralError(Exception):
    """Custom exception raised when the test module cannot be found"""

    def __init__(self) -> None:
        super().__init__("Pytest internal error")


class OpenAIValidationError(Exception):
    """Base exception for OpenAI validation errors"""


class InvalidAPIKeyError(OpenAIValidationError):
    """Invalid API key"""


class APIConnectionError(OpenAIValidationError):
    """Connection error"""


class UnexpectedAPIError(OpenAIValidationError):
    """Unexpected API error"""


@dataclass
class APIValidationResult:
    """Result of API key validation"""

    is_valid: bool
    error: OpenAIValidationError | None = None

    @property
    def user_message(self) -> str:
        """Get a user-friendly message"""
        match self.error:
            case InvalidAPIKeyError():
                return (
                    "🚫 <strong style='color: red;'>Invalid OpenAI API key.</strong><br>"
                    "Please check that your API key is correct and has not expired."
                )
            case ConnectionError():
                return (
                    "🚫 <strong style='color: red;'>Could not connect to OpenAI.</strong><br>"
                    "Please check your internet connection and try again."
                )
            case UnexpectedAPIError():
                return (
                    "🚫 <strong style='color: red;'>Unexpected error with OpenAI API.</strong><br>"
                    f"Error details: {str(self.error)}"
                )
            case _:
                return "✅ <strong>OpenAI client configured successfully.</strong>"
