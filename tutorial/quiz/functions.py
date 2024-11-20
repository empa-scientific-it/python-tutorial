from .common import Question, Quiz


class Functions(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="How do you indicate a docstring for a Python function?",
            options={
                "With triple quotes": "Correct!",
                "With # Docstring:": "What's the meaning of # in Python?",
                "With // Docstring:": "Is // a valid Python comment?",
            },
            correct_answer="With triple quotes",
            shuffle=True,
        )

        q2 = Question(
            question="What is the purpose of type hints in Python function definitions?",
            options={
                "To enforce strict typing": "Does the interpreter enforce type hints?",
                "Only to make the code more readable": "Not only...",
                "To improve code readability and document the expected types of arguments and return values": "Correct!",
            },
            correct_answer="To improve code readability and document the expected types of arguments and return values",
            shuffle=True,
        )

        q3 = Question(
            question="How do you define a function that accepts an arbitrary number of arguments of any type?",
            options={
                "def function_name(*args):": "What about keyword arguments?",
                "def function_name(*args, **kwargs):": "Correct!",
                "def function_name(**kwargs):": "What about positional arguments?",
            },
            correct_answer="def function_name(*args, **kwargs):",
            shuffle=True,
        )

        q4 = Question(
            question="""What's the output of the following Python code?

<pre><code class="language-python">def my_function(x):
    if x &lt; 0:
        return &quot;negative&quot;
    elif x == 0:
        return &quot;zero&quot;

result = my_function(-5) + my_function(0) + my_function(5)

print(result)
</code></pre>
""",
            options={
                "negativezeropositive": "What type is the function's parameter? And its return value?",
                "negative0positive": "What does the function return for the input 5? Try it in a cell below!",
                "Error: cannot concatenate 'str' and 'NoneType' objects": "Correct!",
            },
            correct_answer="Error: cannot concatenate 'str' and 'NoneType' objects",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4])
