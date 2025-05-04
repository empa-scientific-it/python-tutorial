import copy
import math
from typing import Any, Callable, Hashable, Iterable

import pytest


def reference_addition_multiplication(a: float, b: float, c: float) -> float:
    return (a + b) * c


@pytest.mark.parametrize(
    "a, b, c",
    [
        (1, 2, 3),
        (4, 5, 9),
        (10, 11, 21),
        (-5, 1, 2),
        (23.1, 1.8, 14.2),
        (-10.5, 7.4, 84),
        (1e-5, 3.5e-5, 2.5),
    ],
)
def test_addition_multiplication(
    a: float,
    b: float,
    c: float,
    function_to_test: Callable[[float, float, float], float],
):
    assert math.isclose(
        function_to_test(a, b, c), reference_addition_multiplication(a, b, c)
    )


def reference_circle_area(r: float) -> float:
    return math.pi * r**2


@pytest.mark.parametrize(
    "r",
    [
        1,
        2,
        3.5,
        4.5,
        124.5,
        0.5,
        0.0001,
    ],
)
def test_circle_area(r: float, function_to_test: Callable[[float], float]):
    assert math.isclose(function_to_test(r), reference_circle_area(r), rel_tol=1e-4)


def reference_quadratic_equation(a: float, b: float, c: float) -> tuple[float, float]:
    d = b**2 - 4 * a * c
    solution1 = (-b + math.sqrt(d)) / (2 * a)
    solution2 = (-b - math.sqrt(d)) / (2 * a)
    return solution1, solution2


@pytest.mark.parametrize(
    "a, b, c",
    [
        (1, 3, 2),
        (2, 10, 9),
        (10, 22, -21),
        (-5, 3, 2),
        (3.8, 23.1, 2.2),
        (-10.5, 14.4, 4),
        (1e-3, 1, 1.5),
    ],
)
def test_quadratic_equation(
    a: float,
    b: float,
    c: float,
    function_to_test: Callable[[float, float, float], tuple[float, float]],
):
    solution1, solution2 = reference_quadratic_equation(a, b, c)
    provided_solution1, provided_solution2 = function_to_test(a, b, c)

    assert (
        math.isclose(provided_solution1, solution1)
        and math.isclose(provided_solution2, solution2)
    ) or (
        math.isclose(provided_solution1, solution2)
        and math.isclose(provided_solution2, solution1)
    )


def reference_a_plus_b_equals_c(a: float, b: float, c: float) -> bool:
    return math.isclose(a + b, c)


@pytest.mark.parametrize(
    "a, b, c",
    [
        (1, 2, 3),
        (4, 5, 9),
        (10, 11, 21),
        (-5, 1, 2),
        (23.1, 1.8, 14.2),
        (-10.5, 7.4, 84),
        (1e-5, 3.5e-5, 2.5),
        (0.1, 0.2, 0.3),
    ],
)
def test_a_plus_b_equals_c(
    a: float,
    b: float,
    c: float,
    function_to_test: Callable[[float, float, float], bool],
) -> None:
    assert function_to_test(a, b, c) == reference_a_plus_b_equals_c(a, b, c)


def reference_number_is_even(number: int) -> bool:
    return number % 2 == 0


@pytest.mark.parametrize("number", [1, 2, 3, 4])
def test_number_is_even(number: int, function_to_test: Callable[[int], bool]) -> None:
    assert function_to_test(number) == reference_number_is_even(number)


def reference_number_is_greater_than_zero(number: float) -> bool:
    return number > 0


@pytest.mark.parametrize("number", [1, 2, 3, 4])
def test_number_is_greater_than_zero(
    number: int, function_to_test: Callable[[int], bool]
):
    assert function_to_test(number) == reference_number_is_greater_than_zero(number)


def reference_number_is_positive_and_even(number: int) -> bool:
    return number % 2 == 0 and number > 0


@pytest.mark.parametrize("number", [1, 2, 3, 4, -1, -2, -3, -4])
def test_number_is_positive_and_even(
    number: int, function_to_test: Callable[[int], bool]
):
    assert function_to_test(number) == reference_number_is_positive_and_even(number)


def reference_number_is_lower_than_0_or_greater_equal_to_100(number: int) -> bool:
    return number < 0 or number >= 100


@pytest.mark.parametrize("number", [1, 2, 3, 4, -1, -2, -3, -4, 0, 100, 101, 102, 103])
def test_number_is_lower_than_0_or_greater_equal_to_100(
    number: int, function_to_test: Callable[[int], bool]
):
    assert function_to_test(
        number
    ) == reference_number_is_lower_than_0_or_greater_equal_to_100(number)


LISTS = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 5, 6, 7, 8],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6],
    [1, 2, 3, 4, 5],
    [1, 2, 3, 4],
    [1, 2, 3],
    [1, 2],
    [1],
    ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    ["j", "i", "h", "g", "f", "e", "d", "c", "b", "a"],
    ["a", 1, "b", 2, "c", 3, "d", 4, "e", 5],
]

