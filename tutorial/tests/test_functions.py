import inspect
import pathlib
from collections import Counter
from string import ascii_lowercase, ascii_uppercase
from typing import Any, List

import pytest


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    return (pathlib.Path(__file__).parent / f"{data_dir}/{name}").resolve()


def errors_to_list(errors):
    result = "<ul>"
    for error in errors:
        result += "<li>" + error + "</li>"
    result += "</ul>"
    return result


#
# Exercise 1: a `greet` function
#


def reference_greet(name: str, age: int) -> str:
    """Reference solution for the greet exercise"""
    return f"Hello, {name}! You are {age} years old."


@pytest.mark.parametrize(
    "name,age",
    [
        ("John", 30),
    ],
)
def test_greet(
    name: str,
    age: int,
    function_to_test,
) -> None:
    errors = []

    signature = inspect.signature(function_to_test)
    params = signature.parameters
    return_annotation = signature.return_annotation

    if function_to_test.__doc__ is None:
        errors.append("The function is missing a docstring.")
    if len(params) != 2:
        errors.append("The function should take two arguments.")
    if "name" not in params.keys() or "age" not in params.keys():
        errors.append("The function's parameters should be 'name' and 'age'.")
    if any(p.annotation == inspect.Parameter.empty for p in params.values()):
        errors.append("The function's parameters should have type hints.")
    if return_annotation == inspect.Signature.empty:
        errors.append("The function's return value is missing the type hint.")

    # test signature
    assert not errors, errors_to_list(errors)
    # test result
    assert function_to_test(name, age) == reference_greet(name, age)


#
# Exercise 2: calculate area with units
#


def reference_calculate_area(length: float, width: float, unit: str = "cm") -> str:
    """Reference solution for the calculate_area exercise"""
    # Conversion factors from supported units to centimeters
    units = {
        "cm": 1.0,
        "m": 100.0,
        "mm": 10.0,
        "yd": 91.44,
        "ft": 30.48,
    }

    try:
        area = length * width * units[unit] ** 2
    except KeyError:
        return f"Invalid unit: {unit}"
    else:
        return f"{area} cm^2"


def test_calculate_area_signature(function_to_test) -> None:
    errors = []

    signature = inspect.signature(function_to_test)
    params = signature.parameters
    return_annotation = signature.return_annotation

    if function_to_test.__doc__ is None:
        errors.append("The function is missing a docstring.")
    if len(params) != 3:
        errors.append("The function should take three arguments.")
    if (
        "length" not in params.keys()
        or "width" not in params.keys()
        or "unit" not in params.keys()
    ):
        errors.append(
            "The function's parameters should be 'length', 'width' and 'unit'."
        )
    if "unit" in params.keys() and not (
        params["unit"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        and params["unit"].default == "cm"
    ):
        errors.append("Argument 'unit' should have a default value 'cm'.")
    if any(p.annotation == inspect.Parameter.empty for p in params.values()):
        errors.append("The function's parameters should have type hints.")
    if return_annotation == inspect.Signature.empty:
        errors.append("The function's return value is missing the type hint.")

    assert not errors, errors_to_list(errors)


@pytest.mark.parametrize(
    "length,width,unit",
    [
        (2.0, 3.0, "cm"),
        (4.0, 5.0, "m"),
        (10.0, 2.0, "mm"),
        (2.0, 8.0, "yd"),
        (5.0, 4.0, "ft"),
        (3.0, 5.0, "in"),
    ],
)
def test_calculate_area_result(
    length: float,
    width: float,
    unit: str,
    function_to_test,
) -> None:
    errors = []

    if unit in ("cm", "m", "mm", "yd", "ft"):
        result = function_to_test(length, width, unit)

        if not isinstance(result, str):
            errors.append("The function should return a string.")
        if "cm^2" not in result:
            errors.append("The result should be in squared centimeters (cm^2).")
        if result != reference_calculate_area(length, width, unit):
            errors.append("The solution is incorrect.")
    else:
        try:
            result = function_to_test(length, width, unit)
        except KeyError:
            errors.append(
                "The function should return an error string for unsupported units."
            )
        else:
            if result != f"Invalid unit: {unit}":
                errors.append("The error message is incorrectly formatted.")

    assert not errors


#
# Exercise 3: summing anything
#


def reference_summing_anything(*args: Any) -> Any:
    """Reference solution for the summing_anything exercise"""
    if not args:
        return args

    result = args[0]

    for item in args[1:]:
        result += item

    return result


@pytest.mark.parametrize(
    "args,expected",
    [
        ((), ()),
        ((1, 2, 3), 6),
        (([1, 2, 3], [4, 5, 6]), [1, 2, 3, 4, 5, 6]),
        (("hello", "world"), "helloworld"),
    ],
)
def test_summing_anything(args: Any, expected: Any, function_to_test) -> None:
    assert function_to_test(*args) == expected


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

prio = {letter: i for i, letter in enumerate(ascii_lowercase + ascii_uppercase, start=1)}
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
