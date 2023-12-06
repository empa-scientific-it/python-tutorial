import pathlib
import time
import typing as t
from operator import sub
from string import ascii_lowercase as lowercase
from string import ascii_uppercase as uppercase
from string import digits, punctuation

import pytest


#
# Exercise: Password checker factory
#
def reference_password_checker_factory(
    min_up: int, min_low: int, min_pun: int, min_dig: int
) -> t.Callable:
    """Password checker factory"""

    def password_checker(password: str) -> tuple[bool, dict]:
        """Password checker function"""

        # Counts the number of chars for each class in a password
        counts = [
            sum(1 for char in password if char in _class)
            for _class in (uppercase, lowercase, punctuation, digits)
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
    for value in details.values():
        assert value == 0


def test_password_checker_factory_no_min_some_pw(function_to_test: t.Callable):
    pc = function_to_test(0, 0, 0, 0)
    result, details = pc("ABCDefgh!@#$1234")

    assert result
    for value in details.values():
        assert value == 4


def test_password_checker_factory_simple_good(function_to_test: t.Callable):
    pc = function_to_test(1, 2, 3, 4)
    result, details = pc("Abc!@#1234")

    assert result
    for value in details.values():
        assert value == 0


def test_password_checker_factory_simple_bad(function_to_test: t.Callable):
    pc = function_to_test(1, 2, 3, 4)
    result, details = pc("b!#234")

    assert not result
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


class TooSoonError(Exception):
    """Error raised when a function is called too soon"""


def reference_once(func: t.Callable) -> t.Callable:
    """Decorator to run a function at most once"""
    allowed_time = 15
    timer = 0.0

    def wrapper(*args, **kwargs) -> t.Any:
        """Wrapper"""
        nonlocal timer

        if not timer:
            timer = time.perf_counter()
            return func(*args, **kwargs)

        if (stop := time.perf_counter()) - timer < allowed_time:
            raise TooSoonError(
                f"Wait another {allowed_time - (stop - timer):.2f} seconds"
            )

        timer = time.perf_counter()

        return func(*args, **kwargs)

    return wrapper


def test_once_simple(function_to_test: t.Callable) -> None:
    _hello = function_to_test(hello)
    assert _hello("world") == "Hello world!"


def test_once_twice(function_to_test: t.Callable, capsys) -> None:
    _hello = function_to_test(hello)

    with capsys.disabled():
        print("Waiting to run...")

    time.sleep(15)
    assert _hello("world") == "Hello world!"

    with pytest.raises(TooSoonError):
        _hello("world 2")


def test_once_waiting_14_sec(function_to_test: t.Callable, capsys) -> None:
    _hello = function_to_test(hello)

    with capsys.disabled():
        print("Waiting to run...")

    time.sleep(15)
    assert _hello("world") == "Hello world!"
    time.sleep(14)

    with pytest.raises(TooSoonError) as err:
        _hello("world 2")
        assert "Wait another 1." in str(err)


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

    text = "\n".join(f"{one_letter*20}" for one_letter in lowercase) + "\n"

    p.write_text(text)

    return p


@pytest.mark.parametrize("n,expected", [(1, 26), (2, 13), (3, 9), (4, 7)])
def test_read_n_lines(tmp_path, n, expected, function_to_test: t.Callable):
    p = create_alphabet_file(tmp_path)

    i = function_to_test(p, n)
    assert i == iter(i)
    assert len(list(i)) == expected
