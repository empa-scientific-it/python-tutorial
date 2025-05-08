import pathlib
import random
import re
import time
import typing as t
from math import isclose
from string import ascii_lowercase as lowercase
from string import ascii_uppercase as uppercase  # noqa: F401
from string import digits, punctuation  # noqa: F401

import pytest


#
# Example: Randomize list
#
def reference_randomize_list(my_list: list[int]) -> list[int]:
    return sorted(my_list, key=lambda x: random.random())


@pytest.mark.parametrize(
    "my_list",
    [
        ([1, 2, 3, 4]),
        (list(range(100))),
    ],
)
def test_randomize_list(
    function_to_test: t.Callable,
    my_list: list[int],
):
    assert function_to_test(my_list) == reference_randomize_list(my_list)


#
# Exercise: Password checker factory
#
def reference_password_checker_factory(
    min_up: int, min_low: int, min_pun: int, min_dig: int
) -> t.Callable:
    """Password checker factory"""
    # The `string` module contains a number of useful constants
    import string

    # The `sub` function from the operator module can be used to subtract two numbers
    # sub(x, y) is equivalent to x - y
    from operator import sub

    def password_checker(password: str) -> tuple[bool, dict]:
        """Password checker function"""

        # Counts the number of chars for each class in a password
        counts = [
            sum(1 for char in password if char in _class)
            for _class in (
                string.ascii_uppercase,
                string.ascii_lowercase,
                string.punctuation,
                string.digits,
            )
        ]

        # Compare with requirements and calculate the differences
        diffs = [
            sub(*pair) for pair in zip(counts, (min_up, min_low, min_pun, min_dig))
        ]

        result = dict(zip(("uppercase", "lowercase", "punctuation", "digits"), diffs))

        return all(diff >= 0 for diff in diffs), result

    return password_checker


def test_password_checker_factory_no_min_no_pw(function_to_test: t.Callable):
    pc = function_to_test(0, 0, 0, 0)
    result, details = pc("")

    assert result
    assert len(details) == 4
    for value in details.values():
        assert value == 0


def test_password_checker_factory_no_min_some_pw(function_to_test: t.Callable):
    pc = function_to_test(0, 0, 0, 0)
    result, details = pc("ABCDefgh!@#$1234")

    assert result
    assert len(details) == 4
    for value in details.values():
        assert value == 4


def test_password_checker_factory_simple_good(function_to_test: t.Callable):
    pc = function_to_test(1, 2, 3, 4)
    result, details = pc("Abc!@#1234")

    assert result
    assert len(details) == 4
    for value in details.values():
        assert value == 0


def test_password_checker_factory_simple_bad(function_to_test: t.Callable):
    pc = function_to_test(1, 2, 3, 4)
    result, details = pc("b!#234")

    assert not result
    assert len(details) == 4
    for value in details.values():
        assert value == -1


@pytest.mark.parametrize("onlyset", ["uppercase", "lowercase", "punctuation", "digits"])
def test_password_checker_factory_only_set_one(onlyset, function_to_test: t.Callable):
    for source in ["uppercase", "lowercase", "punctuation", "digits"]:
        if onlyset == source:
            pw = globals()[source][:4]

    pc = function_to_test(4, 4, 4, 4)
    result, details = pc(pw)  # type: ignore

    assert not result
    assert len(details) == 4
    for key, value in details.items():
        if key == onlyset:
            assert value == 0
        else:
            assert value == -4


@pytest.mark.parametrize(
    "donotset", ["uppercase", "lowercase", "punctuation", "digits"]
)
def test_password_checker_factory_only_ignore_one(
    donotset, function_to_test: t.Callable
):
    pw = ""
    for source in ["uppercase", "lowercase", "punctuation", "digits"]:
        if donotset == source:
            continue
        pw += globals()[source][:4]

    pc = function_to_test(4, 4, 4, 4)
    result, details = pc(pw)

    assert not result
    assert len(details) == 4
    for key, value in details.items():
        if key == donotset:
            assert value == -4
        else:
            assert value == 0


#
# Exercise: Once per minute
#


def hello(name):
    return f"Hello {name}!"


