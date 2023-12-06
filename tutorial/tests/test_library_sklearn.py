import pytest


def reference_equal_to_one(a):
    return 1 == a


@pytest.mark.parametrize("a", [1, 2, 3, 4])
def test_equal_to_one(a, function_to_test):
    assert reference_equal_to_one(a) == function_to_test(a)
