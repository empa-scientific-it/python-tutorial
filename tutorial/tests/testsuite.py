"""A module to define the `%%ipytest` cell magic"""
import io
import pathlib
import re
from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
from typing import Callable, Dict, List, Optional

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
        self.cell: str = ""
        self.module_file: Optional[pathlib.Path] = None
        self.module_name: Optional[str] = None
        self.cell_execution_count: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.functions_to_run: Dict[str, Callable] = {}

        # This is monkey-patching suppress printing any exception or traceback
        self.shell._showtraceback = lambda *args, **kwargs: None

    # TODO: ideally we want to run the tests for a single function, not multiple solutions
    #   So we need to split the run_cell into multiple functions:
    #       1. extract_function_names: extract the names of all functions to test defined in the cell
    #       2. run_tests: run the tests on a single function
    #       3. run_cell: run the tests on all functions defined in the cell

    def extract_functions_to_test(self) -> None:
        """"""
        # Retrieve the functions names defined in the current cell
        # Only functions with names starting with `solution_` will be candidates for tests
        functions_names: List[str] = re.findall(
            r"^def\s+(solution_.*?)\s*\(", self.cell, re.M
        )

        # Get the functions objects from user namespace
        for name, function in self.shell.user_ns.items():  # type: ignore
            if name in functions_names and callable(function):
                self.functions_to_run[name.removeprefix("solution_")] = function

    def run_test(self, function_name: str, function_object: Callable) -> IPytestResult:
        """Run the tests for a single function"""
        # Store execution count information for each cell
        cell_id = str(self.shell.parent_header["metadata"]["cellId"])  # type: ignore

        self.cell_execution_count[cell_id][function_name] += 1

        with redirect_stdout(io.StringIO()) as _, redirect_stderr(io.StringIO()) as _:
            # Create the test collector
            result_collector = ResultCollector()

            # Run the tests
            result = pytest.main(
                ["-k", f"test_{function_name}", f"{self.module_file}"],
                plugins=[
                    FunctionInjectionPlugin(function_object),
                    result_collector,
                ],
            )

            # reset execution count on success
            success = result == pytest.ExitCode.OK

            if success:
                self.cell_execution_count[cell_id][function_name] = 0

        if result == pytest.ExitCode.NO_TESTS_COLLECTED:
            return IPytestResult(
                status=IPytestOutcome.NO_TEST_FOUND,
                exceptions=[FunctionNotFoundError()],
            )

        return IPytestResult(
            status=IPytestOutcome.FINISHED,
            test_results=list(result_collector.tests.values()),
            cell_execution_count=self.cell_execution_count[cell_id][function_name],
        )

    def run_cell(self) -> List[IPytestResult]:
        # Run the cell through IPython
        try:
            result = self.shell.run_cell(self.cell, silent=True)  # type: ignore
            result.raise_error()
        except Exception as err:
            return [
                IPytestResult(
                    status=IPytestOutcome.SYNTAX_ERROR,
                    exceptions=[err],
                )
            ]

        self.extract_functions_to_test()

        if not self.functions_to_run:
            return [
                IPytestResult(
                    status=IPytestOutcome.SOLUTION_FUNCTION_MISSING,
                    exceptions=[FunctionNotFoundError()],
                )
            ]

        # Run the tests for each function
        test_results: List[IPytestResult] = []

        for name, function in self.functions_to_run.items():
            test_results.append(self.run_test(name, function))

        return test_results

    @cell_magic
    def ipytest(self, line: str, cell: str):
        """The `%%ipytest` cell magic"""
        # Check that the magic is called from a notebook
        if not self.shell:
            raise InstanceNotFoundError("InteractiveShell")

        # Store the cell content
        self.cell = cell

        # Get the module containing the test(s)
        module_name = get_module_name(line, self.shell.user_global_ns)
        self.module_name = module_name
        module_file = pathlib.Path(f"tutorial/tests/test_{self.module_name}.py")

        # Check that the test module file exists
        if not module_file.exists():
            raise FileNotFoundError(f"Module file '{module_file}' does not exist")
        self.module_file = module_file

        result = self.run_cell()

        # TODO: this should be passed somehow to the TestResultOutput class
        # Parse the AST tree of the file containing the test functions,
        # to extract and store all information of function definitions and imports
        ast_parser = AstParser(self.module_file)
        solutions = [
            ast_parser.get_solution_code(function_name)
            for function_name in self.functions_to_run
        ]

        # Display the test results and the solution code
        TestResultOutput(result).display_results()


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """

    ipython.register_magics(TestMagic)
