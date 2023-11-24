"""A module to define the `%%ipytest` cell magic"""
import io
import pathlib
import re
from contextlib import redirect_stderr, redirect_stdout
from typing import Dict, Optional
import asyncio
import ipynbname
import pytest
from IPython.core.display import Javascript
from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import display
from dataclasses import dataclass, field
from .testsuite_helpers import (
    AstParser,
    FunctionInjectionPlugin,
    FunctionNotFoundError,
    InstanceNotFoundError,
    ResultCollector,
    TestResultOutput,
    IpytestResult,
    IpytestStatus
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

    shell: Optional[InteractiveShell]  # type: ignore
    module_file: Optional[pathlib.Path] 
    module_name: Optional[str] 
    cells: Dict[str, int] 

    def __init__(self, shell):
        super().__init__(shell)
        self.shell = shell
        self.module_file = None
        self.module_name = None
        self.cells = {}

    def run_cell(self, cell: str) -> IpytestResult:
        # Run the cell through IPython
        try:
            result = self.shell.run_cell(cell, silent=True)
            result.raise_error()
        except Exception as e:
            return IpytestResult(status=IpytestStatus.SYNTAX_ERROR, exception=e)
        
        #Retrieve the functions names defined in the current cell
        # Only functions with names starting with `solution_` will be candidates for tests
        functions_names = re.findall(r"^def\s+(solution_.*?)\s*\(", cell, re.M)

        # Get the functions objects from user namespace
        functions_to_run = {}
        for name, function in self.shell.user_ns.items():
            if name in functions_names and callable(function):
                functions_to_run[name.removeprefix("solution_")] = function

        if not functions_to_run:
            return IpytestResult(status=IpytestStatus.SOLUTION_FUNCTION_MISSING, exception=FunctionNotFoundError)
        
        #TODO: verify if this is needed: probably not because the shell must exist for ipytest to be called
        if (ipython := get_ipython()) is None:
            raise InstanceNotFoundError("IPython")
        

        # Store execution count information for each cell
        cell_id = ipython.parent_header["metadata"]["cellId"]  # type: ignore
        if cell_id in self.cells:
            self.cells[cell_id] += 1
        else:
            self.cells[cell_id] = 1

        # Parse the AST tree of the file containing the test functions,
        # to extract and store all information of function definitions and imports
        ast_parser = AstParser(self.module_file)

        #Run the test for each function
        outputs = []
        exit_codes = []
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            #TODO: test a single function, not multiple solutions
            for name, function in functions_to_run.items():
                # Create the test collector
                result_collector = ResultCollector()
                # Run the tests
                result = pytest.main(
                    [
                        "-k",
                        f"test_{name}",
                        f"{self.module_file}"
                    ],
                    plugins=[
                        FunctionInjectionPlugin(function),
                        result_collector,
                    ],
                )


                # reset execution count on success
                success = result == pytest.ExitCode.OK
                exit_codes.append(result)
                if success:
                    self.cells[cell_id] = 0

                outputs.append(
                    list(result_collector.tests.values())
                )
        if all(exit_code == pytest.ExitCode.NO_TESTS_COLLECTED for exit_code in exit_codes):
            return IpytestResult(status=IpytestStatus.NO_TEST_FOUND, exception=None)    
        return IpytestResult(status=IpytestStatus.FINISHED, test_results=sum(outputs, []))

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


        self.display(result)

    
    def display(self, result: IpytestResult) -> None:
        #Display the results
        #TODO : display the results in a more readable way. This function should return HTML
        # - If synatx error, display the error message in the same style as the rest
        # - If the solution (function_to_test) is missing, display a message informing the user that the solution is missing
        # - If the test finish, iterate over the test results and display each case
        #   - If all tests pass, display a message informing the user that all tests passed
        #   - If some tests fail, display a message informing the user that some tests failed
        match result.status:
            case IpytestStatus.SYNTAX_ERROR:
                display(f"alert('Syntax error: {result.exception}')")
            case IpytestStatus.SOLUTION_FUNCTION_MISSING:
                display(f"alert('Solution function missing: {result.exception}')")
            case IpytestStatus.FINISHED:
                for test_result in result.test_results:
                    display(test_result)
            case IpytestStatus.NO_TEST_FOUND:
                display(f"alert(no test found)')")
            

       


  

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """

    ipython.register_magics(TestMagic)
