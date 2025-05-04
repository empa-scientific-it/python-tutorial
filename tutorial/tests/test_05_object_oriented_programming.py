import pathlib
import re

import pytest


class SubAssertionError(AssertionError):
    def __init__(self):
        super().__init__("Solution must be a proper class instance with attributes.")


#
# Example 1: Person
#

# NOTE:
# When testing the classes returned by the solutions function in the Examples 1-4
# we often need to check if a class method is implemented and it's using the right attributes.
# One way to check both is to check if the class's method has the __closure__ attribute.
# Why?
#   1. If __method__ is not implemented, Python will fetch object.__method__ instead, which obviously is not a closure
#       `hasattr(solution_result.__method__, "__closure__")` will return False.
#   2. If __method__ is implemented, but it's not using the class attributes, it will be a closure
#       `solution_result.__method__.__closure__ is None` will return False.
# Reference: https://github.com/empa-scientific-it/python-tutorial/pull/249#discussion_r1836867387


def reference_oop_person(first_name: str, last_name: str):
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

    return Person(first_name, last_name)


def validate_oop_person(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple, set)
    ), "Solution must return a class instance, not a datatype."
    assert type(solution_result).__module__ != "builtins", (
        "Solution must return an instance of a custom class, not a built-in type."
    )
    assert type(solution_result).__name__ == "Person", (
        "The class should be named 'Person'."
    )
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 2, "The class should have 2 attributes."
    assert "first_name" in attrs and "last_name" in attrs, (
        "The class attributes should be 'first_name' and 'last_name'."
    )


@pytest.mark.parametrize(
    "first_name, last_name",
    [
        ("John", "Doe"),
    ],
)
def test_oop_person(first_name, last_name, function_to_test):
    solution_result = function_to_test(first_name, last_name)
    reference_result = reference_oop_person(first_name, last_name)

    validate_oop_person(solution_result)
    assert (
        solution_result.first_name == reference_result.first_name
        and solution_result.last_name == reference_result.last_name
    )


#
# Example 2: Person's full name
#


def reference_oop_fullname(first_name: str, last_name: str):
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

        def full_name(self) -> str:
            return f"My name is {self.first_name} {self.last_name}"

    return Person(first_name, last_name)


def validate_oop_fullname(solution_result):
    methods = [
        attr
        for attr in dir(solution_result)
        if callable(getattr(solution_result, attr)) and not attr.startswith("__")
    ]
    assert len(methods) == 1, "The class should have 1 method."
    assert "full_name" in methods, "The class method should be called 'full_name'."
    assert solution_result.full_name.__closure__ is None, (
        "The full_name() method should be using the class attributes."
    )


@pytest.mark.parametrize(
    "first_name, last_name",
    [
        ("John", "Doe"),
    ],
)
def test_oop_fullname(first_name, last_name, function_to_test):
    solution_result = function_to_test(first_name, last_name)
    reference_result = reference_oop_fullname(first_name, last_name)

    validate_oop_person(solution_result)
    validate_oop_fullname(solution_result)
    assert solution_result.full_name() == reference_result.full_name(), (
        "The full_name() result does not match the template 'My name is {first_name} {last_name}'."
    )


#
# Example 3: Person class with __str__ and __repr__
#


def reference_oop_str_and_repr(first_name: str, last_name: str):
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

        def __str__(self):
            return f"My name is {self.first_name} {self.last_name}"

        def __repr__(self):
            return f"Person({self.first_name}, {self.last_name})"

    return Person(first_name, last_name)


def validate_oop_str_method(solution_result):
    assert hasattr(solution_result.__str__, "__closure__"), (
        "Make sure that the class is properly implementing the __str__() method."
    )
    assert solution_result.__str__.__closure__ is None, (
        "The __str__() method should be using the class attributes."
    )


def validate_oop_repr_method(solution_result):
    assert hasattr(solution_result.__repr__, "__closure__"), (
        "Make sure that the class is properly implementing the __repr__() method."
    )
    assert solution_result.__repr__.__closure__ is None, (
        "The __repr__() method should be using the class attributes."
    )


