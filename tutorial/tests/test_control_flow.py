import pathlib
from collections import Counter
from math import factorial
from typing import List, Tuple

import pytest


def read_data(filename: str) -> str:
    """Read input data"""
    # NOTE: the path is relative to the IPython notebook's dir
    return pathlib.Path(f"tutorial/tests/data/{filename}").read_text()


#
# Exercise 1: Find the factors
#

def is_prime(num: int) -> bool:
    """One-liner (non-efficient) to check if a number is prime"""
    return (factorial(num - 1) + 1) % num == 0


def reference_solution_find_factors(num: int) -> List[int]:
    """Dumb way to find the factors of an integer"""
    if is_prime(num):
        return [1, num]
    return [m for m in range(1, num + 1) if num % m == 0]


@pytest.mark.parametrize(
    "num",
    [350, 487, 965, 816, 598, 443, 13, 17, 211]
)
def test_find_factors(num: int, function_to_test) -> None:
    assert function_to_test(num) == reference_solution_find_factors(num)


#
# Exercise 2: Cats with hats
#

def reference_solution_cats_with_hats() -> int:
    """Solution with dictionaries"""
    cats = {i: False for i in range(1, 101)}

    for loop in range(1, 101):
        for cat, has_hat in cats.items():
            if cat % loop == 0:
                cats[cat] = False if has_hat else True

    return Counter(cats.values())[True]


def test_cats_with_hats(function_to_test) -> None:
    assert function_to_test() == reference_solution_cats_with_hats()


#
# Exercise 3: Toboggan trajectory
#

def parse_data(filename: str) -> List[List[int]]:
    """Parse a map of trees"""
    input_data = read_data(filename)
    return [[1 if pos == "#" else 0 for pos in line] for line in input_data.splitlines()]


trees_1, trees_2 = [parse_data(f"trees_{num}.txt") for num in (1, 2)]


@pytest.mark.parametrize(
    "trees_map, right, down, trees",
    [
        (trees_1, 3, 1, 292),
        (trees_2, 3, 1, 209),
    ]
)
def test_toboggan_p1(trees_map: List[List[int]], right: int, down: int, trees: int, function_to_test) -> None:
    assert function_to_test(trees_map, right, down) == trees


@pytest.mark.parametrize(
    "trees_map, slopes, total",
    [
        (trees_1, ((1, 1), (3, 1), (5, 1), (7, 1), (1, 2)), 9354744432),
        (trees_2, ((1, 1), (3, 1), (5, 1), (7, 1), (1, 2)), 1574890240),
    ]
)
def test_toboggan_p2(trees_map: List[List[int]], slopes: Tuple[Tuple[int]], total: int, function_to_test) -> None:
    assert function_to_test(trees_map, slopes) == total
