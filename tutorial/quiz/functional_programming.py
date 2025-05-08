from .common import Question, Quiz


class PureFunctions(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""Is the following function pure?<br><div><pre>def f(x: int) -> int: \n    return x + 1</pre></div>""",
            options={
                "Yes": "Correct!",
                "No": "Why not? The function does not have any side effects.",
            },
            correct_answer="Yes",
            hint="Purity means that the function does not have any side effects, for example changing variables other than the inputs, opening files, etc.",
            shuffle=True,
        )
        q2 = Question(
            question="""Is the following function pure?<br><pre>a = []\ndef f():\n    a.append(1)</pre>""",
            options={
                "Yes": "Wrong! Notice that <code>a</code> is not an argument to the function",
                "No": "Correct",
            },
            correct_answer="No",
            hint="Purity means that the function does not have any side effects, for example changing variables other than the inputs, opening files, etc.",
            shuffle=True,
        )
        q3 = Question(
            question="""Is the following function pure?<br><pre>def f(a: list[int]) -> list[int]:\n    return a+[1]</pre>""",
            options={
                "Yes": "Correct!",
                "No": "Wrong! Notice that <code>a</code> is an argument to the function and we return a new list by concatenating <code>a</code> and <code>[1]</code>.",
            },
            correct_answer="Yes",
            hint="Purity means that the function does not have any side effects, for example changing variables other than the inputs, opening files, etc.",
            shuffle=True,
        )
        q4 = Question(
            question="""Is the following function pure?<br><pre>def f(a: dict[str, str]) -> None:\n    a["test"] = "dest"</pre>""",
            options={
                "Yes": "Wrong!  Notice that <code>a</code> is an argument to the function and we add a new key-value pair to this dictionary.",
                "No": "Correct!",
            },
            correct_answer="No",
            hint="Purity means that the function does not have any side effects, for example changing variables other than the inputs, opening files, etc.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4])
