import io
import pathlib
import re
from contextlib import redirect_stdout
from typing import Callable, Dict

import ipynbname
import pytest
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.display import HTML, display


def _name_from_line(line: str = None):
    return line.strip().removesuffix(".py") if line else None


def _name_from_ipynbname() -> str | None:
    try:
        return ipynbname.name()
    except FileNotFoundError:
        return None


def _name_from_globals(globals_dict: Dict) -> str | None:
    module_path = globals_dict.get('__vsc_ipynb_file__') if globals_dict else None
    return pathlib.Path(module_path).stem if module_path else None


def get_module_name(line: str, globals_dict: Dict = None) -> str:
    """Fetch the test module name"""
    module_name = _name_from_line(line) or _name_from_ipynbname() or _name_from_globals(globals_dict)

    if not module_name:
        raise RuntimeError("Test module is undefined. Did you provide an argument to %%ipytest?")

    return module_name


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
    def ipytest(self, line: str, cell: str):
        """The `%%ipytest` cell magic"""
        # Get the module containing the test(s)
        module_name = get_module_name(line, self.shell.user_global_ns)

        # Check that the test module file exists
        module_file = pathlib.Path(f"tutorial/tests/test_{module_name}.py")
        if not module_file.exists():
            raise FileNotFoundError(f"Module file '{module_file}' does not exist")

        # Run the cell through IPython
        self.shell.run_cell(cell)

        # Retrieve the functions names defined in the current cell
        # Only functions with names starting with `solution_` will be candidates for tests
        functions_names = re.findall(r"^def\s+(solution_.*?)\s*\(", cell, re.M)

        # Get the functions objects from user namespace
        functions_to_run = {}
        for name, function in self.shell.user_ns.items():
            if name in functions_names and callable(function):
                functions_to_run[name.removeprefix("solution_")] = function

        if not functions_to_run:
            raise ValueError("No function to test defined in the cell")

        # Run the tests
        for name, function in functions_to_run.items():
            with redirect_stdout(io.StringIO()) as pytest_stdout:
                result = pytest.main(
                    [
                        "-q",
                        f"{module_file}::test_{name}",
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
