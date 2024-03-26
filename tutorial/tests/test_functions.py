import inspect
import pathlib
from collections import Counter
from string import ascii_lowercase, ascii_uppercase
from typing import List

import pytest


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    return (pathlib.Path(__file__).parent / f"{data_dir}/{name}").resolve()


#
# Exercise 1: a `greet` function
#


def reference_greet(name: str, age: int) -> str:
    """Reference solution for the greet function"""
    return f"Hello {name}, you are {age} years old."


def test_greet(function_to_test) -> None:
    assert function_to_test.__doc__ is not None, "The function is missing a docstring"

    signature = inspect.signature(function_to_test)
    params = signature.parameters
    return_annotation = signature.return_annotation

    assert len(params) == 2, "The function should take two arguments"
    assert (
        "name" in params.keys() and "age" in params.keys()
    ), "The function's parameters should be 'name' and 'age'"

    assert all(
        p.annotation != inspect.Parameter.empty for p in params.values()
    ), "The function's parameters should have type hints"
    assert (
        return_annotation != inspect.Signature.empty
    ), "The function's return value is missing the type hint"


#
# Exercise: Longest Sequence
#


def reference_longest_sequence(nums: List[int]) -> int:
    """
    Find the longest consecutive sequence of integers

    This is the best solution achievable: O(n)
    """
    longest = 0
    nums_set = set(nums)

    for num in nums_set:
        if num - 1 not in nums_set:
            cur = num
            cur_streak = 1

            while cur + 1 in nums_set:
                cur += 1
                cur_streak += 1

            longest = max(longest, cur_streak)

    return longest


@pytest.mark.parametrize(
    "input_nums",
    [
        [100, 4, 200, 1, 3, 2],
        [0, 3, 7, 2, 5, 8, 4, 6, 0, 1],
        [0, 2, 14, 12, 4, 18, 16, 8, 10, 6],
    ],
)
def test_longest_sequence(input_nums: List[int], function_to_test) -> None:
    assert function_to_test(input_nums) == reference_longest_sequence(input_nums)


@pytest.mark.timeout(60)
@pytest.mark.parametrize(
    "input_nums",
    [
        [int(x) for x in read_data("longest_10000.txt").read_text().splitlines()],
    ],
)
def test_longest_sequence_best(input_nums: List[int], function_to_test) -> None:
    assert function_to_test(input_nums) == reference_longest_sequence(input_nums)


#
# Exercise: Password Validator
#


def reference_password_validator1(start: int, end: int) -> int:
    """Password validator reference solution (part 1)"""
    count = 0
    for pwd in range(start, end + 1):
        pwd = list(str(pwd))
        if pwd == sorted(pwd) and len(pwd) != len(set(pwd)):
            count += 1
    return count


def reference_password_validator2(start: int, end: int) -> int:
    """Password validator reference solution (part 2)"""
    count = 0
    for pwd in range(start, end + 1):
        pwd = list(str(pwd))
        if pwd == sorted(pwd):
            counter = Counter(pwd).values()
            if list(counter).count(2) >= 1:
                count += 1
    return count


@pytest.mark.parametrize(
    "start,end",
    [
        (138241, 674034),
        (136760, 595730),
    ],
)
def test_password_validator1(start: int, end: int, function_to_test) -> None:
    assert function_to_test(start, end) == reference_password_validator1(start, end)


@pytest.mark.parametrize(
    "start,end",
    [
        (138241, 674034),
        (136760, 595730),
    ],
)
def test_password_validator2(start: int, end: int, function_to_test) -> None:
    assert function_to_test(start, end) == reference_password_validator2(start, end)


#
# Exercise: Buckets reorganization
#

prio = {l: i for i, l in enumerate(ascii_lowercase + ascii_uppercase, start=1)}
buckets_1, buckets_2 = (read_data(f"buckets_{num}.txt") for num in (1, 2))


def reference_buckets1(buckets: pathlib.Path) -> int:
    """Reference solution (part 1)"""
    data = buckets.read_text().splitlines()
    total = 0
    for line in data:
        mid = len(line) // 2
        first, second = set(line[:mid]), set(line[mid:])
        common = (first & second).pop()
        total += prio[common]
    return total


def reference_buckets2(buckets: pathlib.Path) -> int:
    """Reference solution (part 2)"""
    data = buckets.read_text().splitlines()
    total = 0
    i = 0
    for line in data[::3]:
        group = set(line) & set(data[i + 1]) & set(data[i + 2])
        total += prio[group.pop()]
        i += 3
    return total


@pytest.mark.parametrize(
    "buckets",
    [buckets_1, buckets_2],
)
def test_buckets1(buckets: pathlib.Path, function_to_test):
    assert function_to_test(buckets) == reference_buckets1(buckets)


@pytest.mark.parametrize(
    "buckets",
    [buckets_1, buckets_2],
)
def test_buckets2(buckets: pathlib.Path, function_to_test):
    assert function_to_test(buckets) == reference_buckets2(buckets)
