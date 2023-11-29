import html
import re
import traceback
from dataclasses import dataclass
from enum import Enum
from types import TracebackType
from typing import Callable, Dict, List, Optional

import ipywidgets
import pytest
from IPython.core.display import HTML
from IPython.display import display as ipython_display


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
    status: Optional[IPytestOutcome] = None
    test_results: Optional[List[TestCaseResult]] = None
    exceptions: Optional[List[BaseException]] = None
    cell_execution_count: int = 0


def format_error(exception: BaseException) -> str:
    """
    Takes the output of traceback.format_exception_only() for an AssertionError
    and returns a formatted string with clear, structured information.
    """
    formatted_message = None

    # Get a string representation of the exception, without the traceback
    exception_str = "".join(traceback.format_exception_only(exception))

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


@dataclass
class TestResultOutput:
    """Class to prepare and display test results in a Jupyter notebook"""

    ipytest_result: IPytestResult

    def display_results(self) -> None:
        """Display the test results in an output widget as a VBox"""
        cells = []

        output_cell = self.prepare_output_cell()
        solution_cell = self.prepare_solution_cell()

        cells.append(output_cell)

        success = (
            all(
                map(
                    lambda x: x.outcome == TestOutcome.PASS,
                    self.ipytest_result.test_results,
                )
            )
            if self.ipytest_result.test_results
            else False
        )

        if self.ipytest_result.cell_execution_count > 2 or success:
            cells.append(solution_cell)

        ipython_display(ipywidgets.VBox(children=cells))

    def prepare_solution_cell(self) -> ipywidgets.Widget:
        """Prepare the cell to display the solution code"""
        solution_code = ipywidgets.Output()
        solution_cell = ipywidgets.Output()

        solution_cell.append_display_data(HTML("<h4>&#128073; Proposed solution:</h4>"))

        # FIXME: parse the AST tree to get the function body
        solution_code.append_display_data(
            Code(language="python", data=f"{solution_body}")
        )

        solution_accordion = ipywidgets.Accordion(
            titles=("Click here to reveal",), children=[solution_code]
        )

        solution_cell.append_display_data(
            ipywidgets.Box(
                children=[solution_accordion],
            )
        )

        return solution_cell

    def prepare_output_cell(self) -> ipywidgets.Output:
        """Prepare the cell to display the test results"""
        output_cell = ipywidgets.Output()
        output_cell.append_display_data(HTML("<h2>Test Results</h2>"))

        # TODO: the following is just a placeholder
        match self.ipytest_result.status:
            case IPytestOutcome.SYNTAX_ERROR:
                output_cell.append_display_data(HTML("<h3>Syntax Error</h3>"))
            case IPytestOutcome.SOLUTION_FUNCTION_MISSING:
                output_cell.append_display_data(
                    HTML("<h3>Solution Function Missing</h3>")
                )
            case IPytestOutcome.FINISHED if self.ipytest_result.test_results:
                output_cell.append_display_data(HTML("<h3>Test Finished</h3>"))
            case IPytestOutcome.NO_TEST_FOUND:
                output_cell.append_display_data(HTML("<h3>No Test Found</h3>"))

        return output_cell


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


class FunctionNotFoundError(Exception):
    """Custom exception raised when the solution code cannot be parsed"""

    def __init__(self) -> None:
        super().__init__("No functions to test defined in the cell")


class InstanceNotFoundError(Exception):
    """Custom exception raised when an instance cannot be found"""

    def __init__(self, name: str) -> None:
        super().__init__(f"Could not get {name} instance")