@pytest.mark.parametrize(
    "first_name, last_name",
    [
        ("John", "Doe"),
    ],
)
def test_oop_str_and_repr(first_name, last_name, function_to_test):
    solution_result = function_to_test(first_name, last_name)
    reference_result = reference_oop_str_and_repr(first_name, last_name)

    validate_oop_person(solution_result)
    validate_oop_str_method(solution_result)
    validate_oop_repr_method(solution_result)

    assert str(solution_result) == str(reference_result), (
        "The __str__() result does not match the template 'My name is {first_name} {last_name}'."
    )
    assert solution_result.__repr__() == reference_result.__repr__(), (
        "The __repr__() result does not match the template 'Person({first_name}, {last_name})'."
    )


#
# Example 4: Person class with equality comparison
#


def reference_oop_compare_persons(first_name: str, last_name: str, age: int):
    class Person:
        """A class representing a person with first name, last name and age"""

        def __init__(self, first_name: str, last_name: str, age: int):
            self.first_name = first_name
            self.last_name = last_name
            self.age = age

        def __eq__(self, other):
            if isinstance(other, Person):
                return (self.first_name, self.last_name, self.age) == (
                    other.first_name,
                    other.last_name,
                    other.age,
                )
            else:
                return False

    return Person(first_name, last_name, age)


def validate_oop_compare_persons(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple, set)
    ), "Solution must return a class instance, not a datatype."
    assert type(solution_result).__module__ != "builtins", (
        "Solution must return an instance of a custom class, not a built-in type."
    )
    assert type(solution_result).__name__ == "Person", (
        "The class should be named 'Person'."
    )
    assert hasattr(solution_result.__eq__, "__closure__"), (
        "Make sure that the class is properly implementing the __eq__() method."
    )
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 3, "The class should have 3 attributes."
    assert "first_name" in attrs and "last_name" in attrs and "age" in attrs, (
        "The class attributes should be 'first_name', 'last_name' and 'age'."
    )


@pytest.mark.parametrize(
    "first_name_a, last_name_a, age_a, first_name_b, last_name_b, age_b",
    [
        ("Jane", "Doe", 30, "John", "Doe", 25),
        ("John", "Smith", 25, "John", "Doe", 25),
        ("John", "Doe", 20, "John", "Doe", 25),
        ("John", "Doe", 25, "John", "Doe", 25),
    ],
)
def test_oop_compare_persons(
    first_name_a, last_name_a, age_a, first_name_b, last_name_b, age_b, function_to_test
):
    solution_result_a = function_to_test(first_name_a, last_name_a, age_a)
    reference_result_a = reference_oop_compare_persons(first_name_a, last_name_a, age_a)

    solution_result_b = function_to_test(first_name_b, last_name_b, age_b)
    reference_result_b = reference_oop_compare_persons(first_name_b, last_name_b, age_b)

    validate_oop_compare_persons(solution_result_a)
    assert (solution_result_a == solution_result_b) == (
        reference_result_a == reference_result_b
    ), "Comparison failed."


#
# Exercise 1: Ice cream scoop
#


def reference_ice_cream_scoop(flavors: tuple[str]) -> list:
    class Scoop:
        """A class representing a single scoop of ice cream"""

        def __init__(self, flavor: str):
            self.flavor = flavor

        def __str__(self):
            return f"Ice cream scoop with flavor '{self.flavor}'"

    return [Scoop(flavor) for flavor in flavors]


def validate_ice_cream_scoop(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple, set)
    ), "The returned list must contain class instances, not datatypes."
    assert type(solution_result).__module__ != "builtins", (
        "The returned list must contain instances of a custom class, not a built-in type."
    )
    assert type(solution_result).__name__ == "Scoop", (
        "The class should be named 'Scoop'."
    )
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 1, "The class should have 1 attribute."
    assert "flavor" in attrs, "The class attribute should be 'flavor'."
    assert hasattr(solution_result.__str__, "__closure__"), (
        "Make sure that the class is properly implementing the __str__() method."
    )
    assert solution_result.__str__.__closure__ is None, (
        "The __str__() method should be using the class attributes."
    )
    # check the __str__ result
    pattern = r"^Ice cream scoop with flavor '(.+)'$"
    assert re.match(pattern, str(solution_result)), (
        "The __str__() result does not match the template: Ice cream scoop with flavor '{flavor}'"
    )


