import pytest
import math


@pytest.mark.parametrize("a, b, c",
                         [
    (1, 2, 3),
    (4, 5, 9),
    (10, 11, 21),
    (-5, 1, 2),
    (23.1, 1.8, 14.2),
    (-10.5, 7.4, 84),
    (1e-5, 3.5e-5, 2.5),
    ]
    )
def test_addition_multiplication(a, b, c, function_to_test):
    assert math.isclose(function_to_test(a, b, c), (a + b) * c)

@pytest.mark.parametrize("r",
                            [
    1,
    2,
    3.5,
    4.5,
    124.5,
    0.5,
    0.0001,
    ]
    )
def test_circle_area(r, function_to_test):
    assert math.isclose(function_to_test(r), math.pi * r ** 2, rel_tol=1e-4)



@pytest.mark.parametrize("a, b, c",                      [
    (1, 3, 2),
    (2, 10, 9),
    (10, 22, -21),
    (-5, 3, 2),
    (3.8, 23.1, 2.2),
    (-10.5, 14.4, 4),
    (1e-3, 1, 1.5),
    ])
def test_quadratic_equation(a, b, c, function_to_test):
    d = b ** 2 - 4 * a * c
    solution1 = (-b + math.sqrt(d)) / (2 * a)
    solution2 = (-b - math.sqrt(d)) / (2 * a)
    provided_solution1, provided_solution2 = function_to_test(a, b, c)

    assert (math.isclose(provided_solution1, solution1) and math.isclose(provided_solution2, solution2)) or (math.isclose(provided_solution1, solution2) and math.isclose(provided_solution2, solution1))

SET1_2 = [
    (set(), set()),
    ({1, 2, 3}, {1, 2, 3}),
    ({1, 2, 3}, {3, 2, 1}),
    ({1, 2, 3}, {1, 2, 3, 4}),
    ({1, 2, 3}, {1, 2}),
    ({1, 2, 3}, {4, 5, 6}),
    (set(), {1, 2, 3}),
    ({1, 2, 3}, set()),
]

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_union(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.union(set2)

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_intersection(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.intersection(set2)

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_difference(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.difference(set2)

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_symmetric_difference(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.symmetric_difference(set2)

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_subset(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.issubset(set2)

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_superset(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.issuperset(set2)

@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_disjoint(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.isdisjoint(set2)