LIST1 = ["x", "y", "z"]


LIST1_2 = [
    ([], []),
    ([1, 2, 3], [1, 2, 3]),
    ([1, 2, 3], [3, 2, 1]),
    ([1, 2, 3], [1, 2, 3, 4]),
    ([1, 2, 3], [1, 2]),
    ([1, 2, 3], [4, 5, 6]),
    ([], [1, 2, 3]),
    ([1, 2, 3], []),
    (LIST1, LIST1),
    (LIST1, LIST1.copy()),
]


def reference_remove_every_second_element_from_list(my_list: list) -> list:
    return my_list[::2]


@pytest.mark.parametrize("my_list", LISTS)
def test_remove_every_second_element_from_list(my_list, function_to_test):
    assert function_to_test(my_list) == reference_remove_every_second_element_from_list(
        my_list
    )


def reference_return_first_and_last_element_from_list(my_list: list) -> tuple:
    return my_list[0], my_list[-1]


@pytest.mark.parametrize("my_list", LISTS)
def test_return_first_and_last_element_from_list(my_list, function_to_test):
    # If result is a tuple, transform to list
    result = function_to_test(my_list)
    if isinstance(result, list):
        result = tuple(result)
    assert result == reference_return_first_and_last_element_from_list(my_list)


def reference_first_and_last_element_are_equal(my_list: list) -> bool:
    return my_list[0] == my_list[-1]


@pytest.mark.parametrize("my_list", LISTS)
def test_first_and_last_element_are_equal(my_list, function_to_test):
    assert function_to_test(my_list) == reference_first_and_last_element_are_equal(
        my_list
    )


def reference_lists_are_equal(list1: list, list2: list) -> bool:
    return list1 == list2


@pytest.mark.parametrize("list1, list2", LIST1_2)
def test_lists_are_equal(list1, list2, function_to_test):
    assert function_to_test(list1, list2) == reference_lists_are_equal(list1, list2)


def reference_lists_are_not_same_but_equal(list1: list, list2: list) -> bool:
    return list1 == list2 and list1 is not list2


@pytest.mark.parametrize("list1, list2", LIST1_2)
def test_lists_are_not_same_but_equal(list1, list2, function_to_test):
    assert function_to_test(list1, list2) == reference_lists_are_not_same_but_equal(
        list1, list2
    )


def reference_greater_or_equal(list1: list, list2: list) -> bool:
    return list1 >= list2


@pytest.mark.parametrize("list1, list2", LIST1_2)
def test_greater_or_equal(list1, list2, function_to_test):
    assert function_to_test(list1, list2) == reference_greater_or_equal(list1, list2)


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


