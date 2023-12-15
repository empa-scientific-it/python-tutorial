import asyncio
import functools
import pathlib
import random
import string
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from typing import Awaitable, Callable

import pytest


class SecretServer:
    def __init__(self, key: str, timeout: int = 0.01):
        self.key = key
        self.inner_key = "/" + key
        self.timeout = timeout
        self.sequence = 0
        self.reset_flag = False
        # Count how many concurrent requests are being made
        self.resetter: asyncio.Task = None

    async def start(self):
        self.resetter = asyncio.create_task(self.reset_sequence())

    async def reset_sequence(self):
        while True:
            await asyncio.sleep(self.timeout)
            self.reset_flag = True

    async def get_value(self):
        # Increase the concurrency counter
        if self.reset_flag:
            self.sequence = 0
            self.reset_flag = False
            return "/"
        await asyncio.sleep(self.timeout / len(self.inner_key) * 1.5)
        seq = self.sequence
        # Increase the sequence counter
        self.sequence = (self.sequence + 1) % len(self.inner_key)
        return self.inner_key[seq]

    async def check_key(self, key: str):
        return key == self.key


@pytest.fixture(scope="session")
def make_random_file(tmp_path_factory: pytest.TempPathFactory) -> str:
    def inner_file(size: int = 1000):
        file = tmp_path_factory.mktemp("data").joinpath("file.txt")
        with open(file, "w") as f:
            f.write("".join(random.choices(string.ascii_letters, k=size)))
        return file

    return inner_file


def reference_exercise1(
    input_file: pathlib.Path, size: int, n_processes: int
) -> dict[str, int]:
    def read_segment(file: pathlib.Path, start: int, end: int) -> str:
        with open(file) as f:
            f.seek(start)
            return f.read(end - start)

    def segment_stat(segment: str) -> dict[str, int]:
        return Counter(segment.strip())

    def count_words(
        file: pathlib.Path, size: int, n_processes: int, segment_index: int
    ) -> dict[str, int]:
        segment_size = size // n_processes
        remainder = size % n_processes
        start = segment_index * segment_size + min(segment_index, remainder)
        end = start + segment_size + (1 if segment_index < remainder else 0)
        return segment_stat(read_segment(file, start, end))

    with ProcessPoolExecutor(n_processes) as executor:
        result = executor.map(
            functools.partial(count_words, input_file, size, n_processes),
            range(n_processes),
        )
    return dict(functools.reduce(lambda x, y: x + y, result, Counter()))


random_file_sizes = [53, 123, 517, 1000, 10000]


@pytest.mark.parametrize(
    "size, n_processes", [(s, w) for s in random_file_sizes for w in [2, 4, 5, 7]]
)
def test_exercise1_total_counts(
    function_to_test: Callable,
    make_random_file: Callable[[None], pathlib.Path],
    size: int,
    n_processes: int,
):
    rf = make_random_file(size)
    user_res = function_to_test(rf, size, n_processes)
    total_letters_user = sum(user_res.values())
    assert total_letters_user == size


@pytest.mark.parametrize(
    "size, workers", [(s, w) for s in random_file_sizes for w in [2, 4, 5, 7]]
)
def test_exercise1_counts(
    function_to_test: Callable,
    make_random_file: Callable[[None], pathlib.Path],
    size: int,
    workers: int,
):
    rf = make_random_file(size)
    # We read the file and use a counter as a trick. It is not parallel but we are
    # sure it is correct
    with open(rf) as f:
        file_content = f.read()
    # reference_res = count_words_parallel(rf, size, workers)
    user_res = function_to_test(rf, size, workers)
    assert user_res == Counter(file_content)


# TODO: find a way to test that the user is using multiprocessing (directly or indirectly)
# def test_exercise1_processes(function_to_test: Callable, make_random_file: Callable[[None], pathlib.Path], monkeypatch: pytest.MonkeyPatch):
#     n_process_mock = MagicMock()
#     n_process_mock.return_value = 2
#     size = 1000
#     rf = make_random_file(size)
#     user_res = function_to_test(rf, size, n_process_mock)
#     assert n_process_mock.called


def find_word(letters: list[str], separator: str) -> bool:
    """
    This function finds a word in a list of letters separated by a separator.
    """
    return [w for w in "".join(letters).split(separator) if len(w) > 0]


async def reference_exercise2(server: SecretServer) -> str:
    rng = 50
    # Concurrently get 30 letters from the server
    letters = await asyncio.gather(*[server.get_value() for _ in range(rng)])

    # Function to concurrently check if the key is valid
    async def check_key(key: str):
        valid = await server.check_key(key)
        return valid, key

    res = await asyncio.gather(*[check_key(key) for key in find_word(letters, "/")])
    # Return the first valid key
    return [key for valid, key in res if valid][0]


@pytest.mark.parametrize("secret_key", ["Secret", "Very secret", "Extremely secret"])
def test_exercise2(function_to_test: Callable[[None], Awaitable[str]], secret_key: str):
    server = SecretServer(secret_key, timeout=1)

    async def run_test() -> str:
        await server.start()
        res = await function_to_test(server)
        return res

    res = asyncio.run(run_test())
    print(res, secret_key)
    assert secret_key == res
