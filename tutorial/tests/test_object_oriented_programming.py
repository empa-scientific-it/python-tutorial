import pathlib

import pytest

#
# Example 1: Person
#


def reference_oop_person(first_name: str, last_name: str):
    class Person:
        """A class representing a person with first name and last name"""

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

    return Person(first_name, last_name)


def validate_oop_person(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple)
    ), "Solution must return a class instance, not a primitive type."
    assert (
        type(solution_result).__module__ != "builtins"
    ), "Solution must return an instance of a custom class, not a built-in type."
    assert (
        type(solution_result).__name__ == "Person"
    ), "The class should be named 'Person'."
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError as e:
        raise AssertionError from e
    assert len(attrs) == 2, "The class should have 2 attributes."
    assert (
        "first_name" in attrs and "last_name" in attrs
    ), "The class attributes should be 'first_name' and 'last_name'."


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
    assert (
        solution_result.full_name() == reference_result.full_name()
    ), "The full_name() result does not match the template 'My name is {first_name} {last_name}'."

    solution_result.first_name = "Jane"
    solution_result.last_name = "Smith"
    reference_result.first_name = "Jane"
    reference_result.last_name = "Smith"
    assert (
        solution_result.full_name() == reference_result.full_name()
    ), "The full_name() method should be using the class attributes."


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
            return (
                f"{self.first_name} {self.last_name} is an instance of the class Person"
            )

    return Person(first_name, last_name)


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
    assert str(solution_result) == str(
        reference_result
    ), "The __str__() result does not match the template 'My name is {first_name} {last_name}'."
    assert (
        solution_result.__repr__() == reference_result.__repr__()
    ), "The __repr__() result does not match the template '{first_name} {last_name} is an instance of the class Person'."

    solution_result.first_name = "Jane"
    solution_result.last_name = "Smith"
    reference_result.first_name = "Jane"
    reference_result.last_name = "Smith"
    assert str(solution_result) == str(
        reference_result
    ), "The __str__() method should be using the class attributes."
    assert (
        solution_result.__repr__() == reference_result.__repr__()
    ), "The __repr__() method should be using the class attributes."


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
    params = list(vars(solution_result))
    assert (
        type(solution_result).__name__ == "Person"
    ), "The class should be named 'Person'."
    assert len(params) == 3, "The class should have 3 attributes."
    assert (
        "first_name" in params and "last_name" in params and "age" in params
    ), "The class attributes should be 'first_name', 'last_name' and 'age'."


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
