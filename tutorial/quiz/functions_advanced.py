from markdown import markdown

from .common import Question, Quiz, Spoiler

tricky_closures = Spoiler(
    "Answer",
    markdown(
        "Look at the definition of `op()`. Does it reference the variable `n` other than in setting the default value of `n`? **No**. "
        "Hence, the variable `n` is **not** a free variable, and the function `op()` is **not** a closure, just a plain function."
    ),
)


class FunctionsAdvancedQuiz(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""Are functions in Python objects?<br>
                        <div><pre>def example():\n    return "Hello, World!"\n\n# Can we do this?\nfunc = example\nprint(func())</pre></div>""",
            options={
                "Yes": "Correct! Functions in Python are first-class objects. They can be assigned to variables, passed as arguments, and returned from other functions.",
                "No": "Incorrect. Functions in Python are indeed objects and can be manipulated like any other object.",
            },
            correct_answer="Yes",
            hint="Think about whether you can assign a function to a variable or pass it as an argument.",
            shuffle=True,
        )

        q2 = Question(
            question="""What is the correct order of scope resolution in Python?<br>
                        <div><pre>def outer():\n    x = 'enclosing'\n    def inner():\n        x = 'local'\n        print(x)\n    inner()\nouter()</pre></div>""",
            options={
                "Local → Enclosing → Global → Built-in": "Correct! Python resolves variable names in this order.",
                "Global → Local → Enclosing → Built-in": "Incorrect. The correct order is Local → Enclosing → Global → Built-in.",
                "Built-in → Global → Enclosing → Local": "Incorrect. The correct order is Local → Enclosing → Global → Built-in.",
            },
            correct_answer="Local → Enclosing → Global → Built-in",
            hint="Remember the acronym LEGB.",
            shuffle=True,
        )

        q3 = Question(
            question="""Why is using mutable default arguments in Python considered a bad practice?<br>
                        <div><pre>def add_item(item, items=[]):\n    items.append(item)\n    return items\n\nprint(add_item(1))\nprint(add_item(2))</pre></div>""",
            options={
                "Because the default value is shared across all calls to the function.": "Correct! Mutable default arguments retain their state across function calls.",
                "Because Python does not allow mutable default arguments.": "Incorrect. Python allows mutable default arguments, but they can lead to unexpected behavior.",
                "Because it causes a syntax error.": "Incorrect. Mutable default arguments do not cause syntax errors.",
            },
            correct_answer="Because the default value is shared across all calls to the function.",
            hint="Think about what happens to the `items` list after multiple calls.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])


class FunctionsAdvancedQuizLambdas(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What is the correct syntax for a lambda function that adds two numbers?<br>
                        <div><pre># Example usage:\nadd = ?\nprint(add(2, 3))  # Output: 5</pre></div>""",
            options={
                "lambda x, y: x + y": "Correct! This is the correct syntax for a lambda function.",
                "def lambda(x, y): x + y": "Incorrect. Lambda functions do not use the `def` keyword.",
                "lambda (x, y): x + y": "Incorrect. Parentheses are not used around the arguments in lambda functions.",
            },
            correct_answer="lambda x, y: x + y",
            hint="Lambda functions use the syntax `lambda arguments: expression`.",
            shuffle=True,
        )

        q2 = Question(
            question="""What is the limitation of lambda functions in Python?<br>
                        <div><pre># Example:\nadd = lambda x, y: x + y\nprint(add(2, 3))</pre></div>""",
            options={
                "They can only contain a single expression.": "Correct! Lambda functions are limited to a single expression.",
                "They cannot take arguments.": "Incorrect. Lambda functions can take arguments.",
                "They are slower than regular functions.": "Incorrect. Lambda functions are not inherently slower than regular functions.",
            },
            correct_answer="They can only contain a single expression.",
            hint="Think about the syntax of lambda functions.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])


class FunctionsAdvancedQuizClosures(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What is a closure in Python?<br>
                        <div><pre>def outer():\n    x = 'free variable'\n    def inner():\n        return x\n    return inner\n\nclosure = outer()\nprint(closure())</pre></div>""",
            options={
                "A function that retains access to its enclosing scope's variables.": "Correct! Closures allow inner functions to remember variables from their enclosing scope.",
                "A function that does not take any arguments.": "Incorrect. Closures are not defined by the number of arguments.",
                "A function that is defined inside another function.": "Incorrect. While closures are often defined inside other functions, this is not their defining characteristic.",
            },
            correct_answer="A function that retains access to its enclosing scope's variables.",
            hint="Think about how the `inner` function accesses `x` even after `outer` has finished executing.",
            shuffle=True,
        )

        q2 = Question(
            question="""Why is the variable `x` in the following example considered a free variable?<br>
                        <div><pre>def outer():\n    x = 10\n    def inner():\n        return x\n    return inner\n\nclosure = outer()\nprint(closure())</pre></div>""",
            options={
                "Because it is defined in the enclosing scope and used in the inner function.": "Correct! A free variable is one that is not defined in the local scope but is used in the function.",
                "Because it is defined in the global scope.": "Incorrect. The variable `x` is defined in the enclosing scope, not the global scope.",
                "Because it is a local variable.": "Incorrect. The variable `x` is not local to the inner function.",
            },
            correct_answer="Because it is defined in the enclosing scope and used in the inner function.",
            hint="Think about where `x` is defined and how it is accessed.",
            shuffle=True,
        )

        q3 = Question(
            question="""What happens if you modify a free variable in a closure?<br>
                        <div><pre>def outer():\n    x = 10\n    def inner():\n        x += 1\n        return x\n    return inner\n\nclosure = outer()\nclosure()</pre></div>""",
            options={
                "It raises an UnboundLocalError.": "Correct! You cannot modify a free variable directly in a closure without declaring it as nonlocal.",
                "It modifies the variable in the enclosing scope.": "Incorrect. Free variables cannot be modified directly without using the `nonlocal` keyword.",
                "It creates a new local variable.": "Incorrect. The `x` in the inner function is not treated as a new local variable in this case.",
            },
            correct_answer="It raises an UnboundLocalError.",
            hint="Think about whether the `x` in the inner function is treated as local or nonlocal.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])


class FunctionsAdvancedQuizDecorators(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What is the purpose of a decorator in Python?<br>
                        <div><pre>@decorator\ndef example():\n    pass</pre></div>""",
            options={
                "To modify or extend the behavior of a function or method.": "Correct! Decorators are used to enhance or modify functions.",
                "To define a new function.": "Incorrect. Decorators do not define new functions.",
                "To execute a function immediately.": "Incorrect. Decorators wrap a function but do not execute it immediately.",
            },
            correct_answer="To modify or extend the behavior of a function or method.",
            hint="Think about how decorators are used to add functionality to existing functions.",
            shuffle=True,
        )

        q2 = Question(
            question="""What does the following decorator do?<br>
                        <div><pre>def decorator(func):\n    def wrapper():\n        print("Before the function call")\n        func()\n        print("After the function call")\n    return wrapper\n\n@decorator\ndef example():\n    print("Inside the function")\n\nexample()</pre></div>""",
            options={
                "It adds behavior before and after the function call.": "Correct! The decorator adds behavior before and after the wrapped function is executed.",
                "It modifies the function to return a different value.": "Incorrect. The decorator does not modify the return value of the function.",
                "It executes the function twice.": "Incorrect. The function is executed only once.",
            },
            correct_answer="It adds behavior before and after the function call.",
            hint="Look at the `wrapper` function and what it does before and after calling `func()`.",
            shuffle=True,
        )

        q3 = Question(
            question="""Can a decorator accept arguments? If yes, how?<br>
                        <div><pre>def decorator_with_args(arg):\n    def decorator(func):\n        def wrapper():\n            print(f"Decorator argument: {arg}")\n            func()\n        return wrapper\n    return decorator\n\n@decorator_with_args("Hello")\ndef example():\n    print("Inside the function")\n\nexample()</pre></div>""",
            options={
                "Yes, by nesting the decorator inside another function.": "Correct! A decorator can accept arguments by using an additional outer function.",
                "No, decorators cannot accept arguments.": "Incorrect. Decorators can accept arguments by using an additional outer function.",
                "Yes, but only if the arguments are strings.": "Incorrect. Decorators can accept arguments of any type.",
            },
            correct_answer="Yes, by nesting the decorator inside another function.",
            hint="Think about how the `decorator_with_args` function works.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])


class FunctionsAdvancedQuizGenerators(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What is the purpose of the `yield` keyword in Python?<br>
                        <div><pre>def generator():\n    yield 1\n    yield 2\n    yield 3\n\nfor value in generator():\n    print(value)</pre></div>""",
            options={
                "To produce a value and pause the function's execution.": "Correct! The `yield` keyword allows a function to produce values one at a time.",
                "To return a value and terminate the function.": "Incorrect. `yield` pauses the function, unlike `return` which terminates it.",
                "To define a function.": "Incorrect. `yield` is used inside a function, not to define it.",
            },
            correct_answer="To produce a value and pause the function's execution.",
            hint="Think about how `yield` differs from `return`.",
            shuffle=True,
        )

        q2 = Question(
            question="""What happens when you call `next()` on a generator that has no more values to yield?<br>
                        <div><pre>def generator():\n    yield 1\n    yield 2\n\ngen = generator()\nprint(next(gen))\nprint(next(gen))\nprint(next(gen))</pre></div>""",
            options={
                "A StopIteration exception is raised.": "Correct! When a generator is exhausted, calling `next()` raises a StopIteration exception.",
                "The generator restarts from the beginning.": "Incorrect. Generators do not restart automatically.",
                "It returns `None`.": "Incorrect. Generators do not return `None` when exhausted; they raise an exception.",
            },
            correct_answer="A StopIteration exception is raised.",
            hint="Think about what happens when a generator is exhausted.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])
