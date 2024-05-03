# FAQs for Python Training Course

## What will be the workshop schedule?

Each topic lasts 2 hours and includes a walk-through of the theoretical concepts, a hands-on session and Q&A. At the end of each day we will have 1 extra hour to answer additional questions.

## Which operating system should I use?

There is no specific requirement for the operating system. The training will be conducted on [binder](https://mybinder.org/) using Jupyter notebooks, which are browser-based, so an updated browser is the only requirement. Chrome-based or Firefox usually work better with Jupyter notebooks, but this is only a suggestion.

## Do I have to install any software beforehand?

There is no specific software that you have to install before the training. However, if you prefer having a local Python installation, you can do that.

## Is there a recommended Python installation?

If you plan to install Python locally, we recommend using Python 3.8 at the minimum. If possible, it's better to have Python 3.10 installed.

## Will the workshop cover the topic X?

The workshop will cover the fundamentals of the language, and the topics we will explore include:

Basic:
- Basic syntax and data types
- Control flow, loops, and exceptions
- Functions
- File handling
- Object-oriented programming
- Modules and packages

Advanced:
- Manage Python project
- Advanced functions
- Functional programming
- Advanced Object-oriented programming
- Parallelism and concurrency
- Libraries

## How do I test my solutions?

Each section contains a number of exercises for you to solve. The skeleton of the solution is already provided in the form of a function whose name starts with `solution_`. These cells are easy to spot because they look like this:

```python
%%ipytest functional_programming
def solution_exercise5(input_arg: list[str]) -> list[(str, int)]:
    """
    Write your solution here
    """
    pass
```

The first line `%%ipytest` tells IPython to run the cell in a special manner: instead of just running the cell, the cell is executed in a special environment that tests whether your solution is correct. Your function will automatically receive the needed input as shown by the signature. In this case, we know that the function will receive a list of strings called `input_arg`.

All you have to do is to work on your solution inside the function definition `solution_exercise5`. If you need to load modules or define other functions, you can do it in the same cell.
To avoid breaking the solution testing mechanism, **do not rename** the function and **do not remove the first line** from the cell.

To run the cell and test your solution, select it and press `Shift + Enter`  or the `Run cell` command of Jupyter. The output will tell you whether your solution is correct. If it is not, you will receive an error message along with the output of the failed tests.


## I have another question. Where should I ask?

For any other question you might have about the workshop, feel free to post a message in the `discussions` on GitHub.

If you come across any bug or have suggestions on how we could improve the content and exercises, feel free to open a new `issue`.

Here is the link to the tutorial's [official repository on GitHub](https://github.com/empa-scientific-it/python-tutorial).
