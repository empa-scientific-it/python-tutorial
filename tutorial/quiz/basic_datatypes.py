from .common import Question, Quiz


class IntegerFloatDivistion(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="What is the result of 5 / 2 + 3.0? What is the type of the result?",
            options={
                "5.5, float": "Correct!",
                "5.0, float": "Remember the difference between integer `//` and float `/` division.",
                "5, integer": "Remember that arthmetic operations on integers and float always returns float.",
            },
            correct_answer="5.5, float",
            hint="The float division operator `/` always retuns float as the result.",
            shuffle=True,
        )

        q2 = Question(
            question="What is the result of 5 // 2 + 3? What is the type of the result?",
            options={
                "5.5, float": "What is the type of the result of the integer division `//`?",
                "5.0, float": "Almost. But why float?",
                "5, integer": "Correct!",
            },
            correct_answer="5, integer",
            hint="The integer division operator `//` always retuns integer as the result.",
            shuffle=True,
        )
        q3 = Question(
            question="What is the result of 5 // 2 + 3.0? What is the type of the result?",
            options={
                "5.5, float": "Remember the difference between integer `//` and float `/` division.",
                "5.0, float": "Correct!",
                "5, integer": "Almost. Remember the implicit type casting between integer and float.",
            },
            correct_answer="5.0, float",
            hint="The integer division operator `//` always retuns integer as the result.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])
