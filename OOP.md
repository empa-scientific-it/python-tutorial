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

# Object-oriented Programming


## References

```python

```

## Exercises

<!-- #region tags=[] -->
### Undefined exercise 🌶️
<!-- #endregion -->

Should the easiest of the three...

<!-- #region tags=[] -->
### Intcode computer 🌶️🌶️
<!-- #endregion -->

An **Intcode program** is a list of integers separated by commas (e.g. `1, 0, 0, 3, 99`). The first number is called "position `0`". Each number represents either an **opcode** or a **position**.

An opcode indicates what to do and it's either `1`, `2`, or `99`. The meaning of each opcode is the following:

1. `99` means that the program should immediately terminate. No instruction will be executed after encountering this opcode;

2. `1` **adds** together numbers read from **two positions** and stores the result in a **third position**. The three integers **immediately after** the opcode indicates these three positions. For example, the Intcode program `1,10,20,30` should be executed as: read the values at positions `10` and `20`, add those values, and the overwrite the value at position `30`.

3. `2` works exactly like opcode `1`, but it **multiplies** the two inputs instead of adding them. Again, the three integers following the opcode indicates **where** the inputs and outputs are, not their **values**

Finally, when the program is done with an opcode, it moves to the next one by stepping **forward 4 positions**.

For example, consider the following program

```
1,9,10,3,2,3,11,0,99,30,40,50
```

which can be splitted into multiple lines to indicate the 4 instructions (opcodes):

```
1,9,10,3,
2,3,11,0,
99,
30,40,50
```

The first line represents the **sum** (opcode `1`) of the values stored at positions `9` (that is `30`) and `10` (that is `40`). The result (`70`) is then stored at position `3`. Afterward, the program becomes:

```
1,9,10,70,
2,3,11,0,
99,
30,40,50
```

Stepping forward by 4 positions, we end up on the second line, which represents a **multiplication** operation (opcode `2`). Take the values at positions `3` and `11`, multiply them, and save the result at position `0`. You obtain:

```
3500,9,10,70,
2,3,11,0,
99,
30,40,50
```

Your input program is the following string

```python
intcode_program = "1,12,2,3,1,1,2,3,1,3,4,3,1,5,0,3,2,13,1,19,1,9,19,23,2,23,13,27,1,27,9,31,2,31,6,35,1,5,35,39,1,10,39,43,2,43,6,47,1,10,47,51,2,6,51,55,1,5,55,59,1,59,9,63,1,13,63,67,2,6,67,71,1,5,71,75,2,6,75,79,2,79,6,83,1,13,83,87,1,9,87,91,1,9,91,95,1,5,95,99,1,5,99,103,2,13,103,107,1,6,107,111,1,9,111,115,2,6,115,119,1,13,119,123,1,123,6,127,1,127,5,131,2,10,131,135,2,135,10,139,1,13,139,143,1,10,143,147,1,2,147,151,1,6,151,0,99,2,14,0,0"
```

<div class="alert alert-block alert-warning">
<b>Question:</b> What value is left at position <code>0</code> after the program stops?
</div>


Here are the initial and final states of a few small programs:

- `1,0,0,0,99` becomes `2,0,0,0,99`, so the value at `0` is `2`
- `2,3,0,3,99` becomes `2,3,0,6,99` (value at `0` is `2`)
- `1,1,1,4,99,5,6,0,99` becomes `30,1,1,4,2,5,6,0,99` (value at `0` is `30`)


<div class="alert alert-block alert-info">
<b>Hint:</b> Write a Python class called <code>Computer</code> with a method called <code>run()</code>. <br>The class <code>__init__()</code> method should process your input string and assign the attribute <code>program</code>, which should be a <b>list</b> of integers. 
</div>


<div class="alert alert-block alert-info">
    <b>Hint:</b> Make sure that your Intcode computer <b>correctly</b> returns the above test programs.
</div>

<!-- #region tags=[] -->
### The N-body problem 🌶️🌶️🌶️🌶️
<!-- #endregion -->
