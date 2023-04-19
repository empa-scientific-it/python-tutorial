import io
import pathlib
import re
from contextlib import redirect_stdout, redirect_stderr
from typing import Callable, Dict, Optional, List

import ipynbname
import pytest
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.display import HTML, display
import importlib

import ipywidgets

import importlib.util

import dataclasses

def _name_from_line(line: str = None):
    return line.strip().removesuffix(".py") if line else None


def _name_from_ipynbname() -> str | None:
    try:
        return ipynbname.name()
    except FileNotFoundError:
        return None


def _name_from_globals(globals_dict: Dict) -> str | None:
    module_path = globals_dict.get('__vsc_ipynb_file__') if globals_dict else None
    return pathlib.Path(module_path).stem if module_path else None


def get_module_name(line: str, globals_dict: Dict = None) -> str:
    """Fetch the test module name"""
    module_name = _name_from_line(line) or _name_from_ipynbname() or _name_from_globals(globals_dict)

    if not module_name:
        raise RuntimeError("Test module is undefined. Did you provide an argument to %%ipytest?")

    return module_name

def find_solution(ns: Dict[str, Callable], postfix: str) -> Optional[Callable]:
    """Given a namespace, finds a solution matching a given pattern."""
    return [f for k,f in ns if k.endswith(postfix)][0]


class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        """Override the abstract `function_to_test` fixture function"""
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])






@dataclasses.dataclass
class TestResult:
    stdout: List[str]
    stderr: List[str]
    test_name: str
    success: bool

@dataclasses.dataclass
class OutputConfig:
    style: str
    name: str
    result: str


def format_success_failure(success: bool , name: str) -> OutputConfig:
    """
    Depending on the test results, returns a fragment that represent
    an error message or a success message
    """
    if success:
        return OutputConfig(
            "alert-success",
            f"Tests <strong>PASSED</strong> for the function <code>{name}</code>",
            "&#x1F64C Congratulations, your solution was correct!")
    else:
        return OutputConfig(
                "alert-danger",
                f"Tests <strong>FAILED</strong> for the function <code>{name}</code>",
                "&#x1F631 Your solution was not correct!")



def format_long_stdout(text: str) -> str:
    """
    Format a long test stdout as a HTML by using the <details> element
    """
    def join_lines(text: str, n: int) -> str:
        return "".join([f"<p>{line}</p>" for i, line in enumerate(text.splitlines()) if i < n])
    test_runs = "".join([f"""<details style="overflow-y: scroll; max-height: 200px;"><summary>Click here to see output</summary><div style="border: 1px solid black">{"".join(join_lines(text, len(text)))}</div></details></li>"""])
    return test_runs


    


class TestResultOutput(ipywidgets.VBox):

    def __init__(self, name: str, success: bool, test_outputs: List[TestResult], test_stdout: str):
        
        output_config = format_success_failure(success, name)
        message = f"""<div class="alert alert-box {output_config.style}"><h4>{output_config.name}</h4>{output_config.result}</div><h4>"""
        output_cell = ipywidgets.Output()
        with output_cell:
            display(HTML(message)) 
            display(HTML(f"<h4>We run the test for solution_{name} {len(test_outputs)} times, below you find the details for each test run:</h4>"))
            for test in test_outputs:
                display(HTML(f"<h4>Test {test.test_name}</h4>"))
                display(HTML(f"<h5>Test output (contains the outputs you printed in solution_{name})</h5>"))
                display(HTML(format_long_stdout(test.stdout)))
                display(HTML(f"<h5>Test error</h5>"))
                display(HTML(format_long_stdout(test.stderr)))
            
        super().__init__(children=[output_cell])




class TestCollector:
    """A class to collect all tests that will be run."""
    def __init__(self) -> None:
        self.tests = set()
    
    def pytest_collection_finish(self, session: pytest.Session):
        [self.tests.add(fun) for fun in session.items]


class ResultCollector:
    """A class that will collect the result of a test."""
    def __init__(self) -> None:
        self.tests:Dict[str, TestResult] = {}
    
    def pytest_runtest_logreport(self, report: pytest.TestReport):
        if report.when == "teardown":
            self.tests[report.nodeid] = TestResult(report.capstdout, report.capstderr, report.nodeid, not report.failed)

    def pytest_exception_interact(self, node: pytest.Item, call: pytest.CallInfo, report: pytest.TestReport):
        print(node)
        self.tests[report.nodeid] = TestResult(report.capstdout, str(call.excinfo.getrepr()) , report.nodeid, not report.failed)

@pytest.fixture
def function_to_test():
    """Function to test, overriden at runtime by the cell magic"""


@magics_class
class TestMagic(Magics):
    """Class to add the test cell magic"""

    shell: InteractiveShell

    @cell_magic
    def ipytest(self, line: str, cell: str):
        """The `%%ipytest` cell magic"""
        # Get the module containing the test(s)
        module_name = get_module_name(line, self.shell.user_global_ns)

        # Check that the test module file exists
        module_file = pathlib.Path(f"tutorial/tests/test_{module_name}.py")
        if not module_file.exists():
            raise FileNotFoundError(f"Module file '{module_file}' does not exist")

        # Run the cell through IPython
        self.shell.run_cell(cell)

        # Retrieve the functions names defined in the current cell
        # Only functions with names starting with `solution_` will be candidates for tests
        functions_names = re.findall(r"^def\s+(solution_.*?)\s*\(", cell, re.M)

        # Get the functions objects from user namespace
        functions_to_run = {}
        buttons = []
        for name, function in self.shell.user_ns.items():
            if name in functions_names and callable(function):
                functions_to_run[name.removeprefix("solution_")] = function
                

        if not functions_to_run:
            raise ValueError("No function to test defined in the cell")
        outputs = []
        for name, function in functions_to_run.items():
            #Create the test collector
            test_collector = TestCollector()
            result_collector = ResultCollector()
            # Run the tests
            with  redirect_stderr(io.StringIO()) as pytest_stdout:
                result = pytest.main(
                    [
                        "-q",
                        f"{module_file}::test_{name}",
                    ],
                    plugins=[FunctionInjectionPlugin(function), test_collector, result_collector],
                )
                # Read pytest output
                pytest_output = pytest_stdout.getvalue()
                display(*[(test.stderr) for test in result_collector.tests.values()])
            outputs.append(TestResultOutput(name, result == pytest.ExitCode.OK, list(result_collector.tests.values()), pytest_stdout.getvalue()))
            
        display(*(outputs))


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    ipython.register_magics(TestMagic)
