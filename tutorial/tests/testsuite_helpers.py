import html
import re
import traceback
from dataclasses import dataclass
from enum import Enum
from types import TracebackType
from typing import Callable, ClassVar, Dict, List, Optional

import ipywidgets
import pytest
from IPython.display import Code
from IPython.display import display as ipython_display
from ipywidgets import HTML


class TestOutcome(Enum):
    PASS = 1
    FAIL = 2
    TEST_ERROR = 3


class IPytestOutcome(Enum):
    FINISHED = 0
    COMPILE_ERROR = 1
    SOLUTION_FUNCTION_MISSING = 2
    NO_TEST_FOUND = 3
    PYTEST_ERROR = 4
    UNKNOWN_ERROR = 5


@dataclass
class TestCaseResult:
    """Container class to store the test results when we collect them"""

    test_name: str
    outcome: TestOutcome
    exception: BaseException | None
    traceback: TracebackType | None
    stdout: str = ""
    stderr: str = ""

    # FIXME: this is unused
    # _html_format_string: str = """<div class="alert alert-box {}"><h4>{}</h4>{}</div>"""

    # def __format__(self) -> str:
    #     """Format a test result as a string"""

    #     if self.outcome == TestOutcome.FAIL:
    #         return self._html_format_string.format(
    #             "alert-danger",
    #             f"Tests <strong>FAILED</strong> for the function <code>{self.test_name}</code>",
    #             "&#x1F631 Your solution was not correct!",
    #         )
    #     elif self.outcome == TestOutcome.TEST_ERROR:
    #         return self._html_format_string.format(
    #             "alert-warning",
    #             "Tests <strong>COULD NOT RUN</strong> for this cell.",
    #             "&#129300 Careful, looks like you have a syntax error.",
    #         )
    #     elif self.outcome == TestOutcome.PASS:
    #         return self._html_format_string.format(
    #             "alert-success",
    #             f"Tests <strong>PASSED</strong> for the function <code>{self.test_name}</code>",
    #             "&#x1F389 Congratulations!",
    #         )
    #     else:
    #         return self.__str__()


@dataclass
class IPytestResult:
    function_name: Optional[str] = None
    status: Optional[IPytestOutcome] = None
    test_results: Optional[List[TestCaseResult]] = None
    exceptions: Optional[List[BaseException]] = None
    test_attempts: int = 0


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
                "<h3>Expected exception:</h3>"
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
                f"<h3>{assertion_type}:</h3>"
                "<ul>"
                f"<li>Failed Assertion: <strong>{actual_value} == {expected_value}</strong></li>"
                f"<li>Actual Value: <strong>{actual_value}</strong> obtained from <code>{actual_expression}</code></li>"
                f"<li>Expected Value: <strong>{expected_value}</strong> obtained from <code>{expected_expression}</code></li>"
                "</ul>"
            )

    # If we couldn't parse the exception message, just display it as is
    formatted_message = formatted_message or f"<p>{html.escape(exception_str)}</p>"

    return formatted_message


