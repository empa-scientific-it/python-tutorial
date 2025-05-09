import pathlib
from abc import ABC, abstractmethod

import pytest
from numpy import average


class SubAssertionError(AssertionError):
    def __init__(self):
        super().__init__("Solution must be a proper class instance with attributes.")


#
# Exercise 1: Child Eye Color
#


def reference_child_eye_color(mother_eye_color: str, father_eye_color: str):
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

    return Child(mother_eye_color, father_eye_color)


def validate_child_eye_color(solution_result):
    assert not isinstance(
        solution_result, (str, int, float, bool, list, dict, tuple, set)
    ), "Solution must return a class instance, not a datatype."
    assert type(solution_result).__module__ != "builtins", (
        "Solution must return an instance of a custom class, not a built-in type."
    )
    assert type(solution_result).__name__ == "Child", (
        "The class should be named 'Child'."
    )
    # Check inheritance by base class names
    base_class_names = [base.__name__ for base in type(solution_result).__bases__]
    assert "Mother" in base_class_names, (
        "The 'Child' class must inherit from a class named 'Mother'."
    )
    assert "Father" in base_class_names, (
        "The 'Child' class must inherit from a class named 'Father'."
    )
    # Check the class attributes
    try:
        attrs = list(vars(solution_result))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 3, "The class should have 3 attributes."
    assert "eye_color" in attrs, (
        "The class should have an attribute called 'eye_color'."
    )
    assert "eye_color_mother" in attrs, (
        "The class should have an attribute called 'eye_color_mother'."
    )
    assert "eye_color_father" in attrs, (
        "The class should have an attribute called 'eye_color_father'."
    )


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
    solution_result = function_to_test(mother_eye_color, father_eye_color)
    reference_result = reference_child_eye_color(mother_eye_color, father_eye_color)

    validate_child_eye_color(solution_result)
    assert solution_result.eye_color == reference_result.eye_color


#
# Exercise 2: Banking System
#


def reference_banking_system(tax_rate: float, interest_rate: float) -> list:
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

        def credit(self, amount):
            self.balance += amount

        def get_balance(self):
            return self.balance + self.balance * self.interest_rate

    return [
        SalaryAccount("SAL-001", tax_rate),
        SavingsAccount("SAV-001", interest_rate),
    ]


def validate_banking_system(solution_result):
    assert isinstance(solution_result, list), "Solution must return a list."
    assert len(solution_result) == 2, "The list must contain exactly two elements."
    assert all(
        isinstance(item, object) and type(item).__module__ != "builtins"
        for item in solution_result
    ), "Both elements in the list must be instances of custom classes."
    assert all(
        "Account" in [base.__name__ for base in type(item).__bases__]
        for item in solution_result
    ), "Both elements in the list must inherit from a class named 'Account'."
    assert type(solution_result[0]).__name__ == "SalaryAccount", (
        "The 1st element in the list should be an instance of 'SalaryAccount'."
    )
    assert type(solution_result[1]).__name__ == "SavingsAccount", (
        "The 2nd element in the list should be an instance of 'SavingsAccount'."
    )
    # Check the class attributes: SalaryAccount
    try:
        attrs = list(vars(solution_result[0]))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 3, "The class 'SalaryAccount' should have 3 attributes."
    assert "account_number" in attrs, (
        "The class 'SalaryAccount' should have an attribute called 'account_number'."
    )
    assert "balance" in attrs, (
        "The class 'SalaryAccount' should have an attribute called 'balance'."
    )
    assert "tax_rate" in attrs, (
        "The class 'SalaryAccount' should have an attribute called 'tax_rate'."
    )
    # Check the class attributes: SavingsAccount
    try:
        attrs = list(vars(solution_result[1]))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 3, "The class 'SavingsAccount' should have 3 attributes."
    assert "account_number" in attrs, (
        "The class 'SavingsAccount' should have an attribute called 'account_number'."
    )
    assert "balance" in attrs, (
        "The class 'SavingsAccount' should have an attribute called 'balance'."
    )
    assert "interest_rate" in attrs, (
        "The class 'SavingsAccount' should have an attribute called 'interest_rate'."
    )
    # Check that each class has the required methods
    required_methods = {"credit", "get_balance"}
    for item in solution_result:
        class_methods = {
            method for method in dir(item) if callable(getattr(item, method))
        }
        assert required_methods.issubset(class_methods), (
            f"The class '{type(item).__name__}' must have the methods: {', '.join(required_methods)}."
        )


