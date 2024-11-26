import pathlib
from abc import ABC, abstractmethod
from datetime import datetime

import pytest
from numpy import average

#
# Exercise 1: Child Eye Color
#


def reference_child_eye_color(mother_eye_color: str, father_eye_color: str) -> str:
    class Mother:
        def __init__(self, eye_color: str):
            self.eye_color_mother = eye_color

    class Father:
        def __init__(self, eye_color: str):
            self.eye_color_father = eye_color

    class Child(Mother, Father):
        def __init__(self, eye_color_mother: str, eye_color_father: str):
            Mother.__init__(self, eye_color_mother)
            Father.__init__(self, eye_color_father)
            self.eye_color = self.set_eye_color()

        def set_eye_color(self):
            if self.eye_color_mother == self.eye_color_father:
                return self.eye_color_mother
            return "brown"

    child = Child(mother_eye_color, father_eye_color)
    return child.eye_color


@pytest.mark.parametrize(
    "mother_eye_color, father_eye_color",
    [
        ("blue", "blue"),
        ("brown", "brown"),
        ("blue", "brown"),
        ("brown", "blue"),
    ],
)
def test_child_eye_color(mother_eye_color, father_eye_color, function_to_test):
    assert function_to_test(
        mother_eye_color, father_eye_color
    ) == reference_child_eye_color(mother_eye_color, father_eye_color)


#
# Exercise 2: Store Inventory
#


def reference_store_inventory(computers: list[dict]) -> list[str]:
    class Computer:
        """A class representing a computer sold by the online store"""

        def __init__(self, name: str, price: int, quantity: int):
            self.name = name
            self.price = price
            self.quantity = quantity
            self.type = None

        def __str__(self):
            return f"Computer with name '{self.name}', price {self.price} CHF and quantity {self.quantity}."

    class PC(Computer):
        """A class representing a PC sold by the online store"""

        def __init__(self, name: str, price: int, quantity: int, expansion_slots: int):
            super().__init__(name, price, quantity)
            self.expansion_slots = expansion_slots
            self.type = "PC"

        def __str__(self):
            return (
                super().__str__()
                + f" This PC has {self.expansion_slots} expansion slots."
            )

    class Laptop(Computer):
        """A class representing a laptop sold by the online store"""

        def __init__(self, name: str, price: int, quantity: int, battery_life: int):
            super().__init__(name, price, quantity)
            self.battery_life = battery_life
            self.type = "Laptop"

        def __str__(self):
            return (
                super().__str__()
                + f" This laptop has a battery life of {self.battery_life} hours."
            )

    inventory = []
    for computer in computers:
        computer_type = PC if computer["type"] == "PC" else Laptop
        computer.pop("type")
        inventory.append(computer_type(**computer))

    result = []
    for item in inventory:
        result.append(str(item))

    return result


def test_store_inventory(function_to_test):
    computers = [
        {
            "type": "PC",
            "name": "pc_1",
            "price": 1500,
            "quantity": 1,
            "expansion_slots": 2,
        },
        {
            "type": "Laptop",
            "name": "laptop_1",
            "price": 1200,
            "quantity": 4,
            "battery_life": 6,
        },
    ]

    assert function_to_test(computers) == reference_store_inventory(computers)


#
# Exercise 3: Music Streaming Service
#


def reference_music_streaming_service(song_info: list[dict]):
    class Song:
        def __init__(self, title: str, artist: str, album_title: str):
            self.title = title
            self.artist = artist
            self.album_title = album_title

        def __str__(self):
            return (
                f"Song '{self.title}' by {self.artist} from album '{self.album_title}'."
            )

    class Playlist:
        def __init__(self, name: str):
            self.name = name
            self.songs: list[Song] = []

        def add_song(self, song: Song):
            self.songs.append(song)

        def display_songs(self):
            if not self.songs:
                return f"Playlist '{self.name}' is empty."
            else:
                return f"Songs in playlist '{self.name}':\n" + "\n".join(
                    str(song) for song in self.songs
                )

    class User:
        def __init__(self, username: str):
            self.username = username
            self.playlists: dict = {}

        def create_playlist(self, name: str):
            self.playlists[name] = Playlist(name)

        def add_song_to_playlist(self, playlist_name: str, song: Song):
            if playlist_name not in self.playlists:
                return f"Playlist '{playlist_name}' not found."
            self.playlists[playlist_name].add_song(song)

        def display_playlist(self, playlist_name: str):
            if playlist_name not in self.playlists:
                return f"Playlist '{playlist_name}' not found."
            return self.playlists[playlist_name].display_songs()

    user = User("Bob")
    user.create_playlist("Favorites from Queen")

    for info in song_info:
        user.add_song_to_playlist(
            "Favorites from Queen",
            Song(info["title"], info["artist"], info["album_title"]),
        )

    return user


