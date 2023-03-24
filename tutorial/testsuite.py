import unittest
from typing import Any, Callable, List, Type

from IPython.core import guarded_eval
from IPython.core.magic import (
    Magics,
    cell_magic,
    line_cell_magic,
    line_magic,
    magics_class,
    needs_local_scope,
)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring


class SubmissionTest(unittest.TestCase):
    """
    Base class for submission testing.
    To implement your problems just subclass this one
    and add your own test cases
    """

    def __init__(self, fun: Callable) -> None:
        super().__init__()
        self.fun = fun

    def test_one(self):
        self.assertEqual(self.fun(2), 1, msg="f(2) should return 1")


@magics_class
class TestMagic(Magics):
    """
    Implements a Ipython cell magic
    that can be used to automatically run a test case with class `TestCase` on the function `function_name` on cells
    marked with `%%celltest function_name TestCase`.
    For this to work, you need to import your test case in the notebook for the class to be available
    to the local notebook scope.
    """

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
        # Load the class by name by evaluating
        # its name in the notebook environment
        current_class = self.shell.run_cell(args.test).result
        # Run cell
        function_def = self.shell.run_cell(cell)
        # Extract the definition from the environment
        fun = self.shell.user_ns[args.fun]
        if fun is None:
            raise ValueError(f"There is no function called {fun} in the scope")
        # Setup test suite
        testcase = current_class(fun)
        print(testcase)
        # uite = unittest.TestSuite()
        suite = unittest.TestLoader().loadTestsFromTestCase(testcase)
        print(suite)
        runner = unittest.TextTestRunner()
        runner.run(suite)

    @line_cell_magic
    def lcmagic(self, line, cell=None):
        "Magic that works both as %lcmagic and as %%lcmagic"
        if cell is None:
            print("Called as line magic")
            return line
        else:
            print("Called as cell magic")
            return line, cell


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
