import pathlib
import sys
from typing import List

import pytest


#
# Exercise 1: Ice cream scoop
#

class Scoop:
    """A class representing a single scoop of ice cream"""

    def __init__(self, flavor: str):
        self.flavor = flavor

    def __str__(self):
        return f"Ice cream scoop with flavor '{self.flavor}'"


def test_ice_cream_scoop(function_to_test) -> None:
    flavors = ("chocolate", "vanilla", "persimmon")
    assert function_to_test(flavors) == [str(Scoop(flavor)) for flavor in flavors]


#
# Exercise 2: Ice cream bowl
#


class Bowl:
    """A class representing a bowl of ice cream scoops"""

    def __init__(self):
        self.scoops = []

    def add_scoops(self, *new_scoops: List["Scoop"]) -> None:
        for one_scoop in new_scoops:
            self.scoops.append(one_scoop)

    def __str__(self):
        return f"Ice cream bowl with {', '.join(s.flavor for s in self.scoops)}"


def test_ice_cream_bowl(function_to_test) -> None:
    flavors = ("chocolate", "vanilla", "stracciatella")
    bowl = Bowl()
    scoops = [Scoop(flavor) for flavor in flavors]
    bowl.add_scoops(*scoops)
    assert function_to_test(flavors) == str(bowl)


#
# Exercise 3: Intcode computer
#

def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    current_module = sys.modules[__name__]
    return (pathlib.Path(current_module.__file__).parent / f"{data_dir}/{name}").resolve()


class Computer:
    """An Intcode computer class"""

    def __init__(self, program: str):
        self.program = [int(c.strip()) for c in program.split(',')]
        self._backup = self.program[:]

    def reset(self):
        self.program = self._backup[:]

    def run(self, pos=0):
        while True:
            if self.program[pos] == 99:
                break
            op1, op2 = self.program[self.program[pos + 1]], self.program[self.program[pos + 2]]
            func = self.program[pos]
            self.program[self.program[pos + 3]] = op1 + op2 if func == 1 else op1 * op2
            pos += 4


intcodes = [
    "1,0,0,0,99",
    "2,3,0,3,99",
    "1,1,1,4,99,5,6,0,99"
]
intcodes += [read_data(f"intcode_{i}.txt").read_text() for i in (1, 2)]


@pytest.mark.parametrize("intcode", intcodes)
def test_intcode_computer(intcode: str, function_to_test) -> None:
    computer = Computer(intcode)
    computer.run()
    assert function_to_test(intcode) == computer.program[0]