@pytest.mark.parametrize(
    "flavors",
    [
        ("chocolate", "vanilla", "persimmon"),
    ],
)
def test_ice_cream_scoop(flavors, function_to_test) -> None:
    solution_result = function_to_test(flavors)
    reference_result = reference_ice_cream_scoop(flavors)

    assert isinstance(solution_result, list), "Solution must return a list."
    assert len(solution_result) == len(flavors), (
        "The returned list must contain as many scoops as the provided flavors."
    )

    for res in solution_result:
        validate_ice_cream_scoop(res)

    solution_str_repr = [str(scoop) for scoop in solution_result]
    reference_str_repr = [str(scoop) for scoop in reference_result]
    assert solution_str_repr == reference_str_repr


#
# Exercise 2: Ice cream bowl
#


def reference_ice_cream_bowl(flavors: tuple[str]):
    class Scoop:
        """A class representing a single scoop of ice cream"""

        def __init__(self, flavor: str):
            self.flavor = flavor

        def __str__(self):
            return f"Ice cream scoop with flavor '{self.flavor}'"

    class Bowl:
        """A class representing a bowl of ice cream scoops"""

        def __init__(self):
            self.scoops = []

        def add_scoops(self, *new_scoops: "Scoop") -> None:
            for one_scoop in new_scoops:
                self.scoops.append(one_scoop)

        def __str__(self):
            return (
                f"Ice cream bowl with {', '.join(s.flavor for s in self.scoops)} scoops"
            )

    bowl = Bowl()
    scoops = [Scoop(flavor) for flavor in flavors]
    bowl.add_scoops(*scoops)
    return bowl


def validate_ice_cream_bowl(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple, set)
    ), "Solution must return a class instance, not a datatype."
    assert type(solution_result).__module__ != "builtins", (
        "Solution must return an instance of a custom class, not a built-in type."
    )
    assert type(solution_result).__name__ == "Bowl", "The class should be named 'Bowl'."
    # Check the class methods
    assert hasattr(solution_result.__str__, "__closure__"), (
        "Make sure that the Bowl class is properly implementing the __str__() method."
    )
    assert solution_result.__str__.__closure__ is None, (
        "The __str__() method should be using the class attributes."
    )
    methods = [
        attr
        for attr in dir(solution_result)
        if callable(getattr(solution_result, attr)) and not attr.startswith("__")
    ]
    assert len(methods) == 1, "The class should have 1 custom method."
    assert "add_scoops" in methods, "The class method should be called 'add_scoops'."
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 1, "The class should have 1 attribute."
    assert "scoops" in attrs, "The class attribute should be 'scoops'."
    assert isinstance(solution_result.scoops, (list, set, tuple)), (
        "The class attribute 'scoops' should be a datatype that acts as a container."
    )
    for scoop in solution_result.scoops:
        assert not isinstance(scoop, (str, int, float, bool, list, dict, tuple, set)), (
            "The 'scoops' container must contain class instances, not datatypes."
        )
        assert type(scoop).__module__ != "builtins", (
            "The 'scoops' container must contain instances of a custom class, not a built-in type."
        )
        assert type(scoop).__name__ == "Scoop", (
            "The 'scoops' container must contain instances of 'Scoop'."
        )
    # check the __str__ result
    pattern = r"^Ice cream bowl with ([a-zA-Z\s]+)(?:, ([a-zA-Z\s]+))* scoops$"
    assert re.match(pattern, str(solution_result)), (
        "The __str__() result does not match the template: Ice cream bowl with ... scoops"
    )


@pytest.mark.parametrize(
    "flavors",
    [
        ("chocolate", "vanilla", "stracciatella"),
    ],
)
def test_ice_cream_bowl(flavors, function_to_test) -> None:
    solution_result = function_to_test(flavors)
    reference_result = reference_ice_cream_bowl(flavors)

    validate_ice_cream_bowl(solution_result)
    assert str(solution_result) == str(reference_result)


