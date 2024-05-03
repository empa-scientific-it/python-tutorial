from .common import Question, Quiz


class ConditionalsQuiz(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What would be the output of the following code?
                <pre><code class="language-python">
                    if 'blue' in {'red': 1, 'blue': 2, 'green': 3}:
                        print(1, end=", ")
                        print(2, end=", ")
                        if 'd' in 'abc':
                            print(3, end=", ")
                    print(4)
                </code></pre>
            """,
            options={
                "1, 2, 3, 4": "The character 'd' does not exist in the string 'abc', so the second if statement is False.",
                "1, 2, 4": "Correct!",
                "4": "The word 'blue' exists in the dictionary's keywords, so the first if statement is True.",
            },
            correct_answer="1, 2, 4",
            shuffle=True,
        )

        q2 = Question(
            question="""What would be the output of the following code?
                <pre><code class="language-python">
                    x = 5
                    if x > 10:
                        print("A")
                    else:
                        if x > 7:
                            print("B")
                        else:
                            print("C")
                </code></pre>
            """,
            options={
                "A": "This code is using nested if-else statements. Make sure to check all conditions.",
                "B": "This code is using nested if-else statements. Make sure to check all conditions. ",
                "C": "Correct!",
            },
            correct_answer="C",
            shuffle=True,
        )

        q3 = Question(
            question="""Is the following a syntactically valid statement?
                <pre><code class="language-python">
                    if x < y: if x > 10: print('something')
                </code></pre>
            """,
            options={
                "No": "Correct! You cannot write a nested statement in one line.",
                "Yes": "Conditionals, when written in one line, can only be simple and not nested.",
            },
            correct_answer="No",
            shuffle=True,
        )

        q4 = Question(
            question="""Is the following a syntactically valid statement?
                <pre><code class="language-python">
                    min = a if a < b else b
                </code></pre>
            """,
            options={
                "Yes": "Correct! This is called a ternary operator.",
                "No": "It is syntactically correct and is called a ternary operator. It is particularly handy when you want to avoid writing multiple lines for a simple if-else statement.",
            },
            correct_answer="Yes",
            shuffle=True,
        )

        q5 = Question(
            question="""How do you check for multiple conditions in a single if statement?""",
            options={
                "if x > 10 and y < 5:": "Correct! Python uses the keyword <strong>and</strong>.",
                "if x > 10 && y < 5:": "This is not a valid Python operator.",
                "if x > 10 & y < 5:": "& is bitwise AND operator.",
            },
            correct_answer="if x > 10 and y < 5:",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4, q5])


class LoopsQuiz(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What would be the output of the following code?
                <pre><code class="language-python">
                    x = 0
                    for i in range(2):
                        for j in range(-1, -10, -1):
                            x += 1
                    print(x)
                </code></pre>
            """,
            options={
                "9": "Pay attention to the range of the outer loop.",
                "18": "Correct!",
                "20": "Remember that <code>range()</code> does not include its stop element.",
            },
            correct_answer="18",
            shuffle=True,
        )

        q2 = Question(
            question="""What would be the output of the following code?
                <pre><code class="language-python">
                    for num in range(-2, -5, -1):
                        print(num, end=", ")
                </code></pre>
            """,
            options={
                "-2, -3, -4, -5,": "Remember that <code>range()</code> does not include its stop element.",
                "-2, -1, 0,": "Pay attention to the step element of <code>range()</code>.",
                "-2, -3, -4,": "Correct!",
            },
            correct_answer="-2, -3, -4,",
            shuffle=True,
        )

        q3 = Question(
            question="""What would be the output of the following code?
                <pre><code class="language-python">
                    var = 10
                    for i in range(10):
                        for j in range(2, 10, 1):
                            if var % 2 == 0:
                                continue
                                var += 1
                        var += 1
                    else:
                        var += 1
                    print(var)
                </code></pre>
            """,
            options={
                "12": "Pay attention to the range of the outer loop.",
                "20": "Pay attention to the <code>else</code> statement.",
                "21": "Correct!",
            },
            correct_answer="21",
            shuffle=True,
        )

        q4 = Question(
            question="""What would be the output of the following code?
                <pre><code class="language-python">
                    s = ""
                    n = 5
                    while n > 0:
                        n -= 1
                        if (n % 2) == 0:
                            continue

                        a = ['apple', 'mango', 'banana']
                        while a:
                            s += str(n) + a.pop(0)
                            if len(a) < 2:
                                break
                    print(s)
                </code></pre>
            """,
            options={
                "3apple3mango1apple1mango": "Correct!",
                "3apple3mango3banana1apple1mango1banana": "Pay attention to the <code>break</code>.",
                "3apple3mango1banana": "Remember that list <code>a</code> gets re-initialized in every iteration of the outer loop.",
            },
            correct_answer="3apple3mango1apple1mango",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4])
