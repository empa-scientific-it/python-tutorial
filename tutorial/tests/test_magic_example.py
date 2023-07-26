import pytest

def my_num() -> int:
    return 1


def my_test(x: str) -> str:
    return x


def my_str() -> str:
    return "this is a string"


def my_print(text: str) -> None:
    print(my_test(text))


def my_calc(num: int, pow: int) -> int:
    return num ** pow


def reference_power(num: int, pow: int) -> int:
    """Compute num ^ pow"""
    if my_num():
        print('ok')
    my_print(my_str())
    return my_calc(num, pow)


input_args = [1, 2, 3, 4, 32]


@pytest.mark.parametrize("input_arg", input_args)
def test_power2(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_power(input_arg, 2)


@pytest.mark.parametrize("input_arg", input_args)
def test_power3(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_power(input_arg, 3)


@pytest.mark.parametrize("input_arg", input_args)
def test_power4(input_arg, function_to_test):
    """The test case(s)"""
    assert function_to_test(input_arg) == reference_power(input_arg, 4)
