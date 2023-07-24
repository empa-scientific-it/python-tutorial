import pathlib
import sys
from collections import Counter
from math import isqrt, sqrt, isclose
from typing import List, Tuple

import pytest


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    current_module = sys.modules[__name__]
    return (
        pathlib.Path(current_module.__file__).parent / f"{data_dir}/{name}"
    ).resolve()


#
# Warm-up exercises
#


def reference_indexed_string(string: str) -> list[tuple[str, int]]:
    """Reference solution warm-up 1"""
    return [(char, index) for index, char in enumerate(string)]


@pytest.mark.parametrize(
    "string",
    [
        "manner",
        "reigning",
        "complaint",
        "annotator",
        "assessable",
        "fabricated",
        "organs",
        "swindle",
        "imminently",
        "uncomfortableness",
    ],
)
def test_indexed_string(string: str, function_to_test) -> None:
    result = function_to_test(string)
    assert result is not None, "The function should return a list, not 'None'"
    assert reference_indexed_string(string) == result


def reference_range_of_nums(start: int, end: int) -> list[int]:
    """Reference solution warm-up 2"""
    step = 1 if start < end else -1
    return list(range(start, end + step, step))


@pytest.mark.parametrize(
    "start,end",
    [
        (1, 10),
        (99, 20),
        (-20, 30),
        (30, 100),
        (0, -30),
    ],
)
def test_range_of_nums(start: int, end: int, function_to_test) -> None:
    assert reference_range_of_nums(start, end) == function_to_test(
        start, end
    ), "The function returned an empty range"


def reference_sqrt_of_nums(nums: list[int]) -> list[float]:
    """Reference solution warm-up 3"""
    return [sqrt(num) for num in nums if num >= 0]


@pytest.mark.parametrize(
    "nums",
    [
        [
            -704,
            21,
            505,
            -452,
            -244,
            -800,
        ],
        [
            517,
            -524,
            -883,
            -393,
            100,
            2,
            81,
        ],
    ],
)
def test_sqrt_of_nums(nums: list[int], function_to_test) -> None:
    reference, result = reference_sqrt_of_nums(nums), function_to_test(nums)
    assert isinstance(result, list), "The function should return a list, not 'None'"
    assert len(reference) == len(
        result
    ), "The function should return a list of the same length"
    assert all(
        isclose(x, y) for x, y in zip(reference, result)
    ), "The function should return the square root of each number"


def reference_divide_until(num: int) -> int:
    """Reference solution warm-up 4"""
    while num % 2 == 0:
        num //= 2
    return num


@pytest.mark.parametrize(
    "num", [8134, 92337, 27836, 79264, 85954, 50557, 68360, 58765, 76419, 5864]
)
def test_divide_until(num: int, function_to_test) -> None:
    assert reference_divide_until(num) == function_to_test(num)


#
# Exercise 1: Find the factors
#


def is_prime(num: int) -> bool:
    """Check if a number is prime"""
    if num <= 3:
        return num > 1

    if num % 2 == 0 or num % 3 == 0:
        return False

    for i in range(5, isqrt(num) + 1, 6):
        if num % i == 0 or num % (i + 2) == 0:
            return False

    return True


def reference_find_factors(num: int) -> List[int]:
    """Dumb way to find the factors of an integer"""
    if is_prime(num):
        return [1, num]
    return [m for m in range(1, num + 1) if num % m == 0]


@pytest.mark.parametrize("num", [350, 487, 965, 816, 598, 443, 13, 17, 211])
def test_find_factors(num: int, function_to_test) -> None:
    assert function_to_test(num) == reference_find_factors(num)


#
# Exercise 2: Find the pair/triplet
#

nums_1, nums_2 = [
    [int(x) for x in read_data(f"2020_{i}.txt").read_text().splitlines()]
    for i in (1, 2)
]


def reference_find_pair(nums: List[int]) -> int:
    """Reference solution (part 1)"""
    complements = {}
    for num in nums:
        if num in complements:
            return num * complements[num]
        complements[2020 - num] = num


@pytest.mark.parametrize("nums", [nums_1, nums_2])
def test_find_pair(nums: List[int], function_to_test) -> None:
    assert function_to_test(nums) == reference_find_pair(nums)


def reference_find_triplet_slow(nums: List[int]) -> int:
    """Reference solution (part 2), O(n^3)"""
    n = len(nums)
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 2020:
                    return nums[i] * nums_2[j] * nums[k]


def reference_find_triplet(nums: List[int]) -> int:
    """Reference solution (part 2), O(n^2)"""
    n = len(nums)
    for i in range(n - 1):
        s = set()
        target_sum = 2020 - nums[i]
        for j in range(i + 1, n):
            last_num = target_sum - nums[j]
            if last_num in s:
                return nums[i] * nums[j] * last_num
            s.add(nums[j])


@pytest.mark.parametrize("nums", [nums_1, nums_2])
def test_find_triplet(nums: List[int], function_to_test) -> None:
    assert function_to_test(nums) == reference_find_triplet(nums)


#
# Exercise 3: Cats with hats
#


def reference_cats_with_hats() -> int:
    """Solution with dictionaries"""
    cats = {i: False for i in range(1, 101)}

    for loop in range(1, 101):
        for cat, has_hat in cats.items():
            if cat % loop == 0:
                cats[cat] = not has_hat

    return Counter(cats.values())[True]


def test_cats_with_hats(function_to_test) -> None:
    assert function_to_test() == reference_cats_with_hats()


#
# Exercise 4: Toboggan trajectory
#


def parse_data(filename: str) -> List[List[int]]:
    """Parse a map of trees"""
    input_data = read_data(filename).read_text()
    return [
        [1 if pos == "#" else 0 for pos in line] for line in input_data.splitlines()
    ]


trees_1, trees_2 = [parse_data(f"trees_{num}.txt") for num in (1, 2)]


def reference_toboggan_p1(
    trees_map: List[List[int]], right: int, down: int
) -> int:
    """Reference solution (part 1)"""
    start, trees, depth, width = [0, 0], 0, len(trees_map), len(trees_map[0])
    while start[0] < depth:
        trees += trees_map[start[0]][start[1]]
        start = [start[0] + down, (start[1] + right) % width]
    return trees


@pytest.mark.parametrize(
    "trees_map, right, down",
    [
        (trees_1, 3, 1),
        (trees_2, 3, 1),
    ],
)
def test_toboggan_p1(
    trees_map: List[List[int]], right: int, down: int, function_to_test
) -> None:
    assert function_to_test(trees_map, right, down) == reference_toboggan_p1(
        trees_map, right, down
    )


def reference_toboggan_p2(
    trees_map: List[List[int]], slopes: Tuple[Tuple[int]]
) -> int:
    """Reference solution (part 2)"""
    total = 1
    for right, down in slopes:
        total *= reference_toboggan_p1(trees_map, right, down)
    return total


@pytest.mark.parametrize(
    "trees_map, slopes",
    [
        (
            trees_1,
            ((1, 1), (3, 1), (5, 1), (7, 1), (1, 2)),
        ),  # 9354744432
        (
            trees_2,
            ((1, 1), (3, 1), (5, 1), (7, 1), (1, 2)),
        ),  # 1574890240
    ],
)
def test_toboggan_p2(
    trees_map: List[List[int]], slopes: Tuple[Tuple[int]], function_to_test
) -> None:
    assert function_to_test(trees_map, slopes) == reference_toboggan_p2(
        trees_map, slopes
    )
