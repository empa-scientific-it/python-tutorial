import contextlib
import pathlib
from math import isclose, sqrt
from typing import Any, List, Optional, Tuple

import pytest


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    return (pathlib.Path(__file__).parent / f"{data_dir}/{name}").resolve()


#
# Warm-up exercises
#


def reference_indexed_string(string: str) -> List[Tuple[str, int]]:
    """Reference solution warm-up 1"""
    result = []
    for i, char in enumerate(string):
        result.append((char, i))
    return result


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


def reference_range_of_nums(start: int, end: int) -> List[int]:
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
    assert reference_range_of_nums(start, end) == function_to_test(start, end), (
        "The function returned an empty range"
    )


def reference_sqrt_of_nums(numbers: List[int]) -> List[float]:
    """Reference solution warm-up 3"""
    result = []
    for num in numbers:
        if num >= 0:
            result.append(sqrt(num))
    return result


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
    assert len(reference) == len(result), (
        "The function should return a list of the same length"
    )
    assert all(isclose(x, y) for x, y in zip(reference, result)), (
        "The function should return the square root of each number"
    )


def reference_divide_until(number: int) -> int:
    """Reference solution warm-up 4"""
    while number % 2 == 0:
        number //= 2
    return number


@pytest.mark.parametrize(
    "num", [8134, 92337, 27836, 79264, 85954, 50557, 68360, 58765, 76419, 5864]
)
def test_divide_until(num: int, function_to_test) -> None:
    assert reference_divide_until(num) == function_to_test(num)


#
# Exercise: conditionals inside loops
#


def reference_filter_by_position(numbers: List[int]) -> List[int]:
    result = set()
    for pos, number in enumerate(numbers, start=1):
        if number > pos:
            result.add(number)
    return sorted(result)


@pytest.mark.parametrize(
    "numbers",
    [
        [0, 3, 1, 2],  # Basic case from example = {3}
        [5, 4, 3, 2, 1],  # Decreasing numbers = {4, 5}
        [1, 3, 5, 7, 9],  # All odd numbers = {3, 5, 7, 9}
        [],  # Empty list = {}
        [0, 0, 0],  # Same numbers with none valid = {}
        [2, 2, 2, 2],  # Same number with one valid = {2}
        [4, 4, 4, 4],  # Same number, three are valid but they are duplicates = {4}
        [10, 20, 1, 2, 3],  # Mixed large and small numbers = {10, 20}
    ],
)
def test_filter_by_position(numbers: List[int], function_to_test) -> None:
    """Test filtering numbers by position."""
    assert function_to_test(numbers) == reference_filter_by_position(numbers)


#
# Exercise: breaking out of loops
#


def reference_find_even_multiple_three(numbers: List[int]) -> Optional[int]:
    result = None
    for number in numbers:
        if number % 2 == 0 and number % 3 == 0:
            result = number
            break
    return result


@pytest.mark.parametrize(
    "numbers",
    [
        [1, 2, 3, 4, 6, 8],  # 6 is first even multiple of 3 = 6
        [1, 3, 5, 7, 9],  # No even numbers = None
        [12, 18, 24],  # All are valid, should return the first = 12
        [],  # Empty list = None
        [2, 4, 6, 8, 10],  # Even numbers but no multiples of 3 = None
        [1, 3, 5, 7, 12],  # Valid number at the end = 12
    ],
)
def test_find_even_multiple_three(numbers: List[int], function_to_test) -> None:
    """Test finding first even multiple of 3."""
    assert function_to_test(numbers) == reference_find_even_multiple_three(numbers)


#
# Exercise: using else in loops
#


def reference_is_pure_number(text: str) -> bool:
    for char in text:
        if char not in "1234567890":
            return False
    else:
        return True


def is_for_else_used(function) -> bool:
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(function))
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and node.orelse:
            return True
    return False


@pytest.mark.parametrize(
    "text",
    [
        "123456",  # OK
        "0987654321",  # OK
        "",  # Empty
        "abc123",  # Mixed characters
        "0000",  # All zeros
        "12.34",  # With decimal point
        "    ",  # All spaces
        "-123",  # With negative sign
        "١٢٣",  # Non-ASCII digits (should return False)
    ],
)
def test_is_pure_number(text: str, function_to_test) -> None:
    """Test checking for pure number strings."""
    assert is_for_else_used(function_to_test), "You must use a for-else construct"
    assert function_to_test(text) == reference_is_pure_number(text)


