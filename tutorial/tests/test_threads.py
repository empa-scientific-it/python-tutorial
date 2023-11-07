from typing import Callable


def reference_exercise1() -> int:
    return 42


def test_exercise1(function_to_test: Callable):
    assert function_to_test("") == 42
