import ast
import html
import pathlib
import re
from dataclasses import dataclass
from enum import Enum
from types import TracebackType
from typing import Callable, Dict, List, Optional, Set

import ipywidgets
import pytest
from IPython.core.display import HTML


class TestOutcome(Enum):
    PASS = 1
    FAIL = 2
    TEST_ERROR = 3


class IPytestOutcome(Enum):
    FINISHED = 0
    SYNTAX_ERROR = 1
    SOLUTION_FUNCTION_MISSING = 2
    NO_TEST_FOUND = 3


@dataclass
class TestCaseResult:
    """Container class to store the test results when we collect them"""

    test_name: str
    outcome: TestOutcome
    stdout: str | None
    stderr: str | None
    exception: BaseException | None
    traceback: TracebackType | None
    _html_format_string: str = """<div class="alert alert-box {}"><h4>{}</h4>{}</div>"""

    def __format__(self) -> str:
        """Format a test result as a string"""

        if self.outcome == TestOutcome.FAIL:
            return self._html_format_string.format(
                "alert-danger",
                f"Tests <strong>FAILED</strong> for the function <code>{self.test_name}</code>",
                "&#x1F631 Your solution was not correct!",
            )
        elif self.outcome == TestOutcome.TEST_ERROR:
            return self._html_format_string.format(
                "alert-warning",
                "Tests <strong>COULD NOT RUN</strong> for this cell.",
                "&#129300 Careful, looks like you have a syntax error.",
            )
        elif self.outcome == TestOutcome.PASS:
            return self._html_format_string.format(
                "alert-success",
                f"Tests <strong>PASSED</strong> for the function <code>{self.test_name}</code>",
                "&#x1F389 Congratulations!",
            )
        else:
            return self.__str__()


@dataclass
class IPytestResult:
    status: IPytestOutcome
    test_results: Optional[List[TestCaseResult]] = None
    exceptions: Optional[List[BaseException]] = None
    cell_execution_count: Optional[Dict[str, int]] = None


# TODO: this should be deleted if the new format_assertion_error() is used
def format_long_stdout(text: str) -> str:
    """
    Format the error message lines of a long test stdout
    as an HTML that expands, by using the <details> element
    """

    stdout_body = re.split(r"_\s{3,}", text)[-1]
    stdout_filtered = list(
        filter(re.compile(r".*>E\s").match, stdout_body.splitlines())
    )
    stdout_str = "".join(f"<p>{line}</p>" for line in stdout_filtered)
    stdout_edited = re.sub(r"E\s+[\+\s]*", "", stdout_str)
    stdout_edited = re.sub(
        r"\bfunction\ssolution_[\w\s\d]*", "your_solution", stdout_edited
    )
    stdout_edited = re.sub(r"\breference_\w+\(", "reference_solution(", stdout_edited)

    test_runs = f"""
            <details style="overflow-y: auto; max-height: 200px;">
                <summary><u style="cursor: pointer;">Click here to expand</u></summary>
                <div style="padding-top: 15px;">{stdout_edited}</div>
            </details>
        """
    return test_runs


def format_assertion_error(exception_info: List[str]) -> str:
    """
    Takes the output of traceback.format_exception_only() for an AssertionError
    and returns a formatted string with clear, structured information.
    """
    formatted_message = None

    # Join the list into a single string
    exception_str = "".join(exception_info)

    # Handle the case where we were expecting an exception but none was raised
    if "DID NOT RAISE" in exception_str:
        pattern = r"<class '(.*?)'>"
        match = re.search(pattern, exception_str)

        if match:
            formatted_message = (
                "<h4>Expected exception:</h4>"
                f"<p>Exception <code>{html.escape(match.group(1))}</code> was not raised.</p>"
            )
    else:
        # Regex pattern to extract relevant parts of the assertion message
        pattern = (
            r"(\w+): assert (.*?) == (.*?)\n \+  where .*? = (.*?)\n \+  and .*? = (.*)"
        )
        match = re.search(pattern, exception_str)

        if match:
            (
                assertion_type,
                actual_value,
                expected_value,
                actual_expression,
                expected_expression,
            ) = (html.escape(m) for m in match.groups())

            # Formatting the output as HTML
            formatted_message = (
                f"<h4>{assertion_type}:</h4>"
                "<ul>"
                f"<li>Failed Assertion: <strong>{actual_value} == {expected_value}</strong></li>"
                f"<li>Actual Value: <strong>{actual_value}</strong> obtained from <code>{actual_expression}</code></li>"
                f"<li>Expected Value: <strong>{expected_value}</strong> obtained from <code>{expected_expression}</code></li>"
                "</ul>"
            )

    # If we couldn't parse the exception message, just display it as is
    formatted_message = formatted_message or f"<p>{html.escape(exception_str)}</p>"

    return f"""
            <details style="overflow-y: auto; max-height: 200px;">
                <summary><u style="cursor: pointer;">Click here to expand</u></summary>
                <div style="padding-top: 15px;">{formatted_message}</div>
            </details>
        """


