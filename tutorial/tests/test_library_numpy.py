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


def reference_function_values(x):
    return x**2 + 2 * x * np.exp(x) + 1.0


@pytest.mark.parametrize(
    "x",
    [
        np.array([1, 2, 3]),
        np.array([0, 1, 2]),
        np.array([0.1, 0.2, 0.3]),
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.array([-1, 0, 1]),
        np.random.random(100),
    ],
)
def test_function_values(x, function_to_test):
    assert np.all(reference_function_values(x) == function_to_test(x))


def reference_all_values_strictly_positive(array):
    # Your code starts here
    result = array > 0
    return result.all()
    # Your code ends here


@pytest.mark.parametrize(
    "array",
    [
        np.array([1, 2, 3]),
        np.array([0, 1, 2]),
        np.array([0.1, 0.2, 0.3]),
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.array([-1, 0, 1]),
        np.random.random((3, 4)) * 10 - 1,
        np.random.random((3, 4, 5)) * 20 - 1,
    ],
)
def test_all_values_strictly_positive(array, function_to_test):
    assert reference_all_values_strictly_positive(array) == function_to_test(array)


def reference_compute_integral(f, a, b):
    step = 0.001
    # Create a set of values for x between a and b with step size 0.001
    x = np.arange(a, b, step)
    # Compute the y values
    y = f(x)
    # Compute the integral
    integral = np.sum(y) * step
    return integral


@pytest.mark.parametrize(
    "f, a, b",
    [
        (lambda x: x, 0, 1),
        (lambda x: x**2, 0, 1),
        (lambda x: x**3 + 2 * x**2 + 3 * x + 4, 0, 3),
        (lambda x: np.sin(x), 0, np.pi),
    ],
)
def test_compute_integral(f, a, b, function_to_test):
    assert np.isclose(reference_compute_integral(f, a, b), function_to_test(f, a, b))


def reference_eigenvalue():
    # 1. TODO: define the matrix a_ref here:
    a_ref = np.array([[9, 3, 3], [3, 2, 2], [3, 4, 2]])

    eigenvalues, eigenvectors = np.linalg.eigh(a_ref)
    return eigenvalues, eigenvectors


def test_eigenvalue(function_to_test):
    eigval_ref, eigvec_ref = reference_eigenvalue()
    sol_test = function_to_test()
    assert np.all(np.isclose(eigval_ref, sol_test[0]))
    assert np.all(np.isclose(eigvec_ref, sol_test[1]))


def reference_sum_numbers_0_to_10000():
    # Your code starts here
    numbers = np.arange(0, 10000)
    divis = (numbers % 4 != 0) & (numbers % 7 != 0)
    return np.sum(numbers[divis])
    # Your code ends here


def test_sum_numbers_0_to_10000(function_to_test):
    assert reference_sum_numbers_0_to_10000() == function_to_test()


def reference_mean_and_std():
    # Your code starts here
    x = np.linspace(0, 10, 10000)
    y = np.exp(-x / 10) * np.sin(x)

    mask = (x >= 4) & (x <= 7)
    mean = y[mask].mean()
    std = y[mask].std()
    return mean, std


def test_mean_and_std(function_to_test):
    assert np.allclose(reference_mean_and_std(), function_to_test())


def reference_80_percentile():
    # Your code starts here
    x = np.linspace(0, 10, 10000)
    y = np.exp(-x / 10) * np.sin(x)

    mask = (x >= 4) & (x <= 7)
    percentile = np.percentile(y[mask], 80)
    return percentile
    # Your code ends here


def test_80_percentile(function_to_test):
    assert np.allclose(reference_80_percentile(), function_to_test())


def reference_compute_area():
    # Your code starts here
    theta = np.linspace(0, 2 * np.pi, 1000)
    r = 1 + 3 / 4 * np.sin(3 * theta)
    area = 1 / 2 * np.sum(r**2) * (theta[1] - theta[0])
    return area
    # Your code ends here


def test_compute_area(function_to_test):
    assert np.allclose(reference_compute_area(), function_to_test())


def reference_compute_arc_length():
    # Your code starts here
    theta = np.linspace(0, 2 * np.pi, 1000)
    r = 1 + 3 / 4 * np.sin(3 * theta)
    arc_length = np.sum(np.sqrt(r**2 + np.gradient(r, theta) ** 2)) * (
        theta[1] - theta[0]
    )
    return arc_length
    # Your code ends here


def test_compute_arc_length(function_to_test):
    assert np.allclose(reference_compute_arc_length(), function_to_test())
