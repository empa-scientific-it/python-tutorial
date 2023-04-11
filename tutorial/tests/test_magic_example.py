import pytest

@pytest.mark.parametrize(
    "input_arg, expected_output",
    [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (32, 1024),
    ],
)
def test_power2(input_arg, expected_output, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == expected_output


@pytest.mark.parametrize(
    "input_arg, expected_output",
    [
        (1, 1),
        (2, 8),
        (3, 27),
        (4, 64),
        (32, 32768),
    ],
)
def test_power3(input_arg, expected_output, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == expected_output