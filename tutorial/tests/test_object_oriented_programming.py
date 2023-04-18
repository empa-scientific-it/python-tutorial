from typing import List

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
