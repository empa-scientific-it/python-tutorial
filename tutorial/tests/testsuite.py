import io
from contextlib import redirect_stdout
from typing import Callable

import pytest
import ipynbname
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.display import HTML, display


class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        """Override the abstract `function_to_test` fixture function"""
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])


@pytest.fixture
def function_to_test():
    """Function to test, overriden at runtime by the cell magic"""


@magics_class
class TestMagic(Magics):
    """Class to add the test cell magic"""

    shell: InteractiveShell

    @cell_magic
    def test_functions_from_cell(self, line, cell):
        """The `%%test_functions_from_cell` magic"""
        # Get the path to the current notebook file
        notebook_name = ipynbname.name()

        # Run the cell through IPython
        self.shell.run_cell(cell)

        # Retrieve the names defined in the namespace
        # Only functions with names starting with `solution_` will be candidates for tests
        function_names = {}
        for name, function in self.shell.user_ns.items():
            if name.startswith("solution_") and callable(function):
                function_names[name.lstrip("solution_")] = function

        if not function_names:
            raise ValueError("No function to test defined in the cell")

        # Run the tests
        for name, function in function_names.items():
            with redirect_stdout(io.StringIO()) as pytest_stdout:
                result = pytest.main(
                    [
                        "-q",
                        f"tutorial/tests/test_{notebook_name}.py::test_{name}",
                    ],
                    plugins=[FunctionInjectionPlugin(function)],
                )

            # Read pytest output
            pytest_output = pytest_stdout.getvalue()

            if result == pytest.ExitCode.OK:
                color, title, test_result = (
                    "alert-success",
                    f"Tests <strong>PASSED</strong> for the function <code>{name}</code>",
                    "&#x1F64C Congratulations, your solution was correct!",
                )
            else:
                color, title, test_result = (
                    "alert-danger",
                    f"Tests <strong>FAILED</strong> for the function <code>{name}</code>",
                    "&#x1F631 Your solution was not correct!",
                )

                # Print all pytest output
                print(pytest_output)

            display(
                HTML(
                    f"""<div class="alert alert-box {color}"><h4>{title}</h4>{test_result}</div>"""
                )
            )


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    ipython.register_magics(TestMagic)
