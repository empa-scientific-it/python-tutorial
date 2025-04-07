import inspect
import pathlib
from collections import Counter
from string import ascii_lowercase, ascii_uppercase
from typing import Any, List

import pytest


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    return (pathlib.Path(__file__).parent / f"{data_dir}/{name}").resolve()


#
# Exercise 1: a `greet` function
#


def reference_greet(name: str, age: int) -> str:
    """Creates a personalized greeting message using name and age.

    Args:
        name: The person's name to include in the greeting
        age: The person's age in years

    Returns:
        - A string in the format "Hello, <name>! You are <age> years old."
    """
    return f"Hello, {name}! You are {age} years old."


def test_greet(
    function_to_test,
) -> None:
    name, age = "Alice", 30

    params = inspect.signature(function_to_test).parameters
    return_annotation = inspect.signature(function_to_test).return_annotation

    # Check docstring
    assert function_to_test.__doc__ is not None, "The function is missing a docstring."

    # Check number and names of parameters
    assert len(params) == 2, "The function should take two arguments."
    assert "name" in params and "age" in params, (
        "The function's parameters should be 'name' and 'age'."
    )

    # Check type hints for parameters
    assert all(p.annotation != inspect.Parameter.empty for p in params.values()), (
        "The function's parameters should have type hints."
    )

    # Check return type hint
    assert return_annotation != inspect.Signature.empty, (
        "The function's return value is missing the type hint."
    )

    # Test the return value
    assert function_to_test(name, age) == reference_greet(name, age)


#
# Exercise 2: calculate area with units
#


# Part 1
def reference_calculate_basic_area(length: float, width: float) -> str:
    """Reference solution for Part 1: basic area calculation."""
    area = round(length * width, 2)
    return f"{area} cm^2"


def validate_basic_area_signature(function_to_test) -> None:
    """Validate signature of the basic area calculation function."""
    signature = inspect.signature(function_to_test)
    params = signature.parameters
    return_annotation = signature.return_annotation

    assert function_to_test.__doc__ is not None, "The function is missing a docstring."
    assert len(params) == 2, (
        "The function should take exactly two arguments (length and width)."
    )
    assert all(p in params.keys() for p in ["length", "width"]), (
        "The function's parameters should be 'length' and 'width'."
    )
    assert all(p.annotation is float for p in params.values()), (
        "Both parameters should be annotated as float."
    )
    assert return_annotation is str, "The return type should be annotated as str."


@pytest.mark.parametrize(
    "length,width",
    [
        (2.0, 3.0),
        (5.0, 4.0),
        (1.5, 2.5),
        (0.1, 0.1),
    ],
)
def test_calculate_basic_area(length: float, width: float, function_to_test):
    validate_basic_area_signature(function_to_test)
    expected = reference_calculate_basic_area(length, width)
    result = function_to_test(length, width)
    assert isinstance(result, str), "Result should be a string"
    assert expected == result, "Incorrect area calculation or formatting"


# Part 2


def reference_calculate_metric_area(
    length: float, width: float, unit: str = "cm"
) -> str:
    """Reference solution for Part 2: metric units only."""
    if unit not in ("cm", "m"):
        return f"Invalid unit: {unit}"

    if unit == "m":
        length *= 100
        width *= 100

    area = round(length * width, 2)
    return f"{area} cm^2"


def validate_metric_area_signature(function_to_test) -> None:
    """Validate signature of the metric area calculation function."""
    signature = inspect.signature(function_to_test)
    params = signature.parameters
    return_annotation = signature.return_annotation

    assert function_to_test.__doc__ is not None, "The function is missing a docstring."
    assert len(params) == 3, (
        "The function should take three arguments (length, width, and unit)."
    )
    assert all(p in params.keys() for p in ["length", "width", "unit"]), (
        "The function's parameters should be 'length', 'width' and 'unit'."
    )
    assert params["length"].annotation is float, (
        "Parameter 'length' should be annotated as float."
    )
    assert params["width"].annotation is float, (
        "Parameter 'width' should be annotated as float."
    )
    assert params["unit"].annotation is str, (
        "Parameter 'unit' should be annotated as str."
    )
    assert params["unit"].default == "cm", (
        "Parameter 'unit' should have a default value of 'cm'."
    )
    assert return_annotation is str, "The return type should be annotated as str."


@pytest.mark.parametrize(
    "length,width,unit",
    [
        (2.0, 3.0, "cm"),
        (2.0, 3.0, "m"),
        (1.5, 2.0, "cm"),
        (1.5, 2.0, "m"),
    ],
)
def test_calculate_metric_area(length, width, unit, function_to_test):
    validate_metric_area_signature(function_to_test)
    expected = reference_calculate_metric_area(length, width, unit)
    result = function_to_test(length, width, unit)
    assert isinstance(result, str), "Result should be a string"
    assert expected == result, "Incorrect area calculation or formatting"


# Part 3


def reference_calculate_area(length: float, width: float, unit: str = "cm") -> str:
    """Reference solution for Part 3: all units."""
    conversions = {"cm": 1, "m": 100, "mm": 0.1, "yd": 91.44, "ft": 30.48}

    try:
        factor = conversions[unit]
    except KeyError:
        return f"Invalid unit: {unit}"

    area = round(length * width * factor**2, 2)
    return f"{area} cm^2"


def validate_area_signature(function_to_test) -> None:
    """Validate signature of the full area calculation function."""
    signature = inspect.signature(function_to_test)
    params = signature.parameters
    return_annotation = signature.return_annotation

    assert function_to_test.__doc__ is not None, "The function is missing a docstring."
    assert len(params) == 3, (
        "The function should take three arguments (length, width, and unit)."
    )
    assert all(p in params.keys() for p in ["length", "width", "unit"]), (
        "The function's parameters should be 'length', 'width' and 'unit'."
    )
    assert params["length"].annotation is float, (
        "Parameter 'length' should be annotated as float."
    )
    assert params["width"].annotation is float, (
        "Parameter 'width' should be annotated as float."
    )
    assert params["unit"].annotation is str, (
        "Parameter 'unit' should be annotated as str."
    )
    assert params["unit"].default == "cm", (
        "Parameter 'unit' should have a default value of 'cm'."
    )
    assert return_annotation is str, "The return type should be annotated as str."


@pytest.mark.parametrize(
    "length,width,unit",
    [
        (2.0, 3.0, "cm"),
        (2.0, 3.0, "m"),
        (2.0, 3.0, "mm"),
        (2.0, 3.0, "yd"),
        (2.0, 3.0, "ft"),
    ],
)
def test_calculate_area(length, width, unit, function_to_test):
    validate_area_signature(function_to_test)
    result = function_to_test(length, width, unit)
    expected = reference_calculate_area(length, width, unit)
    assert isinstance(result, str), "Result should be a string"
    assert expected == result, "Incorrect area calculation or formatting"


#
# Exercise 3: summing anything
#


def reference_combine_anything(*args: Any) -> Any:
    """Reference solution for the combine_anything exercise"""
    if not args:
        return args

    result = args[0]

    for item in args[1:]:
        result += item

    return result


@pytest.mark.parametrize(
    "args",
    [
        (()),
        ((1, 2, 3)),
        (([1, 2, 3], [4, 5, 6])),
        (("hello", "world")),
    ],
)
def test_combine_anything(args: Any, function_to_test) -> None:
    assert function_to_test(*args) == reference_combine_anything(*args)


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

prio = {
    letter: i for i, letter in enumerate(ascii_lowercase + ascii_uppercase, start=1)
}
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
