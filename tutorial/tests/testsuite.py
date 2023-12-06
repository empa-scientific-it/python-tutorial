"""A module to define the `%%ipytest` cell magic"""
import dataclasses
import inspect
import io
import pathlib
import re
from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
from queue import Queue
from threading import Thread
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
    TestOutcome,
    TestResultOutput,
)


def run_test(
    module_file: pathlib.Path, function_name: str, function_object: Callable
) -> IPytestResult:
    """
    Run the tests for a single function
    """
    with redirect_stdout(io.StringIO()) as _, redirect_stderr(io.StringIO()) as _:
        # Create the test collector
        result_collector = ResultCollector()

        # Run the tests
        result = pytest.main(
            ["-k", f"test_{function_name}", f"{module_file}"],
            plugins=[
                FunctionInjectionPlugin(function_object),
                result_collector,
            ],
        )

    match result:
        case pytest.ExitCode.OK:
            return IPytestResult(
                function_name=function_name,
                status=IPytestOutcome.FINISHED,
                test_results=list(result_collector.tests.values()),
            )
        case pytest.ExitCode.TESTS_FAILED:
            if any(
                test.outcome == TestOutcome.TEST_ERROR
                for test in result_collector.tests.values()
            ):
                return IPytestResult(
                    function_name=function_name,
                    status=IPytestOutcome.PYTEST_ERROR,
                    exceptions=[
                        test.exception
                        for test in result_collector.tests.values()
                        if test.exception
                    ],
                )

            return IPytestResult(
                function_name=function_name,
                status=IPytestOutcome.FINISHED,
                test_results=list(result_collector.tests.values()),
            )
        case pytest.ExitCode.INTERNAL_ERROR:
            return IPytestResult(
                function_name=function_name,
                status=IPytestOutcome.PYTEST_ERROR,
                exceptions=[Exception("Internal error")],
            )
        case pytest.ExitCode.NO_TESTS_COLLECTED:
            return IPytestResult(
                function_name=function_name,
                status=IPytestOutcome.NO_TEST_FOUND,
                exceptions=[FunctionNotFoundError()],
            )

    return IPytestResult(
        status=IPytestOutcome.UNKNOWN_ERROR, exceptions=[Exception("Unknown error")]
    )


def run_test_in_thread(
    module_file: pathlib.Path,
    function_name: str,
    function_object: Callable,
    test_queue: Queue,
):
    """Run the tests for a single function and put the result in the queue"""
    test_queue.put(run_test(module_file, function_name, function_object))


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

    def __init__(self, shell, threded: bool = True):
        super().__init__(shell)
        self.max_execution_count = 3
        self.shell: InteractiveShell = shell
        self.cell: str = ""
        self.module_file: Optional[pathlib.Path] = None
        self.module_name: Optional[str] = None
        self.threaded = threded
        if self.threaded:
            self.test_queue = Queue[IPytestResult]()
        self.cell_execution_count: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        # self.functions_to_run: Dict[str, Callable] = {}

        # This is monkey-patching suppress printing any exception or traceback
        # self.shell._showtraceback = lambda *args, **kwargs: None

    def extract_functions_to_test(self) -> Dict[str, Callable]:
        """"""
        # Retrieve the functions names defined in the current cell
        # Only functions with names starting with `solution_` will be candidates for tests
        functions_names: List[str] = re.findall(
            r"^(?:async\s+?)?def\s+(solution_.*?)\s*\(", self.cell, re.M
        )

        return {
            name.removeprefix("solution_"): function
            for name, function in self.shell.user_ns.items()
            if name in functions_names
            and (callable(function) or inspect.is_coroutine_function(function))
        }

    def run_test(self, function_name: str, function_object: Callable) -> IPytestResult:
        """Run the tests for a single function"""
        # Store execution count information for each cell
        cell_id = str(self.shell.parent_header["metadata"]["cellId"])  # type: ignore
        self.cell_execution_count[cell_id][function_name] += 1
        # Run the tests on a separate thread
        if self.threaded:
            thread = Thread(
                target=run_test_in_thread,
                args=(
                    self.module_file,
                    function_name,
                    function_object,
                    self.test_queue,
                ),
            )
            thread.start()
            thread.join()
            result = self.test_queue.get()
        else:
            result = run_test(self.module_file, function_name, function_object)
        # Increment the
        match result.status:
            case IPytestOutcome.FINISHED:
                return dataclasses.replace(
                    result,
                    test_attempts=self.cell_execution_count[cell_id][function_name],
                )
            case _:
                return result

    def run_cell(self) -> List[IPytestResult]:
        # Run the cell through IPython
        try:
            result = self.shell.run_cell(self.cell, silent=True)  # type: ignore
            result.raise_error()
        except Exception as err:
            return [
                IPytestResult(
                    status=IPytestOutcome.COMPILE_ERROR,
                    exceptions=[err],
                )
            ]

        functions_to_run = self.extract_functions_to_test()

        if not functions_to_run:
            return [
                IPytestResult(
                    status=IPytestOutcome.SOLUTION_FUNCTION_MISSING,
                    exceptions=[FunctionNotFoundError()],
                )
            ]

        # Run the tests for each function
        test_results = [
            self.run_test(name, function) for name, function in functions_to_run.items()
        ]

        print(test_results)

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

        results = self.run_cell()

        ast_parser = AstParser(self.module_file)

        # Display the test results and the solution code
        for result in results:
            solution = (
                ast_parser.get_solution_code(result.function_name)
                if result.function_name
                else None
            )
            TestResultOutput(result, solution).display_results()


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """

    ipython.register_magics(TestMagic)
