from .common import Question, Quiz


class StringOutput(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="The function <code>print()</code> can be used only to output strings.",
            options={
                "False": "Correct! It can be used on any Python object.",
                "True": "Wrong! Try it in a cell below.",
            },
            correct_answer="False",
            shuffle=True,
        )

        q2 = Question(
            question="What does the <code>f</code> before a string do? E.g <code>f'Hello {name}'</code>",
            options={
                "It formats the string as a float": "Wrong! Try it in a cell below.",
                "It changes the color of the string": "Wrong! Try it in a cell below.",
                "It allows inserting variables into a string": "Correct! In the example above, it will print the value of the <code>name</code> variable, if it is defined.",
            },
            correct_answer="It allows inserting variables into a string",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])


class StringInput(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="What does the function <code>input</code> do?",
            options={
                "It asks for user input and returns it as a string": "Correct! It is used to read user input from the console.",
                "It shows a list of input devices available on the current computer": "Wrong! It is used to read user input from the console.",
            },
            correct_answer="It asks for user input and returns it as a string",
            shuffle=True,
        )

        q2 = Question(
            question="What happens if you call <code>input()</code> in the middle of a function?",
            options={
                "The function execution stops and it waits for the user to type an input": "Correct! Input is a blocking function which waits for user to enter a string in the console and press enter.",
                "The function continues its execution": "Wrong!",
            },
            correct_answer="The function execution stops and it waits for the user to type an input",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])


class Paths(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="What does the operator <code>/</code> do when applied to two <code>Pathlib.Path</code> objects?",
            options={
                "It removes the second path from the first": "Wrong, try it in the shell.",
                "It concatenates paths": "Correct, it lets you construct a path from different segments",
            },
            correct_answer="It concatenates paths",
            shuffle=True,
        )

        q2 = Question(
            question="If you use Pathlib,  do you need to use different path separators on Windows and Linux to combine path segments?",
            options={
                "No, you can combine Pathlib.Path objects with /": "Correct! Pathlib will then generate the correct path for your OS.",
                "Yes": "Wrong! You can always use  <code>/</code>",
            },
            correct_answer="No, you can combine Pathlib.Path objects with /",
            shuffle=True,
        )

        q3 = Question(
            question="""The path </code>Pathlib.Path("./")</code> represent a relative path. What location does it refer to?""",
            options={
                "Relative to the current working directory, the location of the current Python script being run": "Correct!",
                "Relative to the user's home directory": "Wrong!",
            },
            correct_answer="Relative to the current working directory, the location of the current Python script being run",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])


class ReadFiles(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Can you read from a file before calling <code>open</code>?",
            options={
                "Yes": "Wrong, if the file is not open, we cannot access its contents.",
                "No": "Correct, we need to open the file first.",
            },
            correct_answer="No",
            shuffle=True,
        )

        q2 = Question(
            question="The function <code>readlines</code> reads the entire content of a text file into <b>one string</b>. Is this correct?",
            options={
                "No": "Correct! It reads the file line by line.",
                "Yes": "Wrong! It reads the file line by line and returns a list of <code>str</code>, with one element for each line.",
            },
            correct_answer="No",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])


class WriteFiles(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="""What does <code>w</code> in the second argument of <code>open</code> do:  <code>open(path, "w")</code>?""",
            options={
                "It opens the file for writing": "Correct.",
                "It writes a w next to each line of the file": "Wrong, it opens the file for reading.",
            },
            correct_answer="It opens the file for writing",
            shuffle=True,
        )

        q2 = Question(
            question="What function do we use on a file object to write a list of strings line-by-line",
            options={
                "write": "Wrong, this function only writes a single string.",
                "writestrings": "Wrong, this function does not exist.",
                "writelines": "Correct.",
            },
            correct_answer="writelines",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])


class ContextManagers(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Do you need to call <code>close</code> on a file object when using a context manager?",
            options={
                "Yes": "Wrong! The context manager will handle the closing of a file when the context manager scope ends.",
                "No": "Correct! The context manager automatically calls close when leaving the scope.",
            },
            correct_answer="No",
            shuffle=True,
        )

        q2 = Question(
            question="What methods should an class implement to be used as a context manager?",
            options={
                "__enter__ and __exit__": "Correct! Any class implementing these methods can be used as a context manager.",
                "__start__ and __end__": "Wrong.",
                "__open__ and __close__": "Wrong.",
            },
            correct_answer="__enter__ and __exit__",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2])


class CSV(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Does the <code>csv</code> module automatically read the column names of a csv file?",
            options={
                "Yes": "Wrong! You are responsible for reading and storing the first line if the file has column names",
                "No": "Correct! You are responsible for reading and storing the first line if the file has column names.",
            },
            correct_answer="No",
            shuffle=True,
        )

        q2 = Question(
            question="What argument does the <code>writerow</code> function of a csv object take?",
            options={
                "Any iterable of values to write as the current csv row": "Correct!",
                "As many arguments as the columns of the csv": "Wrong",
                "None: the function does not exist": "Wrong",
            },
            correct_answer="Any iterable of values to write as the current csv row",
            shuffle=True,
        )

        q3 = Question(
            question="Does <code>csv.reader</code> interpret the values of a csv row as number, dates etc?",
            options={
                "Yes": "Wrong. By default it reads the current row and returns a list of strings.",
                "No": "Correct. By default it reads the current row and returns a list of strings",
            },
            correct_answer="No",
            shuffle=True,
        )
        super().__init__(questions=[q1, q2, q3])
