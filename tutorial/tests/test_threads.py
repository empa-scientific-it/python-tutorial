import pytest


def reference_exercise1() -> int:
    return 42


def test_exercise1():
    assert threads.exercise1() == 42
