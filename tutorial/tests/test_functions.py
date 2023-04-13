import pytest
from typing import List, Tuple
import pathlib


def read_data(filename: str) -> str:
    """Read input data"""
    # TODO: might need to fix the path
    return pathlib.Path(f"tutorial/tests/data/{filename}").read_text()


#
# Exercise 1: Longest Sequence
#

def reference_solution_longest_sequence(nums: List[int]) -> int:
    """Find the longest consecutive sequence of integers"""


@pytest.mark.parametrize(
    "input_nums, expected_len",
    [
        ([100, 4, 200, 1, 3, 2], 4),
        ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9),
        ([0, 2, 14, 12, 4, 18, 16, 8, 10, 6], 1),
    ]
)
def test_longest_sequence(input_nums: List[int], expected_len: int, function_to_test) -> None:
    assert function_to_test(input_nums) == expected_len


@pytest.mark.timeout(60)
@pytest.mark.parametrize(
    "input_nums, expected_length",
    [
        ([int(x) for x in read_data("longest_10000.txt").splitlines()], 7095),
    ]
)
def test_longest_sequence_best(input_nums: List[int], expected_length: int, function_to_test) -> None:
    assert function_to_test(input_nums) == expected_length


#
# Exercise 2: Password Validator
#

@pytest.mark.parametrize(
    "pwd_range, valid_pwd",
    [
        ((138241, 674034), 1890),
        ((136760, 595730), 1873),
    ]
)
def test_password_validator1(pwd_range: Tuple[int], valid_pwd: int, function_to_test) -> None:
    assert function_to_test(*pwd_range) == valid_pwd


@pytest.mark.parametrize(
    "pwd_range, valid_pwd",
    [
        ((138241, 674034), 1277),
        ((136760, 595730), 1264),
    ]
)
def test_password_validator2(pwd_range: Tuple[int], valid_pwd: int, function_to_test) -> None:
    assert function_to_test(*pwd_range) == valid_pwd


#
# Exercise 3: Buckets reorganization
#

buckets_1, buckets_2 = [read_data(f"buckets_{num}.txt") for num in (1, 2)]

@pytest.mark.parametrize(
    "buckets, total_prio",
    [
        (buckets_1, 7568),
        (buckets_2, 7701)
    ]
)
def test_buckets1(buckets: str, total_prio: int, function_to_test):
    assert function_to_test(buckets) == total_prio


@pytest.mark.parametrize(
    "buckets, total_prio",
    [
        (buckets_1, 2780),
        (buckets_2, 2644)
    ]
)
def test_buckets2(buckets: str, total_prio: int, function_to_test):
    assert function_to_test(buckets) == total_prio
