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

# Control flow


## References


Links


## Conditionals: `if`, `elif`, `else`


## The `while` loop


## Altering loops with `break` and `continue`


## The `try...except` block


## The `for` loop


In Python, an **iterable** is an **object** capable of returning its members one at a time. It's not stricly a "container" or a "collection", like lists or tuples. It's an object with this particular property. We can also create custom objects that can become iterable.

Many objects in Python are iterable: lists, strings, `range()` objects, file objects and many more.

The main purpose of the `for` keyword is to access all the elements of an iterable.

<!-- #region -->
In other languages (C++, Java or JavaScript), a `for` loop is more similar to `while` in Python. For example, the C++ loop

```cpp
for (unsigned int i = 0; i < 10; ++i) {
    std::cout << i << std::endl;
}
```

could be translated to Python with

```python
i = 0
while i < 10:
    print(i)
    i += 1 # remember: Python does not have the prefix/postfix increment (++) operator
```

The only substantial difference with the C++ code is that the looping variable `i` is automatically discarded when the loop is over. In Python, `i` will retain the **last value** that was assigned inside the `while` body. We could do something like `i = None`, but it turns out that's not necessary.

<!-- #endregion -->

```python

```
