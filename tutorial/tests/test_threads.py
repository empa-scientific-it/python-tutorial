import asyncio
import functools
import multiprocessing
import pathlib
import random
import string
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Coroutine, Dict

import pytest


class SecretServer:
    def __init__(self, key: str, timeout: int = 0.01):
        self.key = key
        self.inner_key = "/" + key
        self.timeout = timeout
        self.sequence = 0
        self.reset_flag = False
        self.resetter = asyncio.create_task(self.reset_sequence())

    async def reset_sequence(self):
        while True:
            await asyncio.sleep(self.timeout)
            self.reset_flag = True

    async def get_value(self):
        if self.reset_flag:
            self.sequence = 0
            self.reset_flag = False
            return "/"
        await asyncio.sleep(self.timeout / len(self.inner_key) * 1.5)
        seq = self.sequence
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


def read_segment(file: pathlib.Path, start: int, end: int) -> str:
    with open(file) as f:
        f.seek(start)
        return f.read(end - start)


def segment_stat(segment: str) -> Dict[str, int]:
    return Counter(segment.strip())


def count_words(
    file: pathlib.Path, size: int, n_processes: int, index: int
) -> Dict[str, int]:
    segment_size = size // n_processes
    start = index * segment_size
    end = start + segment_size
    return segment_stat(read_segment(file, start, end))


def reference_exercise1(input_path: pathlib.Path, size: int) -> Dict[str, int]:
    workers = multiprocessing.cpu_count()
    with ProcessPoolExecutor(workers) as executor:
        result = executor.map(
            functools.partial(count_words, input_path, size, workers), range(workers)
        )
    return dict(functools.reduce(lambda x, y: x + y, result, Counter()))


@pytest.mark.parametrize("size", [1000, 10000, 100000])
def test_exercise1_total_counts(
    function_to_test: Callable,
    make_random_file: Callable[[None], pathlib.Path],
    size: int,
):
    rf = make_random_file(size)
    reference_res = reference_exercise1(rf, size)
    total_letters = sum(reference_res.values())
    user_res = function_to_test(rf, size)
    total_letters_user = sum(user_res.values())
    assert total_letters == total_letters_user


@pytest.mark.parametrize("size", [1000, 10000, 100000])
def test_exercise1_counts(
    function_to_test: Callable,
    make_random_file: Callable[[None], pathlib.Path],
    size: int,
):
    rf = make_random_file(size)
    reference_res = reference_exercise1(rf, size)
    user_res = function_to_test(rf, size)
    assert user_res == reference_res


# TODO: find a way to test that the user is using multiprocessing (directly or indirectly)
# def test_exercise1_processes(function_to_test: Callable, make_random_file: Callable[[None], pathlib.Path], monkeypatch: pytest.MonkeyPatch):
#     with patch.object(multiprocessing.Process, "start") as process_mock:
#         size = 1000
#         rf = make_random_file(size)
#         user_res = function_to_test(rf, size)
#     assert process_mock.mock_calls or


def find_word(letters: list[str], separator: str) -> bool:
    """
    This function finds a word in a list of letters separated by a separator.
    """
    return [w for w in "".join(letters).split(separator) if len(w) > 0]


async def reference_exercise2(server: SecretServer) -> str:
    rng = 30
    # Concurrently get 30 letters from the server
    letters = await asyncio.gather(*[server.get_value() for _ in range(rng)])

    # Function to concurrently check if the key is valid
    async def check_key(key: str):
        valid = await server.check_key(key)
        return valid, key

    res = await asyncio.gather(*[check_key(key) for key in find_word(letters, "/")])
    # Return the first valid key
    return [key for valid, key in res if valid][0]


@pytest.mark.parametrize("key", ["Secret", "Very secret", "Extremely secret"])
def test_exercise2(key: str, function_to_test: Coroutine[Any, Any, str]):
    async def run_test() -> str:
        server = SecretServer(key, timeout=1)
        res = await function_to_test(server)
        return res

    res = asyncio.run(run_test())
    assert res == key
