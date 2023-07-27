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


def reference_exercise2(my_list: List[int], k: int):
    return [i for i in my_list if i % k == 0]


def check_for_loop_in_body(fun: Callable) -> bool:
    """Checks if the body of a function contains a for loop"""
    tree = ast.parse(inspect.getsource(fun))
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            return True
    return False


def reference_filter_even(my_list: "list[int]") -> "list[int]":
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
    assert type(res) == list, "The function you wrote does not return a list"
    assert res == reference_filter_even(
        my_list
    ), "The list you return is not equal to the expected solution"
    assert not check_for_loop_in_body(
        function_to_test
    ), "You are not allowed to use a for loop in this exercise"


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
    assert function_to_test(my_list) == reference_add_one(
        my_list
    ), "The list you return is not equal to the expected solution"
    assert not check_for_loop_in_body(
        function_to_test
    ), "You are not allowed to use a for loop in this exercise"


@pytest.mark.parametrize(
    "my_list, k",
    [
        ([1, 2, 3, 4], 1),
        (list(range(100)), 5),
    ],
)
def test_exercise2(
    function_to_test: Callable[[int, int], int],
    my_list: List[int],
    k: int,
):
    assert function_to_test(my_list, k) == reference_exercise2(my_list, k)


def reference_exercise3(x: List[List[int]]) -> List[List[int]]:
    return [list(i) for i in zip(*x)]


@pytest.mark.parametrize(
    "my_input",
    [(np.eye(3)), (np.random.randint(0, 100, size=(4, 4)))],
)
def test_exercise3(
    function_to_test: Callable[[List[List[int]]], List[List[int]]], my_input: NDArray
):
    res = function_to_test(my_input.tolist())
    assert (
        res == reference_exercise3(my_input.tolist())
        and res == my_input.transpose().tolist()
    )


def reference_exercise4(my_list: List[List[Any]]) -> List[Any]:
    return functools.reduce(lambda x, y: x + y, my_list)


@pytest.mark.parametrize(
    "my_input, reference_func",
    [
        ([[1, 2, 3, 4], [4, 5, 5], [4, 5, 6]], reference_exercise4),
        ([["a", "b", "c"], ["d", "f", "e"], ["another"]], reference_exercise4),
    ],
)
def test_exercise4(
    function_to_test: Callable[[List[List[any]]], List[Any]],
    my_input: List[List[Any]],
    reference_func: Callable,
):
    assert function_to_test(my_input) == reference_func(my_input)


@functools.lru_cache
def get_data_exercise5() -> List[str]:
    words = requests.get("https://www.mit.edu/~ecprice/wordlist.10000").text
    return words.splitlines()


def reference_exercise5(w: List[str]) -> List[Tuple[str, int]]:
    return [
        (k, len(list(v)))
        for k, v in itertools.groupby(sorted(w, key=lambda x: x[0]), key=lambda x: x[0])
    ]


def test_exercise5(function_to_test: Callable[[List[str]], List[Tuple[str, int]]]):
    data = get_data_exercise5()
    assert function_to_test(data) == reference_exercise5(data)


def reference_exercise6(
    my_list: List[Tuple[str, int]]
) -> List[Tuple[str, float]]:
    total = sum(map(lambda x: x[1], my_list))  # noqa: C417
    return [(letter, freq / total) for letter, freq in my_list]


def test_exercise6(
    function_to_test: Callable[[List[Tuple[str, int]]], List[Tuple[str, float]]]
):
    input_data = reference_exercise5(get_data_exercise5())
    assert function_to_test(input_data) == reference_exercise6(input_data)


def reference_function_exercise7(my_list: List[str]) -> List[str]:
    return list(filter(lambda x: x == x[::-1] and len(x) > 1, my_list))


def test_exercise7(function_to_test: Callable[[List[str]], List[str]]):
    data = get_data_exercise5()
    assert function_to_test(data) == reference_function_exercise7(data)
