import pytest


@pytest.fixture
def func_to_test():
    """Function to test, overriden by the cell magic"""
    pass


@pytest.mark.parametrize(
    "input_arg, expected_output",
    [
        (2, 4),
        (3, 9),
        (4, 16),
        (32, 1024),
    ],
)
def test_function(input_arg, expected_output, func_to_test):
    """The test case(s)"""
    assert func_to_test(input_arg) == expected_output
