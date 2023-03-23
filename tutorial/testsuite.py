import unittest
from typing import Any, Callable, List, Type

from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic, Magics, magics_class, line_magic, cell_magic, line_cell_magic, needs_local_scope)

from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)


class SubmissionTest(unittest.TestCase):

    def __init__(self, fun: Callable, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.fun = fun


    def runTest(self):
        self.assertEqual(1, 1)


def input_output_test(f: Callable):

    suite = unittest.TestSuite()
    case = SubmissionTest(f)
    suite.addTest(case)
    runner = unittest.TextTestRunner()
    def run(*args, **kwargs):
        runner.run(suite)
        return f(*args, **kwargs)
    return run



@input_output_test
def a():
    return 1




@magics_class
class MyMagics(Magics):

    @line_magic
    def lmagic(self, line):
        "my line magic"
        print("Full access to the main IPython object:", self.shell)
        print("Variables in the user namespace:",
              list(self.shell.user_ns.keys()))
        return line
    
    @needs_local_scope 
    @magic_arguments()
    @argument('test', type=str, help='An integer positional argument.')
    @argument('input', type=str, help='An integer positional argument.')
    @argument('output', type=str, help='An integer positional argument.')
    @cell_magic
    def celltest(self, line, cell, local_ns):
        args = parse_argstring(self.celltest, line)
        self.shell.run_cell(cell)
        self.shell.run_cell(args.input)
        self.shell.run_cell(args.output)
        result = self.shell.user_ns[args.test](self.shell.user_ns["input"])
        assert result == self.shell.user_ns["output"]
        return result

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
    magics = MyMagics(ipython)
    ipython.register_magics(magics)