def test_music_streaming_service(function_to_test):
    song_info = [
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "album_title": "A Night at the Opera",
        },
        {
            "title": "We Will Rock You",
            "artist": "Queen",
            "album_title": "News of the World",
        },
        {
            "title": "I Want to Break Free",
            "artist": "Queen",
            "album_title": "The Works",
        },
    ]

    solution_user = function_to_test(song_info)
    reference_user = reference_music_streaming_service(song_info)

    assert (
        vars(solution_user).keys() == vars(reference_user).keys()
    )  # check that the user instances have the same attributes
    assert len(vars(solution_user)["playlists"]) == len(
        vars(reference_user)["playlists"]
    )  # each user should have only 1 playlist

    solution_playlist = vars(list(vars(solution_user)["playlists"].values())[0])
    reference_playlist = vars(list(vars(reference_user)["playlists"].values())[0])

    assert (
        solution_playlist.keys() == reference_playlist.keys()
    )  # check that the playlist instances have the same attributes
    assert len(solution_playlist["songs"]) == len(
        reference_playlist["songs"]
    )  # both playlists should contain 3 songs

    solution_songs = []
    for song in solution_playlist["songs"]:
        solution_songs.append(vars(song))

    reference_songs = []
    for song in reference_playlist["songs"]:
        reference_songs.append(vars(song))

    assert (
        solution_songs == reference_songs
    )  # both playlists should have the same keys and values


#
# Exercise 4: Banking System
#


def reference_banking_system(
    tax_rate: float,
    interest_rate: float,
    gross_salary: int,
    savings_precentage: float,
    years_passed: int,
) -> float:
    class Account(ABC):
        def __init__(self, account_number):
            self.account_number = account_number
            self.balance = 0

        @abstractmethod
        def credit(self, amount):
            pass

        @abstractmethod
        def get_balance(self):
            pass

        def debit(self, amount):
            if self.balance >= amount:
                self.balance -= amount
            else:
                print("Insufficient funds.")

    class SalaryAccount(Account):
        def __init__(self, account_number, tax_rate):
            super().__init__(account_number)
            self.tax_rate = tax_rate

        def credit(self, amount):
            self.balance += amount - amount * self.tax_rate

        def get_balance(self):
            return self.balance

    class SavingsAccount(Account):
        def __init__(self, account_number, interest_rate):
            super().__init__(account_number)
            self.interest_rate = interest_rate
            self.creation_year = datetime.now().year

        def credit(self, amount):
            self.balance += amount

        def get_balance(self, years_passed):
            interest = self.balance * self.interest_rate * years_passed
            return self.balance + interest

    salary_account = SalaryAccount("SAL-001", tax_rate)
    savings_account = SavingsAccount("SAV-001", interest_rate)

    salary_account.credit(gross_salary)

    amount_to_transfer = salary_account.get_balance() * savings_precentage

    salary_account.debit(amount_to_transfer)
    savings_account.credit(amount_to_transfer)

    return savings_account.get_balance(years_passed)


@pytest.mark.parametrize(
    "tax_rate, interest_rate, gross_salary, savings_precentage, years_passed",
    [
        (0.20, 0.05, 10000, 0.3, 2),
        (0.18, 0.04, 9300, 0.15, 3),
        (0.13, 0.07, 8500, 0.18, 4),
    ],
)
def test_banking_system(
    tax_rate,
    interest_rate,
    gross_salary,
    savings_precentage,
    years_passed,
    function_to_test,
):
    assert function_to_test(
        tax_rate, interest_rate, gross_salary, savings_precentage, years_passed
    ) == reference_banking_system(
        tax_rate, interest_rate, gross_salary, savings_precentage, years_passed
    )


#
# Exercise 5: The N-body problem
#


def read_data(name: str, data_dir: str = "data") -> pathlib.Path:
    """Read input data"""
    return (pathlib.Path(__file__).parent / f"{data_dir}/{name}").resolve()


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
        return list(map(sum, zip(*[moon.velocities for moon in self.moons])))

    def __repr__(self) -> str:
        return "\n".join(repr(moon) for moon in self.moons)


@pytest.mark.parametrize("universe_start", universes)
def test_n_body(universe_start: str, function_to_test) -> None:
    universe = Universe(universe_start)
    energy = [universe.evolve().energy for _ in range(1000)]
    assert function_to_test(universe_start) == pytest.approx(average(energy))
