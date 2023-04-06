import pytest

@pytest.mark.parametrize("set1, set2",
    [
        (1, 1)
    ],
)
def test_sets_equal(set1, set2, function_to_test):
    """The test case(s)"""
    assert (set1 == set2) == function_to_test(set1, set2)
    