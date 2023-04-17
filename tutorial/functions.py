from .common import Question, Quiz


class Functions(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="How do you indicate a docstring for a Python function?",
            options={
                "With triple quotes": "Correct!",
                "With # Docstring:": "",
                "With // Docstring:": "Is // a valid Python comment?",
            },
            correct_answer="With triple quotes",
            shuffle=True,
        )

        q2 = Question(
            question="What is the purpose of type hints in Python function definitions?",
            options={
                "To enforce strict typing": "",
                "To make the code more readable": "",
                "To document the expected types": "Correct!",
            },
            correct_answer="To document the expected types",
            shuffle=True,
        )

        q3 = Question(
            question="What is the syntax to define a function that takes an arbitrary number of arguments in Python?",
            options={
                "def function_name(*args)": "What about keyword arguments?",
                "def function_name(*args, **kwargs):": "Correct!",
                "def function_name(**kwargs):": "What about positional arguments?",
            },
            correct_answer="def function_name(*args, **kwargs):",
            shuffle=True,
        )

        q4 = Question(
            question="""What's the output of the Python code in the cell below?""",
            options={
                "negativezeropositive": "What type is the function's parameter? And its return value?",
                "negative0positive": "What does the function return for the input 5? Try it in a cell below!",
                "Error": "Correct! Cannot concatenate 'str' and 'NoneType' objects",
            },
            correct_answer="Error",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4])
