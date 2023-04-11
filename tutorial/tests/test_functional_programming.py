import pytest
from typing import Callable

def test_solution_exercise1(function_to_test: Callable):
    assert function_to_test([1,2,3], 1) == [1,2, 3]
