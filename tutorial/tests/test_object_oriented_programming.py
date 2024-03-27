import pathlib

import pytest

#
# Exercise 1: Ice cream scoop
#


def reference_ice_cream_scoop(flavors: tuple[str]) -> str:
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
        (("chocolate", "vanilla", "persimmon")),
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

        def reset(self):
            self.program = self._backup[:]

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
