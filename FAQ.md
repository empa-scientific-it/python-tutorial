# FAQs for Python Training Course

## What will be the workshop schedule?

Each tutorial session lasts 4 half-days, from 9:00 to 13:00 (breaks included). During one afternoon, a one hour and a half will be dedicated to the extra session on Linux & Gitlab.

## Which operating system should I use?

There is no specific requirement for the operating system. The training will be conducted on [binder](https://mybinder.org/) using Jupyter notebooks, which are browser-based, so an updated browser is the only requirement. Chrome-based or Firefox usually work better with Jupyter notebooks, but this is only a suggestion.

## Do I have to install any software beforehand?

There is no specific software that you have to install before the training. However, if you prefer having a local Python installation, you can do that.

## Is there a recommended Python installation?

If you plan to install Python locally, we recommend using Python 3.8 at the minimum. If possible, it's better to have Python 3.10 installed. If you need help, please check out the `#help` channel on Slack and feel free to ask for support.

## Will the workshop cover the topic X?

The workshop will cover the fundamentals of the language, and the topics we will explore include:

- Basic syntax and data types
- Control flow, loops, and exceptions
- Functions
- File handling
- Functional programming
- Object-oriented programming
- Modules and packages

We have created dedicated channels on Slack for each topic.

Due to time constraints, we couldn't fit all the requests, and we will mainly focus on the fundamentals of the language. However, you will see some practical use cases during the exercise sessions. If you have any questions or are interested in a specific topic that is not covered in the workshop, you can open a discussion on the `#extra` channel on Slack.

## I have another question. Where should I ask?

For any other question you might have about the workshop, feel free to post a message in the `#help` channel on Slack.

A couple of things worth reminding about Slack:

1. Do a quick search in the channel before posting. It might be that someone already started a discussion on the same topic.
2. **Always** reply within [threads](https://slack.com/help/articles/115000769927-Use-threads-to-organize-discussions-) (or open a new one) when you want to join a conversation. The [purpose](https://slack.com/resources/using-slack/tips-on-how-best-to-use-threaded-messages) is to avoid too many unrelated messages that are difficult to navigate in the long run.

For a few more tips about using Slack effectively, check out [this link](https://slack.com/blog/collaboration/etiquette-tips-in-slack).

## How do I test my solutions?

Each section contains a number of exercises for you to solve. The skeleton of the solution is already provided in the form of a function having the name `solution_exercise*`. These cells are easy to spot because they look like this:

```ipython
%%ipytest functional_programming
def solution_exercise5(w: list[str]) -> list[(str, int)]:
    """
    Write your solution here
    """
    pass

```

the first line `%%ipytest` tells IPython to run the cell in a special manner: instead of just running the cell, the cell is executed in a special environment
where a test verifies if your solution is correct. Your function will automatically receive the needed input as shown by the signature. In this case, we    know that the function will receive a list of strings called `w`,

All you have to do is to work on your solution inside of the function definition `solution_exercise5`. If you need to load modules or define helper functions, you can do it in the same cell.
To avoid breaking the solution testing mechanism, **DO NOT** rename the function and **DO NOT** remove the first line from the cell.

To run the cell and test your solution, select it and press `CTRL + enter` or the `run cell` command of Jupyter. If your solution is correct, you will receive a congratulations message, if it is not, you will receive an error message along with the output of the failed tests.