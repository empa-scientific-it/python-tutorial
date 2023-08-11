import pytest


def reference_magic_example(num: int, power: int) -> int:
    """Compute num ^ power"""
    return num**power


input_args = [1, 2, 3, 4, 32]


@pytest.mark.parametrize("input_arg", input_args)
def test_power2(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_magic_example(input_arg, 2)


@pytest.mark.parametrize("input_arg", input_args)
def test_power3(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_magic_example(input_arg, 3)


@pytest.mark.parametrize("input_arg", input_args)
def test_power4(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_magic_example(input_arg, 4)