#
# Exercise 1: Find the factors
#


def reference_find_factors(num: int) -> List[int]:
    """Reference solution to find the factors of an integer"""
    factors = []
    for m in range(1, num + 1):
        if num % m == 0:
            factors.append(m)
    return factors


@pytest.mark.parametrize("num", [350, 487, 965, 816, 598, 443, 13, 17, 211])
def test_find_factors(num: int, function_to_test) -> None:
    assert function_to_test(num) == reference_find_factors(num)


#
# Exercise 2: Find the pair/triplet
#

nums_1, nums_2 = (
    [int(x) for x in read_data(f"2020_{i}.txt").read_text().splitlines()]
    for i in (1, 2)
)


def reference_find_pair(nums: List[int]):
    """
    Reference solutions:
        - A solution with two nested loops
        - A solution using a dictionary and a single loop
    """

    def find_pair_with_double_loop(nums: List[int]) -> Optional[int]:
        """Two nested loops"""
        for i in nums:
            for j in nums:
                if i + j == 2020:
                    return i * j

    def find_pair_with_sets(nums: List[int]) -> Optional[int]:
        """Using a dictionary and a single loop"""
        complements = {}
        for num in nums:
            if num in complements:
                return num * complements[num]
            complements[2020 - num] = num


def __reference_find_pair(nums: List[int]) -> Optional[int]:
    """Reference solution (part 1)"""
    complements = {}
    for num in nums:
        if num in complements:
            return num * complements[num]
        complements[2020 - num] = num


@pytest.mark.parametrize("nums", [nums_1, nums_2])
def test_find_pair(nums: List[int], function_to_test) -> None:
    assert function_to_test(nums) == __reference_find_pair(nums)


def reference_find_triplet(nums: List[int]):
    """
    Reference solutions:
        - A slow solution with three nested loops
        - A fast solution using only two loops
    """

    def find_triplet_slow(nums: List[int]) -> Optional[int]:
        """Slow solution with a triple loop"""
        n = len(nums)
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                for k in range(j + 1, n):
                    if nums[i] + nums[j] + nums[k] == 2020:
                        return nums[i] * nums[j] * nums[k]

    def find_triplet_best(nums: List[int]) -> Optional[int]:
        """Fast solution with two loops"""
        n = len(nums)
        for i in range(n - 1):
            s = set()
            target_sum = 2020 - nums[i]
            for j in range(i + 1, n):
                last_num = target_sum - nums[j]
                if last_num in s:
                    return nums[i] * nums[j] * last_num
                s.add(nums[j])


def __reference_find_triplet(nums: List[int]) -> Optional[int]:
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
    assert function_to_test(nums) == __reference_find_triplet(nums)


#
# Exercise 3: Cats with hats
#


def reference_cats_with_hats() -> int:
    """Solution with dictionaries"""
    cats = dict.fromkeys(range(1, 101), False)

    for loop in range(1, 101):
        for cat, has_hat in cats.items():
            if cat % loop == 0:
                cats[cat] = not has_hat

    return sum(cats.values())


def test_cats_with_hats(function_to_test) -> None:
    assert function_to_test() == reference_cats_with_hats()


#
# Exercise 4: Base converter
#


