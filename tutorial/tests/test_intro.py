import pytest


def reference_sum_two_numbers(a: int, b: int) -> int:
    return a + b


@pytest.mark.parametrize("a, b", [(1, 3), (2, 10), (10, 22), (-5, 3)])
def test_sum_two_numbers(a, b, function_to_test):
    assert reference_sum_two_numbers(a, b) == function_to_test(a, b)
