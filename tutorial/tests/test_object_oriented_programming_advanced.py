import pytest

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
# Exercise 2: Online Store Inventory System
#


def reference_store_inventory(computers: tuple[str]) -> list[str]:
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

    class_map = {"PC": PC, "Laptop": Laptop}

    inventory = []
    for computer in computers:
        class_type = class_map.get(computer["type"])
        inventory.append(class_type(*list(computer.values())[-4:]))

    result = []
    for item in inventory:
        result.append(str(item))

    return result


@pytest.mark.parametrize(
    "computers",
    [
        [
            {
                "type": "PC",
                "name": "pc1",
                "price": 1500,
                "quantity": 1,
                "expansion_slots": 2,
            },
            {
                "type": "Laptop",
                "name": "laptop1",
                "price": 1200,
                "quantity": 4,
                "battery_life": 6,
            },
        ]
    ],
)
def test_store_inventory(computers, function_to_test):
    assert function_to_test(computers) == reference_store_inventory(computers)


#
# Exercise 3:
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


@pytest.mark.parametrize(
    "song_info",
    [
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
        ]
    ],
)
def test_music_streaming_service(song_info, function_to_test):
    solution_user = function_to_test()
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
