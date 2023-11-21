import asyncio
from typing import Callable

import pytest


class SecretServer:
    def __init__(self, key: str, timeout: int = 5):
        self.key = "/" + key
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
        await asyncio.sleep(self.timeout / len(self.key) * 2)
        seq = self.sequence
        self.sequence = (self.sequence + 1) % len(self.key)
        print(f"Returning value {self.key[self.sequence]}")
        return self.key[seq]

    async def check_key(self, key: str):
        if key == self.key:
            return f"Congratulations, you found the secret key! The key for this case was: {key}"


def reference_exercise1() -> int:
    return 42


def test_exercise1(function_to_test: Callable):
    assert function_to_test("") == 42


def reference_exercise2(server: SecretServer) -> int:
    async def inner():
        return 42

    return asyncio.run(inner())


def test_exercise2(function_to_test: Callable):
    async def run_test():
        server = SecretServer("secret_key", timeout=1)
        res = await function_to_test(server)
        return res

    res = asyncio.run(run_test())
    assert res == 42
