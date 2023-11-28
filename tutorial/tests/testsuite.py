"""A module to define the `%%ipytest` cell magic"""
import io
import pathlib
import re
from contextlib import redirect_stderr, redirect_stdout
from typing import Dict, List, Optional

import ipynbname
import pytest
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class

from .ast_parser import AstParser
from .testsuite_helpers import (
    FunctionInjectionPlugin,
    FunctionNotFoundError,
    InstanceNotFoundError,
    IPytestOutcome,
    IPytestResult,
    ResultCollector,
    TestCaseResult,
    TestResultOutput,
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


@magics_class
class TestMagic(Magics):
    """Class to add the test cell magic"""

    def __init__(self, shell):
        super().__init__(shell)
        self.max_execution_count = 3
        self.shell: InteractiveShell = shell
        self.module_file: Optional[pathlib.Path] = None
        self.module_name: Optional[str] = None
        self.ast_parser: Optional[AstParser] = None

        # This is monkey-patching suppress printing any exception or traceback
        self.shell._showtraceback = lambda *args, **kwargs: None

    def run_cell(self, cell: str) -> IPytestResult:
        # The IPytestResult object to return
        ipytest_result = IPytestResult()

        # Run the cell through IPython
        try:
            result = self.shell.run_cell(cell, silent=True)  # type: ignore
            result.raise_error()
        except Exception as err:
            return IPytestResult(
                status=IPytestOutcome.SYNTAX_ERROR,
                exceptions=[err],
            )

        # Retrieve the functions names defined in the current cell
        # Only functions with names starting with `solution_` will be candidates for tests
        functions_names = re.findall(r"^def\s+(solution_.*?)\s*\(", cell, re.M)

        # Get the functions objects from user namespace
        functions_to_run = {}
        for name, function in self.shell.user_ns.items():  # type: ignore
            if name in functions_names and callable(function):
                functions_to_run[name.removeprefix("solution_")] = function

        if not functions_to_run:
            return IPytestResult(
                status=IPytestOutcome.SOLUTION_FUNCTION_MISSING,
                exceptions=[FunctionNotFoundError()],
            )

        # Store execution count information for each cell
        cell_id = self.shell.parent_header["metadata"]["cellId"]  # type: ignore
        ipytest_result.cell_execution_count[cell_id] += 1

        # Run the tests for each function
        outputs: List[TestCaseResult] = []
        exit_codes: List[int | pytest.ExitCode] = []

        with redirect_stdout(io.StringIO()) as _, redirect_stderr(io.StringIO()) as _:
            # TODO: test a single function, not multiple solutions
            for name, function in functions_to_run.items():
                # Create the test collector
                result_collector = ResultCollector()
                # Run the tests
                result = pytest.main(
                    ["-k", f"test_{name}", f"{self.module_file}"],
                    plugins=[
                        FunctionInjectionPlugin(function),
                        result_collector,
                    ],
                )

                # reset execution count on success
                success = result == pytest.ExitCode.OK
                exit_codes.append(result)

                if success:
                    ipytest_result.cell_execution_count[cell_id] = 0

                outputs.extend(result_collector.tests.values())

        if all(
            exit_code == pytest.ExitCode.NO_TESTS_COLLECTED for exit_code in exit_codes
        ):
            ipytest_result.status = IPytestOutcome.NO_TEST_FOUND
        else:
            ipytest_result.status = IPytestOutcome.FINISHED
            ipytest_result.test_results = outputs

        return ipytest_result

    @cell_magic
    def ipytest(self, line: str, cell: str):
        """The `%%ipytest` cell magic"""
        # Check that the magic is called from a notebook
        if not self.shell:
            raise InstanceNotFoundError("InteractiveShell")

        # Get the module containing the test(s)
        module_name = get_module_name(line, self.shell.user_global_ns)
        self.module_name = module_name
        module_file = pathlib.Path(f"tutorial/tests/test_{self.module_name}.py")

        # Check that the test module file exists
        if not module_file.exists():
            raise FileNotFoundError(f"Module file '{module_file}' does not exist")
        self.module_file = module_file

        result = self.run_cell(cell)

        # TODO: this should be passed somehow to the TestResultOutput class
        # Parse the AST tree of the file containing the test functions,
        # to extract and store all information of function definitions and imports
        self.ast_parser = AstParser(self.module_file)

        # Display the test results and the solution code
        TestResultOutput(result).display_results()


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """

    ipython.register_magics(TestMagic)