def reference_base_converter(number: str, from_base: int, to_base: int) -> str:
    """Reference solution to convert a number from one base to another"""
    # Validate bases
    if not (2 <= from_base <= 16 and 2 <= to_base <= 16):
        err = "Bases must be between 2 and 16"
        raise ValueError(err)

    # Handle empty input
    if not number or number.strip() in ("", "-"):
        err = "Invalid empty input"
        raise ValueError(err)

    # Same to and from bases
    if from_base == to_base:
        return number

    # Handle negative numbers
    is_negative = number.strip().startswith("-")
    number = number.strip().removeprefix("-")

    # Remove spaces and convert to uppercase for consistency
    number = number.replace(" ", "").upper()

    # Validate digits
    valid_digits = "0123456789ABCDEF"
    for digit in number:
        if digit not in valid_digits[:from_base]:
            err = f"Invalid digit '{digit}' for base {from_base}"
            raise ValueError(err)

    # Convert to base 10
    decimal = 0
    for digit in number:
        decimal = decimal * from_base + valid_digits.index(digit)

    # Handle 0 as a special case
    if decimal == 0:
        return "0"

    if to_base == 10:
        return str(decimal)

    # Convert to target base
    result = ""
    while decimal > 0:
        digit = decimal % to_base
        result += valid_digits[digit]
        decimal //= to_base

    return f"-{result}" if is_negative else result


# We need a way to "disable" the use of `int()`, otherwise it's too easy
# Solution: replace `int()` with a function that raises an exception using a context manager
@contextlib.contextmanager
def block_int():
    """Context manager to block int() usage"""
    original_int = int

    class IntReplacement:
        def __call__(self, *args, **kwargs):
            import inspect

            frame = inspect.currentframe()
            while frame:
                if frame.f_code.co_name == "solution_base_converter":
                    raise AssertionError("Using int() is not allowed.")  # noqa: TRY003
                frame = frame.f_back
            return original_int(*args, **kwargs)

        def __instancecheck__(self, instance: Any, /) -> bool:
            return isinstance(instance, original_int)

    import builtins

    builtins.int = IntReplacement()

    try:
        yield
    finally:
        builtins.int = original_int


@pytest.mark.parametrize(
    "number,from_base,to_base", [("42", 10, 2), ("1A", 16, 2), ("1010", 2, 16)]
)
def test_base_converter_basics(number, from_base, to_base, function_to_test):
    with block_int():
        expected = reference_base_converter(number, from_base, to_base)
        assert function_to_test(number, from_base, to_base) == expected


@pytest.mark.parametrize(
    "number,from_base,to_base", [("10 10", 2, 10), ("FF FF", 16, 2)]
)
def test_base_converter_with_spaces(number, from_base, to_base, function_to_test):
    with block_int():
        expected = reference_base_converter(number, from_base, to_base)
        assert function_to_test(number, from_base, to_base) == expected


@pytest.mark.parametrize("number,from_base,to_base", [("-42", 10, 2), ("-FF", 16, 10)])
def test_base_converter_negative_numbers(number, from_base, to_base, function_to_test):
    with block_int():
        expected = reference_base_converter(number, from_base, to_base)
        assert function_to_test(number, from_base, to_base) == expected


@pytest.mark.parametrize(
    "number,from_base,to_base", [("ff", 16, 10), ("FF", 16, 10), ("Ff", 16, 10)]
)
def test_base_converter_case_insensitive(number, from_base, to_base, function_to_test):
    with block_int():
        expected = reference_base_converter(number, from_base, to_base)
        assert function_to_test(number, from_base, to_base) == expected


@pytest.mark.parametrize(
    "number,from_base,to_base", [("42", 1, 10), ("42", 10, 17), ("42", 0, 0)]
)
def test_base_converter_invalid_bases(number, from_base, to_base, function_to_test):
    with block_int():
        with pytest.raises(ValueError):
            reference_base_converter(number, from_base, to_base)
        with pytest.raises(ValueError):
            function_to_test(number, from_base, to_base)


@pytest.mark.parametrize(
    "number,from_base,to_base",
    [
        ("2", 2, 10),  # 2 not valid in base 2
        ("G", 16, 2),  # G not valid in base 16
        ("9", 8, 2),  # 9 not valid in base 8
    ],
)
def test_base_converter_invalid_digits(number, from_base, to_base, function_to_test):
    with block_int():
        with pytest.raises(ValueError):
            function_to_test(number, from_base, to_base)


@pytest.mark.parametrize(
    "number,from_base,to_base", [("", 2, 2), (" ", 2, 2), ("-", 2, 2)]
)
def test_base_converter_empty_or_invalid_input(
    number, from_base, to_base, function_to_test
):
    with block_int():
        with pytest.raises(ValueError):
            function_to_test(number, from_base, to_base)
