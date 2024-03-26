from .common import Question, Quiz


class OopQuiz(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Based on what you learned about Python's special methods, which of the following statements is true?",
            options={
                "__repr__ is also used for __str__, but not vice versa.": "Correct! This statement is true.",
                "__str__ is also used for __repr__, but not vice versa.": "The opposite is true.",
                "__repr__ and __str__ are completely independent.": "__repr__ is also used for __str__, but not vice versa.",
            },
            correct_answer="__repr__ is also used for __str__, but not vice versa.",
            hint="",
            shuffle=True,
        )

        q2 = Question(
            question="Based on what you learned about Python's comparison methods, which of the following statements is false?",
            options={
                "If we implement __gt__, Python will also use it for __lt__": "This statement is true.",
                "If we implement __lt__, Python will also use it for __le__": "Correct! This statement is false.",
                "If we implement __eq__, Python will also use it for __ne__": "This statement is true.",
            },
            correct_answer="If we implement __lt__, Python will also use it for __le__",
            hint="",
            shuffle=True,
        )

        q3 = Question(
            question="Based on what you learned about the @property keyword, which of the following statements is false?",
            options={
                "@property creates attributes that act like methods but can be accessed and assigned as regular attributes.": "This statement is true.",
                "@property helps implement attributes that require additional logic or validation when getting or setting their values.": "This statement is true.",
                "@property makes code more readable but restricts dynamic attibute behaviour.": "Correct! This statement is false.",
            },
            correct_answer="@property makes code more readable but restricts dynamic attibute behaviour.",
            hint="",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])
