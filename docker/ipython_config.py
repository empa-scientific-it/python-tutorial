# Configuration file for ipython.
c = get_config()  # noqa # type: ignore

# Automatically load testsuite extension
c.InteractiveShellApp.extensions = ["tutorial.tests.testsuite"]

# Automatically import some modules
c.InteractiveShellApp.exec_lines = [
    "from typing import Any, ClassVar",
    "from collections.abc import List, Tuple, Callable, Dict",
]