#
# Exercise 3: Ice cream shop
#


def reference_ice_cream_shop(flavors: list[str]):
    class Shop:
        """A class representing an ice cream shop"""

        def __init__(self, flavors):
            self.flavors = flavors

        def __str__(self):
            return (
                f"Ice cream shop selling flavors: {', '.join(f for f in self.flavors)}"
            )

        def __eq__(self, other):
            if isinstance(other, Shop):
                return len(self.flavors) == len(other.flavors)
            return False

        def __lt__(self, other):
            if isinstance(other, Shop):
                return len(self.flavors) < len(other.flavors)
            return False

        def __le__(self, other):
            if isinstance(other, Shop):
                return self < other or self == other
            return False

    return Shop(flavors)


def validate_ice_cream_shop(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple, set)
    ), "Solution must return a class instance, not a datatype."
    assert type(solution_result).__module__ != "builtins", (
        "Solution must return an instance of a custom class, not a built-in type."
    )
    assert type(solution_result).__name__ == "Shop", "The class should be named 'Shop'."
    # Check the class methods
    assert hasattr(solution_result.__eq__, "__closure__"), (
        "Make sure that the class is properly implementing the __eq__() method."
    )
    assert hasattr(solution_result.__lt__, "__closure__"), (
        "Make sure that the class is properly implementing the __lt__() method."
    )
    assert hasattr(solution_result.__le__, "__closure__"), (
        "Make sure that the class is properly implementing the __le__() method."
    )
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 1, "The class should have 1 attribute."
    assert "flavors" in attrs, "The class attribute should be 'flavors'."
    assert isinstance(solution_result.flavors, (list, set, tuple)), (
        "The class attribute 'flavors' should be a datatype that acts as a container."
    )


@pytest.mark.parametrize(
    "flavors_a, flavors_b",
    [
        (["chocolate", "vanilla", "stracciatella"], ["caramel", "strawberry", "mango"]),
        (["vanilla", "stracciatella"], ["chocolate", "vanilla", "mango"]),
        (["vanilla", "mango"], ["chocolate"]),
    ],
)
def test_ice_cream_shop(flavors_a, flavors_b, function_to_test) -> None:
    solution_result_a = function_to_test(flavors_a)
    reference_result_a = reference_ice_cream_shop(flavors_a)

    solution_result_b = function_to_test(flavors_b)
    reference_result_b = reference_ice_cream_shop(flavors_b)

    validate_ice_cream_shop(solution_result_a)
    assert (solution_result_a <= solution_result_b) == (
        reference_result_a <= reference_result_b
    ), "Comparison failed."


#
# Exercise 4: Intcode computer
#


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    return (pathlib.Path(__file__).parent / f"{data_dir}/{name}").resolve()


def prepare_params() -> list[str]:
    """Prepare input values for a parametrized test"""
    intcodes = ["1,0,0,0,99", "2,3,0,3,99", "1,1,1,4,99,5,6,0,99"]
    intcodes += [read_data(f"intcode_{i}.txt").read_text() for i in (1, 2)]
    return intcodes


def reference_intcode_computer(intcode: str) -> int:
    class Computer:
        """An Intcode computer class"""

        def __init__(self, program: str):
            self.program = [int(code.strip()) for code in program.split(",")]

        def run(self, pos=0):
            while True:
                if self.program[pos] == 99:
                    break
                op1, op2 = (
                    self.program[self.program[pos + 1]],
                    self.program[self.program[pos + 2]],
                )
                func = self.program[pos]
                self.program[self.program[pos + 3]] = (
                    op1 + op2 if func == 1 else op1 * op2
                )
                pos += 4

    computer = Computer(intcode)
    computer.run()
    return computer.program[0]


@pytest.mark.parametrize(
    "intcode",
    prepare_params(),
)
def test_intcode_computer(intcode: str, function_to_test) -> None:
    solution_result = function_to_test(intcode)
    reference_result = reference_intcode_computer(intcode)

    assert solution_result == reference_result