def reference_once(allowed_time: int = 15) -> t.Callable:
    """Decorator to run a function at most once"""

    class TooSoonError(RuntimeError):
        def __init__(self, wait: float):
            super().__init__(f"Wait another {wait:.2f} seconds")

    def decorator(func: t.Callable) -> t.Callable:
        timer = 0.0

        def wrapper(*args, **kwargs) -> t.Any:
            """Wrapper"""
            nonlocal timer

            if not timer:
                timer = time.perf_counter()
                return func(*args, **kwargs)

            if (stop := time.perf_counter()) - timer < allowed_time:
                raise TooSoonError(allowed_time - (stop - timer))

            timer = time.perf_counter()

            return func(*args, **kwargs)

        return wrapper

    return decorator


def test_once_simple(function_to_test: t.Callable) -> None:
    _hello = function_to_test(5)(hello)
    assert _hello("world") == "Hello world!"


def test_once_twice(function_to_test: t.Callable) -> None:
    allowed_time = 5
    _hello = function_to_test(allowed_time)(hello)

    time.sleep(allowed_time)
    assert _hello("world") == "Hello world!"

    with pytest.raises(RuntimeError) as err:
        _hello("world 2")

    assert err.type is RuntimeError
    assert "Wait another" in err.value.args[0]

    wait_time = re.search(r"[\d.]+", err.value.args[0])
    assert wait_time and isclose(float(wait_time.group()), 5.0, abs_tol=1e-2)


def test_once_waiting_not_enough_time(function_to_test: t.Callable) -> None:
    allowed_time = 10
    _hello = function_to_test(allowed_time)(hello)

    time.sleep(allowed_time)
    assert _hello("world") == "Hello world!"
    time.sleep(allowed_time - 1)

    with pytest.raises(RuntimeError) as err:
        _hello("world 2")

    assert err.type is RuntimeError
    assert "Wait another" in err.value.args[0]

    wait_time = re.search(r"[\d.]+", err.value.args[0])
    assert wait_time and isclose(float(wait_time.group()), 1.0, abs_tol=1e-2)


def test_once_waiting_enough_time(function_to_test: t.Callable) -> None:
    # Test that waiting the allowed time lets the function run again
    allowed_time = 2
    _hello = function_to_test(allowed_time)(hello)

    # First call should work
    assert _hello("world") == "Hello world!"

    # Wait for the full allowed time
    time.sleep(allowed_time + 0.1)  # Add small buffer to avoid timing issues

    # Second call should work
    assert _hello("world 2") == "Hello world 2!"


#
# Exercise: String range
#


def reference_str_range(start: str, end: str, step: int = 1) -> t.Iterator[str]:
    """Return an iterator of strings from start to end, inclusive"""
    for i in range(ord(start), ord(end) + (1 if step > 0 else -1), step):
        yield chr(i)


def test_str_range_same_start_end(function_to_test: t.Callable):
    r = function_to_test("a", "a")
    assert iter(r) == r
    assert "".join(list(r)) == "a"


def test_str_range_simple(function_to_test: t.Callable):
    r = function_to_test("a", "c")
    assert "".join(list(r)) == "abc"


def test_str_range_simple_with_step(function_to_test: t.Callable):
    r = function_to_test("a", "c", 2)
    assert "".join(list(r)) == "ac"


def test_str_range_simple_with_negativestep(function_to_test: t.Callable):
    r = function_to_test("c", "a", -2)
    assert "".join(list(r)) == "ca"


def test_str_range_hebrew(function_to_test: t.Callable):
    r = function_to_test("א", "ז", 2)
    assert "".join(list(r)) == "אגהז"


#
# Exercise Read n lines
#


def reference_read_n_lines(filename: str, lines: int):
    with open(filename) as file:
        while True:
            first_line = file.readline()

            if not first_line:
                break

            yield first_line + "".join(file.readline() for _ in range(lines - 1))


def create_alphabet_file(tmp_path: pathlib.Path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "alphabet.txt"

    text = "\n".join(f"{one_letter * 20}" for one_letter in lowercase) + "\n"

    p.write_text(text)

    return p


@pytest.mark.parametrize("n,expected", [(1, 26), (2, 13), (3, 9), (4, 7)])
def test_read_n_lines(tmp_path, n, expected, function_to_test: t.Callable):
    p = create_alphabet_file(tmp_path)

    i = function_to_test(p, n)
    assert i == iter(i)
    assert len(list(i)) == expected
