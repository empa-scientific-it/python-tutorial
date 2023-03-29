import io
import sys
from typing import Callable
import importlib

import pytest
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import HTML, display

# class SubmissionTest(unittest.TestCase):
#     """
#     Base class for submission testing.
#     To implement your problems just subclass this one
#     and add your own test cases.
#     If possible, do not override `__init__` and just add
#     your test methods.
#     """

#     def __init__(
#         self,
#         fun: Callable,
#         testName: str,
#     ) -> None:
#         super().__init__(testName)
#         self.fun = self._suppress_output(fun)

#     def setUp(self) -> None:
#         self.original_stdout = sys.stdout

#     def tearDown(self) -> None:
#         sys.stdout = self.original_stdout

#     def _suppress_output(self, fun: Callable) -> Callable:
#         """Suppress a `fun` stdout when running tests"""

#         def wrapper(*args, **kwargs):
#             output = io.StringIO()
#             sys.stdout = output
#             result = fun(*args, **kwargs)
#             sys.stdout = self.original_stdout

#             return result

#         return wrapper


# def format_failures(result: unittest.TestResult) -> str:
#     """Format results upon failures"""
#     result_text = []
#     for _, tb_string in result.failures:
#         if match := re.search(r"([A-Za-z]+Error): (.+)", tb_string, re.MULTILINE):
#             result_text.append(f"{match.group(1).strip()}: {match.group(2).strip()}")

#     return (
#         "<ul>\n"
#         + "\n".join([f"<li>{html.escape(line)}</li>" for line in result_text])
#         + "\n</ul>"
#     )


class FunctionInjectionPlugin:
    """A class to inject a generic test function"""

    def __init__(self, func_to_test: Callable) -> None:
        self.func_to_test = func_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        if "func_to_test" in metafunc.fixturenames:
            metafunc.parametrize("func_to_test", [self.func_to_test])


@magics_class
class TestMagic(Magics):
    """
    Implements an IPython cell magic that can be used to automatically run a test case
    The test is defined by the class `TestCase` and applied to the function `function_name`
    on cells marked with `%%celltest function_name test_module.TestCase`
    """

    shell: InteractiveShell

    @magic_arguments()
    @argument(
        "test_function", type=str, help="The function to test in the following cell"
    )
    @argument("test", type=str, help="The test case class")
    @cell_magic
    def pytest_cell(self, line, cell) -> None:
        # Parse magic's arguments
        args = parse_argstring(self.pytest_cell, line)

        # Save current stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Run cell
        self.shell.run_cell(cell)

        # Extract the function definition from the environment
        if (test_function := self.shell.user_ns.get(args.test_function)) is None:
            raise ValueError(
                f"There is no function called '{args.test_function}' in the scope"
            )

        # Import the module
        test_module = importlib.import_module(f"tests.{args.test}")

        # Run the test
        result = pytest.main(
            ["-q", f"tests/{args.test}.py"],
            plugins=[FunctionInjectionPlugin(test_function)],
        )

        # Restore stdout
        sys.stdout.seek(0)
        pytest_output = sys.stdout.read()
        sys.stdout = old_stdout

        if result == pytest.ExitCode.OK:
            color, title, test_result = (
                "alert-success",
                "Tests <strong>PASSED</strong>",
                "&#x1F64C Congratulations, your solution was correct!",
            )
        else:
            color, title, test_result = (
                "alert-danger",
                "Tests <strong>FAILED</strong>",
                f"&#x1F631 Your solution was not correct!\n{pytest_output}",
            )

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
    # This class must then be registered with a manually created instance,
    # since its constructor has different arguments from the default:
    magics = TestMagic(ipython)
    ipython.register_magics(magics)
