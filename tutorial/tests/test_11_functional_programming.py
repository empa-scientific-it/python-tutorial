import ast
import functools
import inspect
import itertools
import random
from typing import Any, Callable, List, Tuple

import numpy as np
import pytest
import requests
from numpy.typing import NDArray

#
# Example: Pure Function
#


def reference_pure_function(array, new_element):
    return array + [new_element]


@pytest.mark.parametrize(
    "array, new_element",
    [
        ([1, 2, 3], 4),
        (["cat", "dog"], "bird"),
    ],
)
def test_pure_function(array, new_element, function_to_test):
    output_array = function_to_test(array, new_element)
    assert id(output_array) != id(array), "The arrays must be different objects."
    assert output_array == reference_pure_function(array, new_element)


#
# Example: Composition
#


def reference_composition(x, y):
    def square(x: int) -> int:
        return x * x

    def add(x: int, y: int) -> int:
        return x + y

    def eq(x: int, y: int) -> int:
        return add(square(x), square(y))

    return eq(x, y)


@pytest.mark.parametrize(
    "x, y",
    [
        (2, 4),
        (5, 10),
    ],
)
def test_composition(x, y, function_to_test):
    assert function_to_test(x, y) == reference_composition(x, y)


#
# Example: Filter Even Numbers
#


def check_for_loop_in_body(fun: Callable) -> bool:
    """Checks if the body of a function contains a for loop"""
    tree = ast.parse(inspect.getsource(fun))
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            return True
    return False


def reference_filter_even(my_list: List[int]) -> List[int]:
    return list(filter(lambda x: x % 2 == 0, my_list))


@pytest.mark.parametrize(
    "my_list",
    [
        ([1, 2, 3, 4]),
        (list(range(100, 2))),
        ([random.randint(0, 10) for i in range(100)]),
    ],
)
def test_filter_even(function_to_test: Callable, my_list: List[int]):
    res = function_to_test(my_list)
    assert isinstance(res, list), "The function you wrote does not return a list"
    assert not check_for_loop_in_body(function_to_test), (
        "You are not allowed to use a for loop in this exercise"
    )
    assert res == reference_filter_even(my_list), (
        "The list you return is not equal to the expected solution"
    )


#
# Example: Add 1 to Each Element
#


def reference_add_one(my_list: List[int]) -> List[int]:
    return list(map(lambda x: x + 1, my_list))  # noqa: C417


@pytest.mark.parametrize(
    "my_list",
    [
        ([1, 2, 3, 4]),
        (list(range(100, 2))),
        ([random.randint(0, 10) for i in range(100)]),
    ],
)
def test_add_one(function_to_test: Callable, my_list: List[int]):
    assert function_to_test(my_list) == reference_add_one(my_list), (
        "The list you return is not equal to the expected solution"
    )
    assert not check_for_loop_in_body(function_to_test), (
        "You are not allowed to use a for loop in this exercise"
    )


#
# Example: Keeping only multiples of n
#


def reference_multiples_of_n(my_list: List[int], k: int) -> List[int]:
    return [i for i in my_list if i % k == 0]


@pytest.mark.parametrize(
    "my_list, k",
    [
        ([1, 2, 3, 4], 1),
        (list(range(100)), 5),
    ],
)
def test_multiples_of_n(
    function_to_test: Callable[[List[int]], int],
    my_list: List[int],
    k: int,
):
    assert function_to_test(my_list, k) == reference_multiples_of_n(my_list, k)


#
# Exercise 1: Transposing a Matrix
#


def reference_exercise1(matrix: List[List[int]]) -> List[List[int]]:
    return [list(i) for i in zip(*matrix)]


@pytest.mark.parametrize(
    "my_input",
    [(np.eye(3)), (np.random.randint(0, 100, size=(4, 4)))],
)
def test_exercise1(
    function_to_test: Callable[[List[List[int]]], List[List[int]]], my_input: NDArray
):
    res = function_to_test(my_input.tolist())
    assert (
        res == reference_exercise1(my_input.tolist())
        and res == my_input.transpose().tolist()
    )


#
# Exercise 2: Flattening list of lists
#


def reference_exercise2(my_list: List[List[Any]]) -> List[Any]:
    return functools.reduce(lambda x, y: x + y, my_list)


@pytest.mark.parametrize(
    "my_input",
    [
        [[1, 2, 3, 4], [4, 5, 5], [4, 5, 6]],
        [["a", "b", "c"], ["d", "f", "e"], ["another"]],
    ],
)
def test_exercise2(
    function_to_test: Callable[[List[List[Any]]], List[Any]],
    my_input: List[List[Any]],
):
    assert function_to_test(my_input) == reference_exercise2(my_input)


#
# Exercise 3: Counting initials
#


@functools.lru_cache
def get_data_exercise3() -> List[str]:
    words = requests.get("https://www.mit.edu/~ecprice/wordlist.10000").text
    return words.splitlines()


def reference_exercise3(words: List[str]) -> List[Tuple[str, int]]:
    return [
        (k, len(list(v)))
        for k, v in itertools.groupby(
            sorted(words, key=lambda x: x[0]), key=lambda x: x[0]
        )
    ]


def test_exercise3(function_to_test: Callable[[List[str]], List[Tuple[str, int]]]):
    data = get_data_exercise3()
    assert function_to_test(data) == reference_exercise3(data)


#
# Exercise 4: Counting initials frequency
#


def reference_exercise4(my_list: List[Tuple[str, int]]) -> List[Tuple[str, float]]:
    total = sum(map(lambda x: x[1], my_list))  # noqa: C417
    return [(letter, freq / total) for letter, freq in my_list]


def test_exercise4(
    function_to_test: Callable[[List[Tuple[str, int]]], List[Tuple[str, float]]],
):
    input_data = reference_exercise3(get_data_exercise3())
    assert function_to_test(input_data) == reference_exercise4(input_data)


#
# Exercise 5: Finding palindromes
#


def reference_exercise5(words: List[str]) -> List[str]:
    return list(filter(lambda x: x == x[::-1] and len(x) > 1, words))


def test_exercise5(function_to_test: Callable[[List[str]], List[str]]):
    data = get_data_exercise3()
    assert function_to_test(data) == reference_exercise5(data)
