import numpy as np


def reference_ten_zeros():
    return np.zeros(10)


def test_ten_zeros(function_to_test):
    assert np.all(reference_ten_zeros() == function_to_test())


def reference_ones_size_two_by_three():
    return np.ones((2, 3))


def test_ones_size_two_by_three(function_to_test):
    assert np.all(reference_ones_size_two_by_three() == function_to_test())


def reference_fives_size_two_by_three_by_four():
    return np.full((2, 3, 4), 5)


def test_fives_size_two_by_three_by_four(function_to_test):
    assert np.all(reference_fives_size_two_by_three_by_four() == function_to_test())


def reference_array_of_true():
    return np.full(100, True, dtype=bool)


def test_array_of_true(function_to_test):
    assert np.all(reference_array_of_true() == function_to_test())
    assert function_to_test().dtype == np.dtype("bool")


def reference_empty_strings():
    return np.full(55, "", dtype=str)


def test_empty_strings(function_to_test):
    assert np.all(reference_empty_strings() == function_to_test())
    assert function_to_test().dtype == np.dtype("<U1")
