import asyncio

import pytest


def my_num() -> int:
    return 1


def my_test2(x: str) -> None:
    print(x)


def last_test() -> str:
    return "this has been a success"


def my_test(x: str) -> str:
    my_test2(last_test())
    return x


def my_str() -> str:
    return "this is a string"


def my_print(text: str) -> None:
    print(my_test(text))


def my_calc(num: int, power: int) -> int:
    return num**power


def reference_power2(num: int) -> int:
    """Compute num ^ 2"""
    if my_num():
        print("ok")
    my_print(my_str())
    return my_calc(num, 2)


def reference_power3(num: int) -> int:
    """Compute num ^ 3"""
    return num**3


def reference_power4(num: int) -> int:
    """Compute num ^ 4"""
    return num**4


def test_power2_raise(function_to_test):
    """The test case(s)"""
    with pytest.raises(TypeError):
        function_to_test("a")


input_args = [1, 2, 3, 4, 32]


@pytest.mark.parametrize("input_arg", input_args)
def test_power2(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_power2(input_arg)


@pytest.mark.parametrize("input_arg", input_args)
def test_power3(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_power3(input_arg)


@pytest.mark.parametrize("input_arg", input_args)
def test_power4(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_power4(input_arg)


async def reference_async() -> int:
    await asyncio.sleep(1)
    return 1


def test_async(function_to_test):
    async def async_test():
        return 1

    result = asyncio.run(async_test())
    user_result = asyncio.run(function_to_test())
    assert result == user_result


def reference_debug() -> int:
    print("I print here")
    return 1


def test_debug(function_to_test):
    print("I print here")
    assert function_to_test() == 1
