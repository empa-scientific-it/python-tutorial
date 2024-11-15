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
