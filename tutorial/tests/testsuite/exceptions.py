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


class ShadowedBuiltinError(Exception):
    """Custom exception raised when a cell fails because a built-in type was overwritten"""

    def __init__(self, names: list[str], original: BaseException) -> None:
        quoted = ", ".join(f"`{name}`" for name in names)
        first = names[0]
        what = "built-in" if len(names) == 1 else "built-ins"
        variable = "variable" if len(names) == 1 else "variables"
        super().__init__(
            f"You have overwritten the {what} {quoted} with your own {variable} "
            f"(e.g. `{first} = ...`), so type hints like `{first}[int]` no longer work.\n"
            f"Run `del {', '.join(names)}` in a new cell, or restart the kernel, "
            f"and use a different variable name (e.g. `my_{first}`).\n\n"
            f"Original error: {type(original).__name__}: {original}"
        )


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
