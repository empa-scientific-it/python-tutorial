# pylint: disable=missing-docstring, unused-argument, wrong-import-position, invalid-name, line-too-long
import html
import io
import re
import sys
import unittest
from importlib import import_module
from types import ModuleType
from typing import Callable, List, Type

from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import HTML, display


def find_class(namespace: ModuleType, name: str) -> Type:
    """
    Recursively find a class in a local namespace by name
    """

    def find_rec(current: dict, components: List[str]) -> Type:
        if len(components) == 1:
            return getattr(current, components[0])
        return find_rec(getattr(current, components[0]), components[1::])

    return find_rec(namespace, name.split("."))


class SubmissionTest(unittest.TestCase):
    """
    Base class for submission testing.
    To implement your problems just subclass this one
    and add your own test cases.
    If possible, do not override `__init__` and just add
    your test methods.
    """

    def __init__(
        self,
        fun: Callable,
        testName: str,
    ) -> None:
        super().__init__(testName)
        self.fun = self._suppress_output(fun)

    def setUp(self) -> None:
        self.original_stdout = sys.stdout

    def tearDown(self) -> None:
        sys.stdout = self.original_stdout

    def _suppress_output(self, fun: Callable) -> Callable:
        """Suppress a `fun` stdout when running tests"""

        def wrapper(*args, **kwargs):
            output = io.StringIO()
            sys.stdout = output
            result = fun(*args, **kwargs)
            sys.stdout = self.original_stdout

            return result

        return wrapper


def format_failures(result: unittest.TestResult) -> str:
    """Format results upon failures"""
    result_text = []
    for _, tb_string in result.failures:
        if match := re.search(r"([A-Za-z]+Error): (.+)", tb_string, re.MULTILINE):
            result_text.append(f"{match.group(1).strip()}: {match.group(2).strip()}")

    return (
        "<ul>\n"
        + "\n".join([f"<li>{html.escape(line)}</li>" for line in result_text])
        + "\n</ul>"
    )


@magics_class
class TestMagic(Magics):
    """
    Implements an IPython cell magic that can be used to automatically run a test case
    The test is defined by the class `TestCase` and applied to the function `function_name`
    on cells marked with `%%celltest function_name test_module.TestCase`
    """

    shell: InteractiveShell

    @magic_arguments()
    @argument("fun", type=str, help="The function to test in the following cell")
    @argument("test", type=str, help="The test case class")
    @cell_magic
    def celltest(self, line, cell):
        args = parse_argstring(self.celltest, line)

        # Find the class in the current module
        module_name, class_name = args.test.split(".")
        test_module = import_module(f"tests.{module_name}")
        test_class = getattr(test_module, class_name)

        # Run cell
        self.shell.run_cell(cell)

        # Extract the definition from the environment
        if (fun := self.shell.user_ns.get(args.fun)) is None:
            raise ValueError(f"There is no function called '{args.fun}' in the scope")

        # Load the test suite
        case_names = unittest.TestLoader().getTestCaseNames(test_class)
        suite = unittest.TestSuite([test_class(fun, name) for name in case_names])

        # Run the test suite and print results
        with io.StringIO() as stream:
            result = unittest.TextTestRunner(stream=stream).run(suite)

        if result.wasSuccessful():
            color, title, test_result = (
                "alert-success",
                "Tests <strong>PASSED</strong>",
                "&#x1F64C Congratulations, your solution was correct!",
            )
        else:
            color, title, test_result = (
                "alert-danger",
                "Tests <strong>FAILED</strong>",
                "&#x1F631 Your solution was not correct!\n" + format_failures(result),
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
