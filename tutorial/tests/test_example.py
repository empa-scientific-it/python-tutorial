import pytest


@pytest.fixture
def function_to_test():
    """Function to test, always overriden by the cell magic"""


class TestClass:
    """A class collecting tests"""

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
    def test_function(self, input_arg, expected_output, function_to_test):
        """The test case(s)"""
        assert function_to_test(input_arg) == expected_output