def show_test_result_output(ipytest_result: IPytestResult) -> ipywidgets.VBox:
    """
    Display the test results in an output widget as a VBox
    """
    solution_output = ipywidgets.Output()
    solution_box = ipywidgets.VBox()
    output_cell = ipywidgets.Output()

    output_cell.append_display_data(HTML("<h2>Test Results</h2>"))
    match ipytest_result.status:
        case IPytestOutcome.SYNTAX_ERROR:
            # Syntax error
            output_cell.append_display_data(HTML("<h3>Syntax Error</h3>"))
        case IPytestOutcome.SOLUTION_FUNCTION_MISSING:
            # Solution function missing
            output_cell.append_display_data(HTML("<h3>Solution Function Missing</h3>"))
        case IPytestOutcome.FINISHED if ipytest_result.test_results:
            output_cell.append_display_data(HTML("<h3>Test Finished</h3>"))
        case IPytestOutcome.NO_TEST_FOUND:
            output_cell.append_display_data(HTML("<h3>No Test Found</h3>"))
    return ipywidgets.VBox(children=[output_cell, solution_box, solution_output])


@pytest.fixture
def function_to_test():
    """Function to test, overridden at runtime by the cell magic"""


class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        # Override the abstract `function_to_test` fixture function
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])


class ResultCollector:
    """A class that will collect the result of a test. If behaves a bit like a visitor pattern"""

    def __init__(self) -> None:
        self.tests: Dict[str, TestCaseResult] = {}

    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo):
        # Test run is finished without error
        if call.when == "call":
            if call.excinfo is None:
                # Test passes
                self.tests[item.nodeid] = TestCaseResult(
                    test_name=item.nodeid,
                    outcome=TestOutcome.PASS,
                    stdout=call.result,
                    stderr=call.result,
                    exception=None,
                    traceback=None,
                )
            else:
                # Test fails
                self.tests[item.nodeid] = TestCaseResult(
                    test_name=item.nodeid,
                    outcome=TestOutcome.FAIL,
                    stdout=None,
                    stderr=None,
                    exception=call.excinfo.value,
                    traceback=call.excinfo.tb,
                )

        if call.when == "collect":
            # Test fails to run because of syntax error
            if call.excinfo is not None:
                self.tests[item.nodeid] = TestCaseResult(
                    test_name=item.nodeid,
                    outcome=TestOutcome.TEST_ERROR,
                    stdout=None,
                    stderr=None,
                    exception=call.excinfo.value,
                    traceback=call.excinfo.tb,
                )

    def pytest_runtest_logreport(self, report: pytest.TestReport):
        # Only collect the results if it did not fail
        if report.when == "teardown" and report.nodeid in self.tests:
            test_result = self.tests[report.nodeid]
            test_result.stdout = report.capstdout
            test_result.stderr = report.capstderr


class AstParser:
    """
    Helper class for extraction of function definitions and imports.
    To find all reference solutions:
    Parse the module file using the AST module and retrieve all function definitions and imports.
    For each reference solution store the names of all other functions used inside of it.
    """

    def __init__(self, module_file: pathlib.Path) -> None:
        self.module_file = module_file
        self.function_defs = {}
        self.function_imports = {}
        self.called_function_names = {}

        tree = ast.parse(self.module_file.read_text(encoding="utf-8"))

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.function_defs[node.name] = node
            elif isinstance(node, (ast.Import, ast.ImportFrom)) and hasattr(
                node, "module"
            ):
                for n in node.names:
                    self.function_imports[n.name] = node.module

        for node in tree.body:
            if (
                node in self.function_defs.values()
                and hasattr(node, "name")
                and node.name.startswith("reference_")
            ):
                self.called_function_names[node.name] = self.retrieve_functions(
                    {**self.function_defs, **self.function_imports}, node, {node.name}
                )

    def retrieve_functions(
        self, all_functions: Dict, node: object, called_functions: Set[object]
    ) -> Set[object]:
        """
        Recursively walk the AST tree to retrieve all function definitions in a file
        """

        if isinstance(node, ast.AST):
            for n in ast.walk(node):
                match n:
                    case ast.Call(ast.Name(id=name)):
                        called_functions.add(name)
                        if name in all_functions:
                            called_functions = self.retrieve_functions(
                                all_functions, all_functions[name], called_functions
                            )
                for child in ast.iter_child_nodes(n):
                    called_functions = self.retrieve_functions(
                        all_functions, child, called_functions
                    )

        return called_functions

    def get_solution_code(self, name):
        """
        Find the respective reference solution for the executed function.
        Create a str containing its code and the code of all other functions used,
        whether coming from the same file or an imported one.
        """

        solution_functions = self.called_function_names[f"reference_{name}"]
        solution_code = ""

        for f in solution_functions:
            if f in self.function_defs:
                solution_code += ast.unparse(self.function_defs[f]) + "\n\n"
            elif f in self.function_imports:
                function_file = pathlib.Path(
                    f"{self.function_imports[f].replace('.', '/')}.py"
                )
                if function_file.exists():
                    function_file_tree = ast.parse(
                        function_file.read_text(encoding="utf-8")
                    )
                    for node in function_file_tree.body:
                        if (
                            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and node.name == f
                        ):
                            solution_code += ast.unparse(node) + "\n\n"

        return solution_code


class FunctionNotFoundError(Exception):
    """Custom exception raised when the solution code cannot be parsed"""

    def __init__(self) -> None:
        super().__init__("No functions to test defined in the cell")


class InstanceNotFoundError(Exception):
    """Custom exception raised when an instance cannot be found"""

    def __init__(self, name: str) -> None:
        super().__init__(f"Could not get {name} instance")
