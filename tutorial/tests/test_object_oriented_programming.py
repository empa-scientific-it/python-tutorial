import pathlib
import sys

import pytest
from numpy import average

FLAVORS = [
    ("chocolate",),
    ("chocolate", "vanilla", "persimmon"),
    ("chocolate", "vanilla", "stracciatella"),
    ("chocolate", "vanilla", "stracciatella", "strawberry"),
    ("chocolate", "vanilla", "stracciatella", "strawberry", "pistachio"),
]

#
# Exercise 1: Ice cream scoop
#


class Scoop:
    """A class representing a single scoop of ice cream"""

    def __init__(self, flavor: str):
        self.flavor = flavor

    def __str__(self):
        return f"Ice cream scoop with flavor '{self.flavor}'"


def reference_ice_cream_scoop(flavors: tuple[str]) -> list[Scoop, str]:
    return [(Scoop(flavor), str(Scoop(flavor))) for flavor in flavors]


@pytest.mark.parametrize("flavors", FLAVORS)
def test_ice_cream_scoop(flavors, function_to_test) -> None:
    test_solution = [string for _, string in function_to_test(flavors)]
    reference_solution = [string for _, string in reference_ice_cream_scoop(flavors)]
    assert test_solution == reference_solution


#
# Exercise 2: Ice cream bowl
#


class Bowl:
    """A class representing a bowl of ice cream scoops"""

    def __init__(self):
        self.scoops = []

    def add_scoops(self, *new_scoops: list["Scoop"]) -> None:
        for one_scoop in new_scoops:
            self.scoops.append(one_scoop)

    def __str__(self):
        return f"Ice cream bowl with {', '.join(s.flavor for s in self.scoops)} scoops"


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
    return (
        pathlib.Path(current_module.__file__).parent / f"{data_dir}/{name}"
    ).resolve()


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
            self.program[self.program[pos + 3]] = op1 + op2 if func == 1 else op1 * op2
            pos += 4


intcodes = ["1,0,0,0,99", "2,3,0,3,99", "1,1,1,4,99,5,6,0,99"]
intcodes += [read_data(f"intcode_{i}.txt").read_text() for i in (1, 2)]


@pytest.mark.parametrize("intcode", intcodes)
def test_intcode_computer(intcode: str, function_to_test) -> None:
    computer = Computer(intcode)
    computer.run()
    assert function_to_test(intcode) == computer.program[0]


#
# Exercise 4: The N-body problem
#


universes = [read_data(f"universe_{i}.txt").read_text() for i in (1, 2)]


class Moon:
    """A class for a moon"""

    def __init__(self, scan: str) -> None:
        name, pos = scan.split(": ")
        self.name = name
        self.positions = [int(x[2:]) for x in pos.split(", ")]
        self.velocities = [0 for _ in range(len(self.positions))]

    def update_velocities(self, moon: "Moon") -> None:
        """Update the velocity of the moon"""
        for n, position in enumerate(self.positions):
            if position > moon.positions[n]:
                delta = -1
            elif position < moon.positions[n]:
                delta = 1
            else:
                delta = 0

            if delta:
                self.velocities[n] += delta
                moon.velocities[n] -= delta

    def update_positions(self) -> None:
        """Update the position of the moon"""
        for n in range(len(self.positions)):
            self.positions[n] += self.velocities[n]

    @property
    def abs_velocity(self) -> int:
        """Return the absolute velocity of the moon"""
        return sum(abs(v) for v in self.velocities)

    @property
    def abs_position(self) -> int:
        """Return the absolute position of the moon"""
        return sum(abs(p) for p in self.positions)

    @property
    def energy(self) -> int:
        """Return the energy of the moon"""
        return self.abs_position * self.abs_velocity

    def __repr__(self) -> str:
        return "{}: x={}, y={}, z={}, vx={}, vy={}, vz={}".format(
            self.name, *self.positions, *self.velocities
        )


@pytest.mark.parametrize("moons", universes)
def test_moons(moons: str, function_to_test):
    universe = [Moon(moon) for moon in moons.splitlines()]
    assert function_to_test(moons) == [repr(moon) for moon in universe]


class Universe:
    """A class for a universe"""

    def __init__(self, universe_start: str) -> None:
        self.moons = [Moon(moon) for moon in universe_start.splitlines()]

    def evolve(self) -> "Universe":
        """Evolve the universe"""
        for n, moon_i in enumerate(self.moons[:-1]):
            for moon_j in self.moons[n + 1 :]:
                moon_i.update_velocities(moon_j)

        for moon in self.moons:
            moon.update_positions()

        return self

    @property
    def energy(self) -> int:
        """Return the total energy of the universe"""
        return sum(moon.energy for moon in self.moons)

    @property
    def momentum(self) -> list:
        """Return the momentum of the universe"""
        return list(
            map(sum, zip(*[moon.velocities for moon in self.moons], strict=False))
        )

    def __repr__(self) -> str:
        return "\n".join(repr(moon) for moon in self.moons)


@pytest.mark.parametrize("universe_start", universes)
def test_n_body(universe_start: str, function_to_test) -> None:
    universe = Universe(universe_start)
    energy = [universe.evolve().energy for _ in range(1000)]
    assert function_to_test(universe_start) == pytest.approx(average(energy))