@dataclass
class TestResultOutput:
    """Class to prepare and display test results in a Jupyter notebook"""

    ipytest_result: IPytestResult
    solution: Optional[str] = None
    MAX_ATTEMPTS: ClassVar[int] = 3

    def display_results(self) -> None:
        """Display the test results in an output widget as a VBox"""
        cells = []

        output_cell = self.prepare_output_cell()
        solution_cell = self.prepare_solution_cell()

        cells.append(output_cell)

        success = (
            all(
                test.outcome == TestOutcome.PASS
                for test in self.ipytest_result.test_results
            )
            if self.ipytest_result.test_results
            else False
        )

        if self.ipytest_result.test_attempts > 2 or success:
            cells.append(solution_cell)
        else:
            cells.append(
                ipywidgets.HTML(
                    "<h4>&#128221; A proposed solution will appear after "
                    f"{TestResultOutput.MAX_ATTEMPTS - self.ipytest_result.test_attempts} "
                    f"more failed attempt{'s' if self.ipytest_result.test_attempts < 2 else ''}.</h4>",
                )
            )

        ipython_display(
            ipywidgets.VBox(
                children=cells,
                # CSS: "border: 1px solid; border-color: lightgray; background-color: #FAFAFA; margin: 5px; padding: 10px;"
                layout={
                    "border": "1px solid lightgray",
                    "background-color": "#FAFAFA",
                    "margin": "5px",
                    "padding": "10px",
                },
            )
        )

    def prepare_solution_cell(self) -> ipywidgets.Widget:
        """Prepare the cell to display the solution code"""
        solution_code = ipywidgets.Output()
        solution_cell = ipywidgets.Output()

        solution_cell.append_display_data(HTML("<h4>&#128073; Proposed solution:</h4>"))

        solution_code.append_display_data(
            Code(language="python", data=f"{self.solution}")
        )

        solution_accordion = ipywidgets.Accordion(
            titles=("Click here to reveal",), children=[solution_code]
        )

        solution_cell.append_display_data(ipywidgets.Box(children=[solution_accordion]))

        return solution_cell

    def prepare_output_cell(self) -> ipywidgets.Output:
        """Prepare the cell to display the test results"""
        output_cell = ipywidgets.Output()
        output_cell.append_display_data(
            HTML(
                f'<h2>Test Results for <span style="color: #00f;">solution_{self.ipytest_result.function_name}</span></h2>'
            )
        )

        match self.ipytest_result.status:
            case IPytestOutcome.COMPILE_ERROR | IPytestOutcome.PYTEST_ERROR | IPytestOutcome.UNKNOWN_ERROR:
                # We know that there is exactly one exception
                assert self.ipytest_result.exceptions is not None
                exception = self.ipytest_result.exceptions[0]
                exceptions_str = (
                    format_error(exception) if self.ipytest_result.exceptions else ""
                )
                output_cell.append_display_data(
                    ipywidgets.VBox(
                        children=[
                            HTML(f"<h3>{type(exception).__name__}</h3>"),
                            HTML(exceptions_str),
                        ]
                    )
                )

            case IPytestOutcome.SOLUTION_FUNCTION_MISSING:
                output_cell.append_display_data(
                    HTML("<h3>Solution Function Missing</h3>")
                )

            case IPytestOutcome.FINISHED if self.ipytest_result.test_results:
                captures: Dict[str, Dict[str, str]] = {}

                for test in self.ipytest_result.test_results:
                    captures[test.test_name.split("::")[-1]] = {
                        "stdout": test.stdout,
                        "stderr": test.stderr,
                    }

                # Create lists of HTML outs and errs
                outs = [
                    f"<h3>{test_name}</h3><br>{captures[test_name]['stdout']}"
                    for test_name in captures
                    if captures[test_name]["stdout"]
                ]
                errs = [
                    f"<h3>{test_name}</h3><br>{captures[test_name]['stderr']}"
                    for test_name in captures
                    if captures[test_name]["stderr"]
                ]

                output_cell.append_display_data(
                    ipywidgets.VBox(
                        children=(
                            ipywidgets.Accordion(
                                children=(
                                    ipywidgets.VBox(
                                        children=[
                                            HTML(o, style={"background": "#FAFAFA"})
                                            for o in outs
                                        ]
                                    ),
                                ),
                                titles=("Captured output",),
                            ),
                            ipywidgets.Accordion(
                                children=(
                                    ipywidgets.VBox(
                                        children=[
                                            HTML(e, style={"background": "#FAFAFA"})
                                            for e in errs
                                        ]
                                    ),
                                ),
                                titles=("Captured error",),
                            ),
                        )
                    )
                )

                success = all(
                    test.outcome == TestOutcome.PASS
                    for test in self.ipytest_result.test_results
                )

                num_results = len(self.ipytest_result.test_results)

                output_cell.append_display_data(
                    HTML(
                        f"<h4>&#128073; We ran {num_results} test{'s' if num_results > 1 else ''}. "
                        f"""{"All tests passed!</h4>" if success else "Below you find the details for each test run:</h4>"}"""
                    )
                )

                if not success:
                    for result in self.ipytest_result.test_results:
                        test_succeded = result.outcome == TestOutcome.PASS
                        test_name = result.test_name.split("::")[-1]

                        output_box_children: List[ipywidgets.Widget] = [
                            ipywidgets.HTML(
                                f'<h3>{"&#10004" if test_succeded else "&#10060"} Test <code>{test_name}</code></h3>',
                                style={
                                    "background": "rgba(251, 59, 59, 0.25)"
                                    if not test_succeded
                                    else "rgba(207, 249, 179, 0.60)"
                                },
                            )
                        ]

                        if not test_succeded:
                            assert result.exception is not None

                            output_box_children.append(
                                ipywidgets.Accordion(
                                    children=[
                                        ipywidgets.HTML(format_error(result.exception))
                                    ],
                                    titles=("Test results",),
                                )
                            )

                        output_cell.append_display_data(
                            ipywidgets.VBox(children=output_box_children)
                        )

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
        """Called when an individual test item has finished execution."""
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
                    exception=call.excinfo.value,
                    traceback=call.excinfo.tb,
                )

    def pytest_exception_interact(
        self, call: pytest.CallInfo, report: pytest.TestReport
    ):
        """Called when an exception was raised which can potentially be interactively handled."""
        if call.excinfo is not None:
            self.tests[report.nodeid] = TestCaseResult(
                test_name=report.nodeid,
                outcome=TestOutcome.TEST_ERROR,
                exception=call.excinfo.value,
                traceback=call.excinfo.tb,
            )

    def pytest_runtest_logreport(self, report: pytest.TestReport):
        """Called to log the report of a test item."""
        if test_result := self.tests.get(report.nodeid):
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