@pytest.mark.parametrize(
    "tax_rate, interest_rate",
    [
        (0.20, 0.05),
        (0.18, 0.04),
    ],
)
def test_banking_system(tax_rate, interest_rate, function_to_test):
    solution_result = function_to_test(tax_rate, interest_rate)
    reference_result = reference_banking_system(tax_rate, interest_rate)

    validate_banking_system(solution_result)

    amount = 10000
    # test SalaryAccount functions
    solution_result[0].credit(amount)
    reference_result[0].credit(amount)
    assert solution_result[0].get_balance() == reference_result[0].get_balance()
    # test SavingsAccount functions
    solution_result[1].credit(amount)
    reference_result[1].credit(amount)
    assert solution_result[1].get_balance() == reference_result[1].get_balance()


#
# Exercise 3: Store Inventory
#


def reference_store_inventory(pc: dict, laptop: dict) -> list:
    class Computer:
        """A class representing a computer sold by the online store"""

        def __init__(self, name: str, price: int, quantity: int):
            self.name = name
            self.price = price
            self.quantity = quantity

        def __str__(self):
            return f"Computer with name '{self.name}', price {self.price} CHF and quantity {self.quantity}."

    class PC(Computer):
        """A class representing a PC sold by the online store"""

        def __init__(self, name: str, price: int, quantity: int, expansion_slots: int):
            super().__init__(name, price, quantity)
            self.expansion_slots = expansion_slots

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

        def __str__(self):
            return (
                super().__str__()
                + f" This laptop has a battery life of {self.battery_life} hours."
            )

    return [
        PC(**pc),
        Laptop(**laptop),
    ]


def validate_store_inventory(solution_result):
    assert isinstance(solution_result, list), "Solution must return a list."
    assert len(solution_result) == 2, "The list must contain exactly two elements."
    assert all(
        isinstance(item, object) and type(item).__module__ != "builtins"
        for item in solution_result
    ), "Both elements in the list must be instances of custom classes."
    assert all(
        "Computer" in [base.__name__ for base in type(item).__bases__]
        for item in solution_result
    ), "Both elements in the list must inherit from a class named 'Computer'."
    assert type(solution_result[0]).__name__ == "PC", (
        "The 1st element in the list should be an instance of 'PC'."
    )
    assert type(solution_result[1]).__name__ == "Laptop", (
        "The 2nd element in the list should be an instance of 'Laptop'."
    )
    # Check the class attributes: PC
    try:
        attrs = list(vars(solution_result[0]))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 4, "The class 'PC' should have 4 attributes."
    assert "name" in attrs, "The class 'PC' should have an attribute called 'name'."
    assert "price" in attrs, "The class 'PC' should have an attribute called 'price'."
    assert "quantity" in attrs, (
        "The class 'PC' should have an attribute called 'quantity'."
    )
    assert "expansion_slots" in attrs, (
        "The class 'PC' should have an attribute called 'expansion_slots'."
    )
    # Check the class attributes: Laptop
    try:
        attrs = list(vars(solution_result[1]))
    except TypeError:
        raise SubAssertionError from None
    assert len(attrs) == 4, "The class 'Laptop' should have 4 attributes."
    assert "name" in attrs, "The class 'Laptop' should have an attribute called 'name'."
    assert "price" in attrs, (
        "The class 'Laptop' should have an attribute called 'price'."
    )
    assert "quantity" in attrs, (
        "The class 'Laptop' should have an attribute called 'quantity'."
    )
    assert "battery_life" in attrs, (
        "The class 'Laptop' should have an attribute called 'battery_life'."
    )


@pytest.mark.parametrize(
    "pc, laptop",
    [
        (
            {
                "name": "pc_1",
                "price": 1500,
                "quantity": 1,
                "expansion_slots": 2,
            },
            {
                "name": "laptop_1",
                "price": 1200,
                "quantity": 4,
                "battery_life": 6,
            },
        ),
    ],
)
def test_store_inventory(pc, laptop, function_to_test):
    solution_result = function_to_test(pc, laptop)
    reference_result = reference_store_inventory(pc, laptop)

    validate_store_inventory(solution_result)

    assert str(solution_result[0]) == str(reference_result[0])
    assert str(solution_result[1]) == str(reference_result[1])


#
# Exercise 4: Music Streaming Service
#


def reference_music_streaming_service(
    song_info: list[dict], username: str, playlist_name: str
):
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

    user = User(username)
    user.create_playlist(playlist_name)

    for info in song_info:
        user.add_song_to_playlist(
            playlist_name,
            Song(info["title"], info["artist"], info["album_title"]),
        )

    return user


@pytest.mark.parametrize(
    "song_info, username, playlist_name",
    [
        (
            [
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
            ],
            "Bob",
            "Favorites from Queen",
        ),
    ],
)
def test_music_streaming_service(song_info, username, playlist_name, function_to_test):
    solution_user = function_to_test(song_info, username, playlist_name)
    reference_user = reference_music_streaming_service(
        song_info, username, playlist_name
    )

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
