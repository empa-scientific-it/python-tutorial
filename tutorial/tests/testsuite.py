import io
from typing import Callable
from contextlib import redirect_stdout

import pytest
import ipynbname
from IPython.core.magic import register_cell_magic
from IPython.display import HTML, display

class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        """Override the abstract `function_to_test` fixture function"""
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])


@register_cell_magic
def test_functions_from_cell(line, cell):
    # Execute the cell code in a new namespace

    # Get the path to the current notebook file
    nbname = ipynbname.name()

    local_ns = {}
    exec(cell, local_ns)

    # Retrieve the names defined in the namespace
    function_names = [name for name in local_ns if callable(local_ns[name])]

    if not function_names:
        raise ValueError("No function defined in the cell")
    
    # Run the test
    for function_to_test in function_names:
        with redirect_stdout(io.StringIO()) as pytest_stdout:
            result = pytest.main(
                ["-q", f"tutorial/tests/test_example.py::test_{function_to_test}"],
                plugins=[FunctionInjectionPlugin(local_ns[function_to_test])],
            )    
        # Read pytest output
        pytest_output = pytest_stdout.getvalue()

        if result == pytest.ExitCode.OK:
            color, title, test_result = (
                "alert-success",
                f"Tests <strong>PASSED</strong> for function <code>{function_to_test}</code>",
                "&#x1F64C Congratulations, your solution was correct!",
            )
        else:
            color, title, test_result = (
                "alert-danger",
                f"Tests <strong>FAILED</strong> for function <code>{function_to_test}</code>",
                "&#x1F631 Your solution was not correct!",
            )

            # Print all pytest output
            print(pytest_output)

            # Print only a summary
            # lines = pytest_output.split("\n")
            # summary_start = next(
            #     i for i, line in enumerate(lines) if "short test summary info" in line
            # )
            # print(f"{lines[0]}\n" + "\n".join(lines[summary_start:]))

        display(
            HTML(
                f"""<div class="alert alert-box {color}"><h4>{title}</h4>{test_result}</div>"""
            )
        )

