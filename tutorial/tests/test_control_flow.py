from typing import List, Tuple
import pytest
import pathlib


def read_data(filename: str) -> str:
    """Read input data"""
    # TODO: might need to fix the path
    return pathlib.Path(f"tutorial/tests/data/{filename}").read_text()


#
# Exercise 1: Toboggan trajectory
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