def reference_sets_union(set1: set, set2: set) -> set:
    return set1 | set2


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_union(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == reference_sets_union(set1, set2)


def reference_sets_intersection(set1: set, set2: set) -> set:
    return set1 & set2


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_intersection(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == reference_sets_intersection(set1, set2)


def reference_sets_difference(set1: set, set2: set) -> set:
    return set1 - set2


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_difference(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == reference_sets_difference(set1, set2)


def reference_sets_symmetric_difference(set1: set, set2: set) -> set:
    return set1 ^ set2


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_symmetric_difference(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == reference_sets_symmetric_difference(
        set1, set2
    )


def reference_sets_subset(set1: set, set2: set) -> bool:
    return set1 <= set2


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_subset(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == set1.issubset(set2)


def reference_sets_superset(set1: set, set2: set) -> bool:
    return set1 >= set2


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_superset(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == reference_sets_superset(set1, set2)


def reference_sets_disjoint(set1: set, set2: set) -> bool:
    return (set1 & set2) == set()


@pytest.mark.parametrize("set1, set2", SET1_2)
def test_sets_disjoint(set1, set2, function_to_test):
    """The test case(s)"""
    assert function_to_test(set1, set2) == reference_sets_disjoint(set1, set2)


DICTS1 = [
    {},
    {"a": 1},
    {"a": 1, "b": 2},
    {"a": 1, "b": 2, "c": 3},
    {"a": 1, "b": 2, "c": 3, "d": 4},
    {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
]

DICTS2 = [
    {"a": 10, "b": 20, "c": 30, "d": 40, "e": 50},
    {"a": 10, "b": 20, "c": 30, "d": 40},
    {"a": 10, "b": 20, "c": 30},
    {"a": 10, "b": 20},
    {"a": 10},
    {},
]


def reference_dict_return_value(my_dict: dict[Hashable, Any], key: Any) -> Any:
    return my_dict.get(key)


@pytest.mark.parametrize(
    "my_dict, key", list(zip(copy.deepcopy(DICTS1), ["b"] * len(DICTS1)))
)
def test_dict_return_value(my_dict, key, function_to_test):
    my_dict_to_try = my_dict.copy()
    assert function_to_test(my_dict_to_try, key) == reference_dict_return_value(
        my_dict, key
    )
    # Check that the original dict is not modified
    assert my_dict == my_dict_to_try


def reference_dict_return_delete_value(my_dict: dict[Hashable, Any], key: Any) -> Any:
    return my_dict.pop(key, None)


@pytest.mark.parametrize(
    "my_dict, key", list(zip(copy.deepcopy(DICTS1), ["b"] * len(DICTS1)))
)
def test_dict_return_delete_value(my_dict, key, function_to_test):
    my_dict_original1 = my_dict.copy()
    my_dict_original2 = my_dict.copy()
    assert function_to_test(
        my_dict_original1, key
    ) == reference_dict_return_delete_value(my_dict_original2, key)

    assert my_dict_original1 == my_dict_original2


def reference_update_one_dict_with_another(
    dict1: dict[Hashable, Any], dict2: dict[Hashable, Any]
) -> dict[Hashable, Any]:
    dict1.update(dict2)
    return dict1


@pytest.mark.parametrize(
    "my_dict1, my_dict2", list(zip(copy.deepcopy(DICTS1), copy.deepcopy(DICTS2)))
)
def test_update_one_dict_with_another(my_dict1, my_dict2, function_to_test):
    my_dict1_original1 = my_dict1.copy()
    my_dict1_original2 = my_dict1.copy()
    new_dict = function_to_test(my_dict1_original1, my_dict2)
    if new_dict is None:
        new_dict = my_dict1_original1
    ref_dict = reference_update_one_dict_with_another(my_dict1_original2, my_dict2)
    if ref_dict is None:
        ref_dict = my_dict1_original2

    assert new_dict == ref_dict


STRINGS = [
    "",
    "a",
    "ab",
    "abc",
    "abcd",
    "a b c d eOne two three four five six seven eight nine ten",
    "Hello world",
    "How are you?",
]


def reference_string_capitalize(my_string: str) -> str:
    return my_string.capitalize()


@pytest.mark.parametrize("my_string", STRINGS)
def test_string_capitalize(my_string, function_to_test):
    assert function_to_test(my_string) == reference_string_capitalize(my_string)


def reference_string_lower_case(my_string: str) -> str:
    return my_string.lower()


@pytest.mark.parametrize("my_string", STRINGS)
def test_string_lower_case(my_string, function_to_test):
    assert function_to_test(my_string) == reference_string_lower_case(my_string)


def reference_string_word_split(my_string: str) -> list[str]:
    return my_string.split()


@pytest.mark.parametrize("my_string", STRINGS)
def test_string_word_split(my_string, function_to_test):
    assert function_to_test(my_string) == reference_string_word_split(my_string)


def reference_string_join_commas(my_string: Iterable[str]) -> str:
    return ",".join(my_string)


@pytest.mark.parametrize("my_string", STRINGS)
def test_string_join_commas(my_string, function_to_test):
    my_string_splitted = my_string.split()
    assert function_to_test(my_string_splitted) == reference_string_join_commas(
        my_string_splitted
    )


def reference_string_split_lines(my_string: str) -> list[str]:
    return my_string.splitlines()


def test_string_split_lines(function_to_test):
    my_string = "\n".join(STRINGS)
    assert function_to_test(my_string) == reference_string_split_lines(my_string)


INT_SETS = [set(), {1, 2, 3}, {3, -1, 0, 4, 42, 1002}]


def reference_sets_of_even_and_odd(my_set: set[int]) -> tuple[set[int]]:
    even_set = my_set.copy()
    odd_set = my_set.copy()
    for n in my_set:
        if n % 2 == 0:
            odd_set.remove(n)
        else:
            even_set.remove(n)
    return even_set, odd_set


@pytest.mark.parametrize("my_set", INT_SETS)
def test_sets_of_even_and_odd(my_set, function_to_test):
    sol_set = my_set.copy()
    ref_set = my_set.copy()
    sol_even_set, sol_odd_set = function_to_test(sol_set)
    ref_even_set, ref_odd_set = reference_sets_of_even_and_odd(ref_set)

    assert sol_even_set == ref_even_set
    assert sol_odd_set == ref_odd_set


INT_TUPLES = [(), (1, 2, 3), (3, -1, 0, 4, 42, 1002)]


def reference_tuple_increased_by_one(my_tuple: tuple[int]) -> tuple[int]:
    increase = []
    for n in my_tuple:
        increase.append(n + 1)
    return tuple(increase)


@pytest.mark.parametrize("my_tuple", INT_TUPLES)
def test_tuple_increased_by_one(my_tuple, function_to_test):
    new_tuple = function_to_test(my_tuple)
    ref_tuple = reference_tuple_increased_by_one(my_tuple)

    assert new_tuple == ref_tuple
