import pytest
from typing import Callable, List, Any, Tuple
import numpy as np
from numpy.typing import ArrayLike, NDArray
import functools
import requests
import itertools


def reference_solution_exercise2(l: List[int], k: int):
    return [i for i in l if i % k == 0]


@pytest.mark.parametrize(
    "l, k",
    [
        ([1, 2, 3, 4], 1),
        (list(range(100)), 5),
    ],
)
def test_exercise2(
    function_to_test: Callable[[int, int], int],
    l: List[int],
    k: int,
):
    assert function_to_test(l, k) == reference_solution_exercise2(l, k)



def reference_solution_exercise3(x: List[List[int]]) -> List[List[int]]:
    return [list(i) for i in zip(*x)]

@pytest.mark.parametrize(
    "input",
    [(np.eye(3)), (np.random.randint(0, 100, size=(4, 4)))],
)
def test_exercise3(
    function_to_test: Callable[[List[List[int]]], List[List[int]]], input: NDArray
):
    res = function_to_test(input.tolist())
    assert res == reference_solution_exercise3(input.tolist()) and res == input.transpose().tolist()


def reference_solution_exercise4(l: List[List[Any]]) -> List[Any]:
    return functools.reduce(lambda x, y: x + y, l)


@pytest.mark.parametrize(
    "input, reference_func",
    [
        ([[1, 2, 3, 4], [4, 5, 5], [4, 5, 6]], reference_solution_exercise4),
        ([["a", "b", "c"], ["d", "f", "e"], ["another"]], reference_solution_exercise4),
    ],
)
def test_exercise4(
    function_to_test: Callable[[List[List[any]]], List[Any]],
    input: List[List[Any]],
    reference_func: Callable,
):
    assert function_to_test(input) == reference_func(input)


@functools.lru_cache
def get_data_exercise5() -> List[str]:
    words = requests.get("https://www.mit.edu/~ecprice/wordlist.10000").text
    return words.splitlines()


def reference_solution_exercise5(w: List[str]) -> List[Tuple[str, int]]:
    return [
        (k, len(list(v)))
        for k, v in itertools.groupby(sorted(w, key=lambda x: x[0]), key=lambda x: x[0])
    ]


def test_exercise5(function_to_test: Callable[[List[str]], List[Tuple[str, int]]]):
    data = get_data_exercise5()
    assert function_to_test(data) == reference_solution_exercise5(data)



def reference_solution_exercise6(l: List[Tuple[str, int]]) -> List[Tuple[str, float]]:
    total = sum(map(lambda x: x[1], l))
    return [(letter, freq/total) for letter, freq in l] 

def test_exercise6(function_to_test: Callable[[List[Tuple[str, int]]], List[Tuple[str, float]]]):
    input_data = reference_solution_exercise5(get_data_exercise5())
    assert function_to_test(input_data) == reference_solution_exercise6(input_data)


def reference_function_exercise7(l: List[str]) -> List[str]:
    return list(filter(lambda x: x == x[::-1] and len(x) > 1, l))

def test_exercise7(function_to_test: Callable[[List[str]], List[str]]):
    data = get_data_exercise5()
    assert function_to_test(data) == reference_function_exercise7(data)