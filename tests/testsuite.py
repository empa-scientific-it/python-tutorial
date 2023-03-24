import io
import unittest
from types import ModuleType
from typing import Any, Callable, Dict, List, Type

from IPython.core import guarded_eval
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import (Magics, cell_magic, line_cell_magic,
                                line_magic, magics_class, needs_local_scope)
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.display import HTML, DisplayHandle, display


def find_class(ns: ModuleType, name: str) -> Type:
    """
    Recursively find a class in a local namespace by name
    """

    def find_rec(current: dict, components: List[str]) -> Type:
        if len(components) == 1:
            return getattr(current, components[0])
        elif len(components) > 1:
            module = getattr(current, components[0])
            return find_rec(module, components[1::])

    components = name.split(".")
    return find_rec(ns, components)


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
        self.fun = fun


def format_failures(result: unittest.TestResult) -> DisplayHandle:
    result_text = "\n".join([res for case, res in result.failures if res is not None])
    return display(
        HTML(
            f"""<font color=red>The solution is not correct, following tests failed:<div style="white-space:pre">{result_text}</div></font>"""
        )
    )


@magics_class
class TestMagic(Magics):
    """
    Implements a Ipython cell magic
    that can be used to automatically run a test case with class `TestCase` on the function `function_name` on cells
    marked with `%%celltest function_name TestCase`.
    For this to work, you need to import your test case in the notebook for the class to be available
    to the local notebook scope.
    """

    shell: InteractiveShell

    @line_magic
    def lmagic(self, line):
        return line

    @needs_local_scope
    @magic_arguments()
    @argument("fun", type=str, help="The function to test in the following cell")
    @argument("test", type=str, help="The test case class")
    @cell_magic
    def celltest(self, line, cell, local_ns):
        args = parse_argstring(self.celltest, line)
        # Find the class in the current module
        test_class = find_class(self.shell.user_module, args.test)
        # Run cell
        function_def = self.shell.ex(cell)
        # Extract the definition from the environment
        fun = self.shell.user_ns[args.fun]
        if fun is None:
            raise ValueError(f"There is no function called {fun} in the scope")
        # #Load the test suite
        case_names = unittest.TestLoader().getTestCaseNames(test_class)
        cases = [test_class(fun, name) for name in case_names]
        suite = unittest.TestSuite(cases)
        with io.StringIO() as stream:
            runner = unittest.TextTestRunner(stream=stream)
            result = runner.run(suite)
        if result.wasSuccessful():
            return display(
                HTML(
                    "<font color=green>Congratulations, your solution was correct</font>"
                )
            )
        else:
            return format_failures(result)




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
