from .common import Question, Quiz


class OopQuiz(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Based on what you learned about Python's special methods, which statement best describes the relationship between <i>__str__</i> and <i>__repr__</i>?",
            options={
                "__repr__ is used as a fallback when __str__ is missing.": "Correct! When __str__ is not defined, Python will use __repr__ instead.",
                "__str__ is used as a fallback when __repr__ is missing.": "Think again based on the example we saw earlier.",
                "__repr__ and __str__ are independent methods with no relationship to each other.": "There is a relationship between the two methods. Which one could it be?",
            },
            correct_answer="__repr__ is used as a fallback when __str__ is missing.",
            hint="",
            shuffle=True,
        )

        q2 = Question(
            question="Based on what you learned about Python's comparison methods, which of the following statements is <strong>false</strong>?",
            options={
                "If we implement __gt__, Python will also use it for __lt__": "Wrong! This statement is true because Python is able to cleverly swap the comparison terms.",
                "If we implement __lt__, Python will also use it for __le__": "Correct! This statement is false because Python has no knowledge of what equality could mean based just on a comparison.",
                "If we implement __eq__, Python will also use it for __ne__": "Wrong! This statement is true because Python is able to cleverly negate the equality comparison.",
            },
            correct_answer="If we implement __lt__, Python will also use it for __le__",
            hint="",
            shuffle=True,
        )

        q3 = Question(
            question="Based on what you learned about the <i>@property</i> keyword, which of the following statements is <strong>true</strong>?",
            options={
                "@property creates attributes that act like methods, which means that they need to be called as regular methods.": "Wrong! This statement is false beacuse we access these attributes as regular ones.",
                "@property helps implement attributes that require additional logic or validation when calculating their values.": "Correct! This is how you can make your classes more readable and user-friendly.",
                "@property allows to get and set the values of attributes, while applying additional logic in the background.": "Wrong! This statement is false beacuse we are not allowed to directly set the values of these attributes.",
            },
            correct_answer="@property helps implement attributes that require additional logic or validation when calculating their values.",
            hint="",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])
