from .common import Question, Quiz


class Threads(Quiz):
    def __init__(self, title="Decide if the following are parallel or not"):
        q1 = Question(
            question="One cashier serves two lines of people in a store?",
            options={
                "Parallel:": "What if the cashier is slow?",
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
