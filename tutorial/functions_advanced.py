from markdown import markdown

from .common import Spoiler

tricky_closures = Spoiler(
    "Answer",
    markdown(
        "Look at the definition of `op()`. Does it reference the variable `n` other than in setting the default value of `n`? **No**. "
        "Hence, the variable `n` is **not** a free variable, and the function `op()` is **not** a closure, just a plain function."
    ),
)
