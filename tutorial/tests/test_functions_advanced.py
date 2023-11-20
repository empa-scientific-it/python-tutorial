import time
import typing as t

import pytest


def hello(name):
    return f"Hello {name}!"


class TooSoonError(Exception):
    """Error raised when a function is called too soon"""


def reference_once(func: t.Callable) -> t.Callable:
    """Decorator to run a function at most once"""
    allowed_time = 15
    timer = 0.0

    def wrapper(*args, **kwargs):
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
    at_hello = function_to_test(hello)
    assert at_hello("world") == "Hello world!"


def test_once_twice(function_to_test: t.Callable, capsys) -> None:
    at_hello = function_to_test(hello)

    with capsys.disabled():
        print("Waiting to run...")

    time.sleep(15)
    assert at_hello("world") == "Hello world!"

    with pytest.raises(TooSoonError):
        at_hello("world 2")


def test_once_waiting_14_sec(function_to_test: t.Callable, capsys) -> None:
    at_hello = function_to_test(hello)

    with capsys.disabled():
        print("Waiting to run...")

    time.sleep(15)
    assert at_hello("world") == "Hello world!"
    time.sleep(14)

    with pytest.raises(TooSoonError) as err:
        at_hello("world 2")
        assert "Wait another 1." in str(err)
