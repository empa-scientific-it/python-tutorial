import pathlib
import re

import pytest

#
# Example 1: Person
#


def reference_oop_person():
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

    return Person("John", "Doe")


def test_oop_person(function_to_test):
    solution_result = function_to_test()
    reference_result = reference_oop_person()

    assert (
        type(solution_result).__name__ == type(reference_result).__name__
    )  # check that the class is named 'Person'
    assert list(vars(solution_result)) == list(
        vars(reference_result)
    )  # check that the instances have the same attributes


#
# Example 2: Person's full name
#


def reference_oop_fullname():
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

        def full_name(self) -> str:
            return f"My name is {self.first_name} {self.last_name}"

    return Person("John", "Doe")


def verify_method_fullname(p) -> list[str]:
    return [
        attr
        for attr in dir(p)
        if callable(getattr(p, attr)) and not attr.startswith("__")
    ]


def verify_result_fullname(res: str) -> bool:
    # Define the pattern to match the template "My name is {first_name} {last_name}"
    pattern = r"^(My name is) \w+ \w+$"
    # Check if the sentence matches the template
    return re.match(pattern, res)


def test_oop_fullname(function_to_test):
    solution_result = function_to_test()
    reference_result = reference_oop_fullname()

    assert (
        type(solution_result).__name__ == type(reference_result).__name__
    )  # check that the class is named 'Person'
    assert list(vars(solution_result)) == list(
        vars(reference_result)
    )  # check that the instances have the same attributes
    assert verify_method_fullname(solution_result) == verify_method_fullname(
        reference_result
    )  # check that the instances have the same methods
    assert verify_result_fullname(
        solution_result.full_name()
    ), "The result does not match the template 'My name is {first_name} {last_name}'."


#
# Example 3: Person class with __str__ and __repr__
#


def reference_oop_str_and_repr():
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

        def __str__(self):
            return f"My name is {self.first_name} {self.last_name}"

        def __repr__(self):
            return (
                f"{self.first_name} {self.last_name} is an instance of the class Person"
            )

    return Person("John", "Doe")


def verify_result_repr(res: str) -> bool:
    # Define the pattern to match the template "{first_name} {last_name} is an instance of the class Person"
    pattern = r"^[A-Z][a-z]+ [A-Z][a-z]+ is an instance of the class Person$"
    # Check if the sentence matches the template
    return re.match(pattern, res)


def test_oop_str_and_repr(function_to_test):
    solution_result = function_to_test()
    reference_result = reference_oop_str_and_repr()

    assert (
        type(solution_result).__name__ == type(reference_result).__name__
    )  # check that the class is named 'Person'
    assert list(vars(solution_result)) == list(
        vars(reference_result)
    )  # check that the instances have the same attributes
    assert verify_result_fullname(
        str(solution_result)
    ), "The __str__ result does not match the template 'My name is {first_name} {last_name}'."
    assert verify_result_repr(
        solution_result.__repr__()
    ), "The __repr__ result does not match the template '{first_name} {last_name} is an instance of the class Person'."


#
# Example 4: Person class with equality comparison
#


def reference_oop_compare_persons(
    first_name: str = "John", last_name: str = "Doe", age: int = 25
):
    class Person:
        """A class representing a person with first name, last name and age"""

        def __init__(self, first_name: str, last_name: str, age: int):
            self.first_name = first_name
            self.last_name = last_name
            self.age = age

        def __eq__(self, other):
            return (self.first_name, self.last_name, self.age) == (
                other.first_name,
                other.last_name,
                other.age,
            )

    return Person(first_name, last_name, age)


@pytest.mark.parametrize(
    "first_name, last_name, age, result",
    [
        ("Jane", "Doe", 30, False),
        ("John", "Smith", 25, False),
        ("John", "Doe", 20, False),
        ("John", "Doe", 25, True),
    ],
)
def test_oop_compare_persons(first_name, last_name, age, result, function_to_test):
    solution_result = function_to_test()
    reference_result = reference_oop_compare_persons(first_name, last_name, age)

    assert (solution_result == reference_result) == result


#
# Exercise 1: Ice cream scoop
#


def reference_ice_cream_scoop(flavors: tuple[str]) -> list[str]:
    class Scoop:
        """A class representing a single scoop of ice cream"""

        def __init__(self, flavor: str):
            self.flavor = flavor

        def __str__(self):
            return f"Ice cream scoop with flavor '{self.flavor}'"

    return [str(Scoop(flavor)) for flavor in flavors]


@pytest.mark.parametrize(
    "flavors",
    [
        ("chocolate", "vanilla", "persimmon"),
    ],
)
def test_ice_cream_scoop(flavors, function_to_test) -> None:
    assert function_to_test(flavors) == reference_ice_cream_scoop(flavors)


#
# Exercise 2: Ice cream bowl
#


def reference_ice_cream_bowl(flavors: tuple[str]) -> str:
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
    return str(bowl)


@pytest.mark.parametrize(
    "flavors",
    [
        ("chocolate", "vanilla", "stracciatella"),
    ],
)
def test_ice_cream_bowl(flavors, function_to_test) -> None:
    assert function_to_test(flavors) == reference_ice_cream_bowl(flavors)


#
# Exercise 3: Ice cream shop
#


def reference_ice_cream_shop(flavors_1: list[str], flavors_2: list[str]) -> bool:
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

    shop_1 = Shop(flavors_1)
    shop_2 = Shop(flavors_2)
    return shop_1 <= shop_2


@pytest.mark.parametrize(
    "flavors_1, flavors_2",
    [
        (["chocolate", "vanilla", "stracciatella"], ["caramel", "strawberry", "mango"]),
        (["vanilla", "stracciatella"], ["chocolate", "vanilla", "mango"]),
        (["vanilla", "mango"], ["chocolate"]),
    ],
)
def test_ice_cream_shop(flavors_1, flavors_2, function_to_test) -> None:
    assert function_to_test(flavors_1, flavors_2) == reference_ice_cream_shop(
        flavors_1, flavors_2
    )


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
            self.program = [int(c.strip()) for c in program.split(",")]
            self._backup = self.program[:]

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
    assert function_to_test(intcode) == reference_intcode_computer(intcode)
