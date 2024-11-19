from .common import Question, Quiz


class OopAdvanced(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="A method with which decorator takes `cls` as its first parameter?",
            options={
                "@classmethod": "Correct! A class method is bound to a class rather than its instances and the parameter `cls` represents the class itself.",
                "@staticmethod": "A static method does not have access to `cls` or `self` and cannot modify the class state.",
                "@abstractmethod": "This decorator defines a method in an abstract class that **must** be implemented by all its concrete subclasses.",
            },
            correct_answer="@classmethod",
            hint="",
            shuffle=True,
        )

        q2 = Question(
            question="Even though it's not recommended, which type of attributes and methods can be accessed using name mangling in Python?",
            options={
                "public": "All public attributes and methods can be accessed from anywhere, by default.",
                "private": "Correct! Even though private attributes and methods should not be directly accessed from outside the class, Python allows for name mangling.",
                "protected": "Protected attibutes and methods should not be accessed directly from outside the class, but there's no strict enforcement.",
            },
            correct_answer="private",
            hint="",
            shuffle=True,
        )

        q3 = Question(
            question="What is something that `attrs` provides but `dataclasses` doesn't?",
            options={
                "__init__()": "Both packages automatically generate `__init__()`: `dataclasses` uses the `@dataclass` decorator, while `attrs` uses `@define`.",
                "__repr__()": "Both packages automatically generate `__repr__()` to help you easily print a class instance.",
                "validators": "Correct! You need to define the attribute as a `field()` and then use the validator decorator.",
            },
            correct_answer="validators",
            hint="",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])
