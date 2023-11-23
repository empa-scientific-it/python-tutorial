"""A module to define the `%%ipytest` cell magic"""
import io
import pathlib
import re
from contextlib import redirect_stderr, redirect_stdout
from multiprocessing import Process, Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, Optional, Callable

from dataclasses import dataclass

import ipynbname
import pytest
from pytest import ExitCode
from IPython.core.display import Javascript
from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import display

from .testsuite_helpers import (
    AstParser,
    FunctionInjectionPlugin,
    FunctionNotFoundError,
    InstanceNotFoundError,
    ResultCollector,
    TestResultOutput,
    TestExecutionResult
)


def _name_from_line(line: str = ""):
    return line.strip().removesuffix(".py") if line else None


def _name_from_ipynbname() -> str | None:
    try:
        return ipynbname.name()
    except FileNotFoundError:
        return None


def _name_from_globals(globals_dict: Dict) -> str | None:
    """Find the name of the test module from the globals dictionary if working in VSCode"""

    module_path = globals_dict.get("__vsc_ipynb_file__") if globals_dict else None
    return pathlib.Path(module_path).stem if module_path else None


def get_module_name(line: str, globals_dict: Dict) -> str:
    """Fetch the test module name"""

    module_name = (
        _name_from_line(line)
        or _name_from_ipynbname()
        or _name_from_globals(globals_dict)
    )

    if not module_name:
        raise ModuleNotFoundError(module_name)

    return module_name



def run_test(module_name: str, function_name: str, function_to_test: Callable, q: Queue) -> TestExecutionResult:
    rc = ResultCollector()
    with redirect_stderr(io.StringIO()) as pytest_stderr, redirect_stdout(
        io.StringIO()
    ) as pytest_stdout:
        test_name = f"test_{function_name}"
        result = pytest.main(
            [
                "-q",
                f"tutorial/tests/test_{module_name}.py::{test_name}",
            ],
            plugins=[rc, FunctionInjectionPlugin(function_to_test)],
        )


    res = TestExecutionResult(
        pytest_stdout.getvalue(),
        pytest_stderr.getvalue(),
        test_name,
        result == ExitCode.OK,
        result == ExitCode.INTERNAL_ERROR,
        list(rc.tests.values()))
    q.put(res)
    return res


@magics_class
class TestMagic(Magics):
    """Class to add the test cell magic"""

    shell: Optional[InteractiveShell]  # type: ignore
    cells: Dict[str, int] = {}

    @cell_magic
    def ipytest(self, line: str, cell: str):
        """The `%%ipytest` cell magic"""
        # Check that the magic is called from a notebook
        if not self.shell:
            raise InstanceNotFoundError("InteractiveShell")

        # Get the module containing the test(s)
        module_name = get_module_name(line, self.shell.user_global_ns)

        # Check that the test module file exists
        module_file = pathlib.Path(f"tutorial/tests/test_{module_name}.py")
        if not module_file.exists():
            raise FileNotFoundError(f"Module file '{module_file}' does not exist")

        # Run the cell through IPython
        result = self.shell.run_cell(cell)

        try:
            result.raise_error()

            # Retrieve the functions names defined in the current cell
            # Only functions with names starting with `solution_` will be candidates for tests
            functions_names = re.findall(r"^def\s+(solution_.*?)\s*\(", cell, re.M)

            # Get the functions objects from user namespace
            functions_to_run = {}
            for name, function in self.shell.user_ns.items():
                if name in functions_names and callable(function):
                    functions_to_run[name.removeprefix("solution_")] = function

            if not functions_to_run:
                raise FunctionNotFoundError

            # Store execution count information for each cell
            if (ipython := get_ipython()) is None:
                raise InstanceNotFoundError("IPython")

            cell_id = ipython.parent_header["metadata"]["cellId"]
            if cell_id in self.cells:
                self.cells[cell_id] += 1
            else:
                self.cells[cell_id] = 1

            # Parse the AST tree of the file containing the test functions,
            # to extract and store all information of function definitions and imports
            ast_parser = AstParser(module_file)

            outputs = []
            for name, function in functions_to_run.items():
                #Create the queue to store the result
                q = Queue()
                # Run the tests
                p = Process(target=run_test, args=(module_name, name, function, q))
                p.start()
                p.join()
                #Get the result
                res = q.get()
                # reset execution count on success
                if res.success:
                    self.cells[cell_id] = 0
                outputs.append(
                    TestResultOutput(
                        res.test_result,
                        res.test_name,
                        res.syntax_error,
                        res.success,
                        self.cells[cell_id],
                        ast_parser.get_solution_code(name),
                    )
                )

            display(*outputs)

            # hide cell outputs that were not generated by a function
            display(
                Javascript(
                    """
                        var output_divs = document.querySelectorAll(".jp-OutputArea-executeResult");
                        for (let div of output_divs) {
                            div.setAttribute("style", "display: none;");
                        }
                    """
                )
            )

        except SyntaxError:
            # Catches syntax errors
            display(
                TestResultOutput(
                    syntax_error=True,
                    success=False,
                )
            )


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """

    ipython.register_magics(TestMagic)


