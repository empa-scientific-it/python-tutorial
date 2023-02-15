---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

<!-- #region tags=[] -->
# Functions
<!-- #endregion -->

<!-- #region tags=[] -->
## References
<!-- #endregion -->

Additional materials where you can find more details about writing functions in Python. For each link, it's indicated if it's a video, a text, or a practical resource.

- [Python For Everybody: Functions](https://www.py4e.com/lessons/functions) (video)
- [Python For Everybody: Functions examples](https://www.py4e.com/html3/04-functions) (text)


---


Every programmer knows that splitting the work to be done in smaller pieces isn't only a good problem-solving technique, but it also makes your code more readable, easier to understand, and more efficient (or at least it will be easier to make it so). **Functions** are the fundamental building block to achieve this.


1. Functions in Python are blocks of reusable code that perform a specific task.
2. They allow you to break down complex programs into smaller and manageable parts.
3. Functions make your code easier to read and maintain because you can encapsulate logic into self-contained blocks and reuse them throughout your program. When you have to perform the same task multiple times, instead of repeating the code, you can simply call the function.
4. Best practices for writing functions (we will see more in detail later on):
    1. Giving descriptive names
    2. Keeping them small and focused on a single task
    3. Using clear and concise documentation (also known as docstrings)
    4. Explaining the required (and optional) inputs and outputs

<!-- #region tags=[] -->
## Anatomy of a function
<!-- #endregion -->

<!-- #region -->
A function in Python has three main parts: signature, body, and docstrings.

**Signature**: The signature of a function includes the function name, the input parameters (if any), and the return statement (if any). The Python keyword to indicate that a name is a function's name is `def`, and it's a **reserved keyword** (you cannot call a variable or any other object with that name). The signature is what allows you to call the function and pass it arguments. For example:

```python
def multiply(x, y):
```

You have the keyword `def`, the function's name, and its parameters in parentheses. The semi-colon tells Python that what comes next is the function's body.
<!-- #endregion -->

**Body**: The body of a function contains the statements that the function executes when it is called. These statements perform the task that the function was created to perform. For example:

<!-- #region -->
```python
def multiply(x, y):
    product = x * y
    return product
```
<!-- #endregion -->

The function's outputs are indicated by the (reserved) keyword `return`. All functions in Python return a value, even if that value is `None`. If you omit the `return` keyword, Python assumes that the function returns `None`.


**Docstrings**: Docstrings are string literals that appear as the first statement in a function. They provide documentation for the function, explaining what it does and how it works. Docstrings are surrounded by triple quotes ("""). For example:

<!-- #region -->
```python
def multiply(x, y):
    """This function calculates the product of two numbers"""
    product = x * y
    return product
```
<!-- #endregion -->

A few more examples of simple functions:

<!-- #region -->
```python
def greet(name):
    """This function greets the person passed in as a parameter"""
    return "Hello, " + name

def add(a, b):
    """This function returns the sum of two numbers"""
    return a + b

def is_even(number):
    """This function returns True if the number is even, False otherwise"""
    return number % 2 == 0

```
<!-- #endregion -->

<!-- #region tags=[] -->
## Parameters and arguments
<!-- #endregion -->

The terms "parameters" and "arguments" are often used interchangeably, but they refer to different things in the context of function calls.

1. **Parameters** are the names that are used in the function definition to accept values passed to the function. For example:

<!-- #region -->
```python
def greet(name):
    """This function greets the person passed in as a parameter"""
    return "Hello, " + name
```

Here `name` is a parameter.

2. **Arguments**: are the actual values that are passed to the function when it is called.

```python
greet("John")
# "Hello, John"
```

Here the literal string `"John"` is the argument.
<!-- #endregion -->

<!-- #region -->
In Python, there are two ways to pass arguments to a function: positional arguments and keyword arguments.

1. **Positional arguments** are arguments that are passed to the function in the same order as the parameters. For example:

```python
def add(a, b):
    """This function returns the sum of two numbers"""
    return a + b

add(1, 2)
```

Here, `1` and `2` are positional arguments that are passed to the `add` function.

2. **Keyword arguments** are arguments that are passed to the function using the name of the parameter followed by an equal sign and the value. For example:

```python
def greet(name):
    """This function greets the person passed in as a parameter"""
    return "Hello, " + name

greet(name="John")
```

Here, `name="John"` is a keyword argument that is passed to the greet function. Keyword arguments make the function call more readable and can be useful when the order of the parameters is not important.

Another important use of the keyword syntax (the `=` sign) is to define **parameters with default values**. For example:

```python
def greet(name="my friend"):
    """This function greets the person passed in as a parameter"""
    return "Hello, " + name
```

Calling `greet` without any arguments, tells Python to use the default value. Therefore, `greet()` will return `"Hello, my friend"`. Let's run this code for real!
<!-- #endregion -->

```python tags=[]
def greet(name="my friend"):
    """This function greets the person passed in as a parameter"""
    return "Hello, " + name

print(greet())

print(greet("John"))
```

<!-- #region tags=[] -->
## How Python executes a function
<!-- #endregion -->

This sentence may seem another trivial one: to execute a function, you must **call it**. In Python, it means using the `function_name()` with **parentheses**, enclosing any argument if need be.

When you call a function in Python, three things happen: calling, executing, and returning.

1. **Calling**: When you call a function, Python creates a new function call frame on the call stack. A function call frame contains information about the function call, such as the function name, arguments, local variables, and the return address (i.e., where to return control when the function returns). The function call frame is pushed onto the top of the call stack.

2. **Executing**: After the function call frame is created, control is transferred to the function body. The function body is executed from top to bottom, line by line. The function can access its parameters, declare local variables, and perform any other operations specified in the body. The function can call other functions, which will create their own function call frames and push them onto the call stack.

3. **Returning**: When the function reaches the end of the body or encounters a return statement, the function returns control to the calling code. The function call frame is popped from the call stack, and any local variables and parameters are discarded. The function returns a value if specified in the return statement, otherwise it returns `None` (remember: every function in Python returns **at least** `None`)

This process repeats every time a function is called, and the call stack grows and shrinks as functions are called and return. This allows Python to keep track of the execution context and return control to the correct location when a function returns.



## The scope of a function

<!-- #region -->
The following might seem like a trivial question: could we assign the same variable name two different values?

The obvious (and right) answer is **no**. If `x` is `3` and `2` at the same time, how should Python evaluate `x + 2`? There is, however, a workaround to this and it involves the concept of **scope**. While you don't *use* the scope to have a variable with two values at the same time (it doesn't make sense!), it's important to understand it to avoid bugs or serious debug nightmares.

Look at the following lines of valid Python code:

```python
x = "Hello World"

def func():
    x = 2
    return f"Inside 'func', x has the value {x}")

print(func())
print(f"Outside 'func', x has the value {x}")
```

What output do you expect?

Does `x` really have two simultaneous values? **Not really:** the exact reason is that `x` **within the function's body** and `x` **in the outside code** live in two separates **scopes**. The function body has a **local scope**, while all the code outside (contained in `main.py`) is the **global scope**.
<!-- #endregion -->

We can define the "scope" as **the region of a program where a name has a meaning**. In other words, scoping determines the accessibility of variables in different parts of a program. There are three levels of scope in Python:

1. **Global scope**: Variables declared at the top level of a program or module are in the global scope. They are accessible from anywhere in the program or module.

2. **Local scope**: Variables declared inside a function are in the local scope. They are only accessible from within the function and are discarded when the function returns.

3. **Non-local scope**: Variables declared inside a nested function are in the non-local scope. They are accessible from the outer function and from within the nested function.


Here's an example to illustrate the different scopes:

```python tags=[]
# Global scope
x = 10

def outer_function():
    # Local scope
    y = 20

    def inner_function():
        # Non-local scope
        nonlocal y
        y = 30
        z = 40
        print("Inner function:", x, y, z)

    inner_function()
    print("Outer function:", x, y)

outer_function()
print("Global scope:", x)
```

In this example, `x` is a global variable and is accessible from anywhere in the program. `y` is a local variable to the `outer_function`, and is accessible from within the `outer_function` and from the `inner_function`. `z` is a local variable to the `inner_function` and is **only** accessible from within the `inner_function`.

The `nonlocal` keyword is used to access a variable in the **nearest enclosing scope that is not global**. In the example above, the `inner_function` uses `nonlocal y` to access the `y` variable in the `outer_function` and modify its value. If `nonlocal` was not used, a new local `y` variable would be created in the `inner_function`.

The `global` keyword is used to access a global variable and modify its value from within a function. For example:

```python
# Global scope
x = 10

def modify_x():
    global x
    x = 20

modify_x()
print("Global scope:", x)
```

Even though you can access and modify variables from different scope, it's not considered a good practice. When a function makes use of `global` or `nonlocal`, or when modifying a mutable type in-place, it's like when a function modifies its own arguments. It's a **side-effect** that should be generally avoided. It's is considered a much better programming practice to make use of a function's return values instead of resorting to the scoping keywords.


---


## Practicals

<!-- #region tags=[] -->
### Longest consecutive sequence 🌶️🌶️
<!-- #endregion -->

Given an **unsorted** set of $N$ random integers, write a function that returns the length of the longest consecutive sequence of integers.

- Example 1: given the list `nums = [100, 4, 200, 1, 3, 2]`, the longest sequence is `[1, 2, 3, 4]` of length *4*.

- Example 2: given the list `nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]`, the longest sequence contains all the numbers from 0 to 8, so its length is **9**.

```python
def longest_sequence(numbers: list):
    """Function"""
    # Write your solution here
    return None
```

```python
longest_sequence_test(longest_sequence)
```

<!-- #region tags=[] -->
### Password validator
<!-- #endregion -->

<!-- #region tags=[] -->
#### Part 1 🌶️
<!-- #endregion -->

You have a range of numbers `136760-595730` and need to count how many valid password are there. A valid password must meet **all** the following criteria:

- It is a six-digit number
- Two adjacent digits are the same (like `22` in `122345`)
- Going from left to right, the digits **never decrease**; they only ever increase or stay the same (like 111123 or 135679)

For example, the following are true:

- `111111` meets these criteria (double `11`, never decreases)
- `223450` does **not** meet these criteria (`50` is a decreasing pair of digits)
- `123789` does **not** meet these criteria (no double digit)

Write a function named `count_valid()` that returns the number of valid password in your range.

<!-- #region tags=[] -->
#### Part 2 🌶️🌶️
<!-- #endregion -->

You have a new rule: the two adjacent matching digits **must not be part of a larger group of matching digits**. For example:

- `112233` meets these criteria because the digits never decrease and all repeated digits are exactly two digits long
- `123444` **doesn't** meet the criteria (the repeated `44` is part of a larger group of `444`)
- `111122` meets the criteria (even though `1` is repeated more than twice, it still contains a double `22`)

How could you modify/extend your `count_valid()` function to return the correct number of valid passwords including this last rule?

<!-- #region tags=[] -->
### Buckets reorganization
<!-- #endregion -->

#### Part 1 🌶️


You have a list of buckets, each containing some items labelel from `a` to `z`, or from `A` to `Z`. Each bucket has two large compartments, and each compartment always has the same number of items.

For example, in the following list of buckets

```
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
```

- The first bucket contains `vJrwpWtwJgWrhcsFMMfFFhFp`, which means its first compartment contains the items `vJrwpWtwJgWr`, while the second compartment contains the items `hcsFMMfFFhFp`. The only item type that appears in both compartments is `p`.
- The third bucket's compartments contain `PmmdzqPrV` and `vPwwTWBwg`; the only common item type is `P`.
- The sixth bucket's compartments only share item type `s`.

Each item has also a priority:

- Items types `a` through `z` have priorities 1 through 26
- Items types `A` through `Z` have priorities 27 through 52

Write a function that returns the priority of the item type that appears in **both compartments**.

<div class="alert alert-block alert-warning">
<b>Question:</b> What is the sum of the priorities of those item types?
</div>

In the above example, the priority of the item that appears in both compartments of each bucket is 16 (`p`), 38 (`L`), 42 (`P`), 22 (`v`), 20 (`t`), and 19 (`s`); the sum of these is **157**.


#### Part 2 🌶️🌶️


You are told that you should not care about the priority of **every item**, but only of a "special item" that is common to groups of **three buckets**. Every set of three lines correspond to a single group, and each group can have a different special item – that is, an item with a different letter.

Considering once again the above example, in the first three lines:

```
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
```
The only item that appears in **all** three buckets is `r` (priority 18). This must be the "special item". If you consider the second group of three, the special item is of type `Z` (priority 52). The sum is `18 + 52 = 70`.

<div class="alert alert-block alert-warning">
<b>Question:</b> What is the sum of the priorities of all the special items?
</div>

```python

```
