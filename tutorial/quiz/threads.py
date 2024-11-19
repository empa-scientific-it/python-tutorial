import os
from concurrent.futures import ProcessPoolExecutor
from time import sleep

from .common import Question, Quiz


class Threads(Quiz):
    def __init__(self, title="Decide if the following are parallel or not"):
        q1 = Question(
            question="One cashier serves two lines of people in a store",
            options={
                "Parallel": "What if the cashier is slow?",
                "Not parallel": "Correct, there's only one cashier",
            },
            correct_answer="Not parallel",
            shuffle=True,
        )

        q2 = Question(
            question="A swimming pool offers multiple shower stalls",
            options={
                "Parallel": "Correct!",
                "Not parallel": "We have more than one shower",
            },
            correct_answer="Parallel",
            shuffle=True,
        )

        q3 = Question(
            question="Multiple people take turns drinking from a cup",
            options={
                "Parallel": "Why are they sharing a cup?",
                "Not parallel": "Correct!",
            },
            correct_answer="Not parallel",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])


def work(n: int, show: bool = False) -> int:
    """This function waits a small time and returns the number"""
    pid = os.getpid()
    if show:
        print(f"{pid} Working on {n}\n")
    sleep(0.001)
    return n


def parallel_work(executor: ProcessPoolExecutor, n: int, batch_size=5) -> int:
    """Wrapper function to run the `work` function in parallel and compute the sum of their results"""
    res = executor.map(work, range(n), chunksize=batch_size)
    return sum(res)


def sequential_work(n: int) -> int:
    """
    This function computes the sum of the results of the `work` function sequentially
    """
    return sum([work(i) for i in range(n)])
