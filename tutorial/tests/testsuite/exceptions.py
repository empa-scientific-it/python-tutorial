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


class PytestInternalError(Exception):
    """Custom exception raised when the test module cannot be found"""

    def __init__(self) -> None:
        super().__init__("Pytest internal error")


class OpenAIWrapperError(Exception):
    """Base exception for OpenAI validation errors"""


class InvalidAPIKeyError(OpenAIWrapperError):
    """Invalid API key"""


class APIConnectionError(OpenAIWrapperError):
    """Connection error"""


class UnexpectedAPIError(OpenAIWrapperError):
    """Unexpected API error"""


class InvalidModelError(OpenAIWrapperError):
    """Invalid model selection"""


@dataclass
class ValidationResult:
    """Result of OpenAI wrapper validation"""

    is_valid: bool
    error: OpenAIWrapperError | None = None
    message: str = ""

    @property
    def user_message(self) -> str:
        """Get a user-friendly message"""
        if self.error is not None:
            return f"🚫 <strong style='color: red;'>{self.message}</strong><br>{str(self.error)}"
        return "✅ <strong>OpenAI client configured successfully.</strong>"
