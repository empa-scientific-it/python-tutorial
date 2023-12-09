import numpy as np
import pytest


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


some_2d_arrays = [
    np.array([[1, 2], [3, 4]]),
    np.array([[1]]),
    np.array(
        [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
            [11, 12, 13, 14, 15],
        ]
    ),
    np.array([[1, 2], [3, 5]]),
    np.ones((10, 10)),
    np.full((10, 10), 5),
    np.zeros((10, 10)),
]

some_indexes = [0, 0, 2, 1, 5, 3, 9]


def reference_sum_of_a_row(array, row):
    return np.sum(array[row])


@pytest.mark.parametrize("array, row", list(zip(some_2d_arrays, some_indexes)))
def test_sum_of_a_row(array, row, function_to_test):
    assert reference_sum_of_a_row(array, row) == function_to_test(array, row)


def reference_sum_of_a_column(array, column):
    return np.sum(array[:, column])


@pytest.mark.parametrize("array, column", list(zip(some_2d_arrays, some_indexes)))
def test_sum_of_a_column(array, column, function_to_test):
    assert reference_sum_of_a_column(array, column) == function_to_test(array, column)


def reference_sub_matrix(array, row, column):
    return array[:row, :column]


row_column_indexes = [(2, 3), (1, 1), (1, 5), (2, 1), (9, 9), (10, 10), (3, 10)]


@pytest.mark.parametrize(
    "array, row_column", list(zip(some_2d_arrays, row_column_indexes))
)
def test_sub_matrix(array, row_column, function_to_test):
    row, column = row_column
    assert np.all(
        reference_sub_matrix(array, row, column) == function_to_test(array, row, column)
    )


def reference_multiply_each_row_by_its_sum(array):
    for row in array:
        row *= sum(row)
    return array


@pytest.mark.parametrize("array", some_2d_arrays)
def test_multiply_each_row_by_its_sum(array, function_to_test):
    assert np.all(
        reference_multiply_each_row_by_its_sum(array) == function_to_test(array)
    )
