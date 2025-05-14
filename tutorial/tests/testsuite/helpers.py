import html
import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import Any, ClassVar

import ipywidgets
import pytest
from IPython.display import Code
from IPython.display import display as ipython_display
from ipywidgets import HTML

from .ai_helpers import AIExplanation, OpenAIWrapper


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from text"""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


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
class DebugOutput:
    """Class to format debug information about test execution"""

    module_name: str
    module_file: Path
    results: list["IPytestResult"]

    def to_html(self) -> str:
        """Format debug information as HTML"""
        debug_parts = [
            """
            <style>
                .debug-container {
                    font-family: ui-monospace, monospace;
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin: 1rem 0;
                }
                .debug-title {
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                }
                .debug-section {
                    margin: 0.5rem 0;
                }
                .debug-result {
                    margin: 1rem 0;
                    padding: 0.5rem;
                    border: 1px solid #e5e7eb;
                    border-radius: 0.375rem;
                }
                .debug-list {
                    margin-left: 1rem;
                }
            </style>
            <div class="debug-container">
        """
        ]

        # Overall test run info
        debug_parts.append('<div class="debug-title">Debug Information</div>')
        debug_parts.append(
            '<div class="debug-section">'
            f"Module: {self.module_name}<br>"
            f"Module file: {self.module_file}<br>"
            f"Number of results: {len(self.results)}"
            "</div>"
        )

        # Detailed results
        for i, result in enumerate(self.results, 1):
            debug_parts.append(
                f'<div class="debug-result">'
                f"<strong>Result #{i}</strong><br>"
                f"Status: {result.status.name if result.status else 'None'}<br>"
                f"Function: {result.function.name if result.function else 'None'}<br>"
                f"Solution attempts: {result.test_attempts}"
            )

            if result.test_results:
                debug_parts.append(
                    f'<div class="debug-section">'
                    f"Test Results ({len(result.test_results)}):"
                    '<div class="debug-list">'
                )
                for test in result.test_results:
                    debug_parts.append(
                        f"• {test.test_name}: {test.outcome.name}"
                        f"{f' - {type(test.exception).__name__}: {str(test.exception)}' if test.exception else ''}<br>"
                    )
                debug_parts.append("</div></div>")

            if result.exceptions:
                debug_parts.append(
                    f'<div class="debug-section">'
                    f"Exceptions ({len(result.exceptions)}):"
                    '<div class="debug-list">'
                )
                for exc in result.exceptions:
                    debug_parts.append(f"• {type(exc).__name__}: {str(exc)}<br>")
                debug_parts.append("</div></div>")

            debug_parts.append("</div>")

        debug_parts.append("</div>")

        return "\n".join(debug_parts)


@dataclass
class TestCaseResult:
    """Container class to store the test results when we collect them"""

    test_name: str
    outcome: TestOutcome
    exception: BaseException | None = None
    traceback: TracebackType | None = None
    formatted_exception: str = ""
    stdout: str = ""
    stderr: str = ""
    report_output: str = ""

    def __str__(self) -> str:
        """Basic string representation"""
        return (
            f"TestCaseResult(\n"
            f"  test_name: {self.test_name}\n"
            f"  outcome: {self.outcome.name if self.outcome else 'None'}\n"
            f"  exception: {type(self.exception).__name__ if self.exception else 'None'}"
            f" - {str(self.exception) if self.exception else ''}\n"
            f"  formatted_exception: {self.formatted_exception[:100]}..."
            f" ({len(self.formatted_exception)} chars)\n"
            f"  stdout: {len(self.stdout)} chars\n"
            f"  stderr: {len(self.stderr)} chars\n"
            f"  report_output: {len(self.report_output)} chars\n"
            ")"
        )

    def to_html(self) -> str:
        """HTML representation of the test result"""
        # CSS styles for the output
        styles = """
        <style>
            .test-result {
                font-family: system-ui, -apple-system, sans-serif;
                margin: 0.75rem 0;
                padding: 1rem;
                border-radius: 0.5rem;
                transition: all 0.2s ease;
            }
            .test-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 0.75rem;
            }
            .test-icon {
                font-size: 1.25rem;
                width: 1.5rem;
                height: 1.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .test-name {
                font-family: ui-monospace, monospace;
                font-size: 0.9rem;
                padding: 0.25rem 0.5rem;
                background: rgba(0, 0, 0, 0.05);
                border-radius: 0.25rem;
            }
            .test-status {
                font-weight: 600;
                font-size: 1rem;
            }
            .test-pass {
                background-color: #f0fdf4;
                border: 1px solid #86efac;
            }
            .test-fail {
                background-color: #fef2f2;
                border: 1px solid #fecaca;
            }
            .test-error {
                background-color: #fff7ed;
                border: 1px solid #fed7aa;
            }
            .error-block {
                background-color: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.1);
                padding: 1rem;
                border-radius: 0.375rem;
                margin-top: 0.75rem;
            }
            .error-title {
                font-weight: 600;
                color: #dc2626;
                margin-bottom: 0.5rem;
            }
            .error-message {
                font-family: ui-monospace, monospace;
                font-size: 0.9rem;
                white-space: pre-wrap;
                margin: 0;
            }
            .output-section {
                margin-top: 0.75rem;
            }
            .output-tabs {
                display: flex;
                gap: 0.5rem;
                border-bottom: 1px solid #e5e7eb;
                margin-bottom: 0.5rem;
            }
            .output-tab {
                border: none;
                background: transparent;
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                color: #6b7280;
            }
            .output-tab.active {
                border-bottom-color: #3b82f6;
                color: #1f2937;
                font-weight: 500;
            }
            .output-content {
                padding: 1rem;
                background: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 0.375rem;
            }
            .output-pane {
                display: none;
            }
            .output-pane.active {
                display: block;
            }
        </style>
        """

        # Determine test status and icon
        match self.outcome:
            case TestOutcome.PASS:
                status_class = "test-pass"
                icon = "✅"
                status_text = "Passed"
            case TestOutcome.FAIL:
                status_class = "test-fail"
                icon = "❌"
                status_text = "Failed"
            case TestOutcome.TEST_ERROR:
                status_class = "test-error"
                icon = "🚨"
                status_text = "Syntax Error"
            case _:
                status_class = "test-error"
                icon = "⚠️"
                status_text = "Error"

        # Start building the HTML content
        test_name = self.test_name.split("::")[-1]
        html_parts = [styles]

        # Main container
        html_parts.append(
            f"""
        <div class="test-result {status_class}">
            <div class="test-header">
                <span class="test-icon">{icon}</span>
                {f'<span class="test-name">{html.escape(test_name)}</span>' if test_name else ""}
                <span class="test-status">{html.escape(status_text)}</span>
            </div>
        """
        )

        # Exception information if test failed
        if self.exception is not None:
            exception_type = type(self.exception).__name__
            exception_message = strip_ansi_codes(str(self.exception))

            html_parts.append(
                f"""
            <div class="error-block">
                <div class="error-title">{html.escape(exception_type)}</div>
                <pre class="error-message">{html.escape(exception_message)}</pre>
            </div>
            """
            )

        # Output sections (if any)
        if self.stdout or self.stderr:
            # Generate unique IDs for this test's tabs
            tab_id = f"test_{hash(self.test_name)}"
            html_parts.append(
                f"""
                        <div id="{tab_id}_container" class="output-section">
                            <div class="output-tabs">
                                <button class="output-tab active"
                                        onclick="
                                            document.querySelectorAll('#{tab_id}_container .output-tab').forEach(t => t.classList.remove('active'));
                                            document.querySelectorAll('#{tab_id}_container .output-pane').forEach(p => p.classList.remove('active'));
                                            this.classList.add('active');
                                            document.querySelector('#{tab_id}_output').classList.add('active');"
                                >Output</button>
                                <button class="output-tab"
                                        onclick="
                                            document.querySelectorAll('#{tab_id}_container .output-tab').forEach(t => t.classList.remove('active'));
                                            document.querySelectorAll('#{tab_id}_container .output-pane').forEach(p => p.classList.remove('active'));
                                            this.classList.add('active');
                                            document.querySelector('#{tab_id}_error').classList.add('active');"
                                >Error</button>
                            </div>
                            <div class="output-content">
                                <div id="{tab_id}_output" class="output-pane active">
                                    <pre>{html.escape(strip_ansi_codes(self.stdout)) if self.stdout else "No output"}</pre>
                                </div>
                                <div id="{tab_id}_error" class="output-pane">
                                    <pre>{html.escape(strip_ansi_codes(self.stderr)) if self.stderr else "No errors"}</pre>
                                </div>
                            </div>
                        </div>
                        """
            )

        # Close main div
        html_parts.append("</div>")

        return "\n".join(html_parts)


@dataclass
class AFunction:
    """Container class to store a function and its metadata"""

    name: str
    implementation: Callable[..., Any]
    source_code: str | None


@dataclass
class IPytestResult:
    """Class to store the results of running pytest on a solution function"""

    function: AFunction | None = None
    status: IPytestOutcome | None = None
    test_results: list[TestCaseResult] | None = None
    exceptions: list[BaseException] | None = None
    test_attempts: int = 0
    cell_content: str | None = None


@dataclass
class TestResultOutput:
    """Class to prepare and display test results in a Jupyter notebook"""

    ipytest_result: IPytestResult
    solution: str | None = None
    MAX_ATTEMPTS: ClassVar[int] = 3
    openai_client: OpenAIWrapper | None = None

    def display_results(self) -> None:
        """Display the test results in an output widget as a VBox"""
        cells = []

        output_cell = self.prepare_output_cell()
        solution_cell = self.prepare_solution_cell()

        cells.append(output_cell)

        tests_finished = self.ipytest_result.status == IPytestOutcome.FINISHED
        success = (
            all(
                test.outcome == TestOutcome.PASS
                for test in self.ipytest_result.test_results
            )
            if self.ipytest_result.test_results
            else False
        )

        if success or self.ipytest_result.test_attempts >= self.MAX_ATTEMPTS:
            cells.append(solution_cell)
        else:
            if tests_finished:
                attempts_remaining = (
                    self.MAX_ATTEMPTS - self.ipytest_result.test_attempts
                )
                cells.append(
                    HTML(
                        '<div style="margin-top: 1.5rem; font-family: system-ui, -apple-system, sans-serif;">'
                        f'<div style="display: flex; align-items: center; gap: 0.5rem;">'
                        '<span style="font-size: 1.2rem;">📝</span>'
                        '<span style="font-size: 1.1rem; font-weight: 500;">Solution will be available after '
                        f"{attempts_remaining} more failed attempt{'s' if attempts_remaining > 1 else ''}</span>"
                        "</div>"
                        "</div>"
                    )
                )

        ipython_display(
            ipywidgets.VBox(
                children=cells,
                layout={
                    "border": "1px solid #e5e7eb",
                    "background-color": "#ffffff",
                    "margin": "5px",
                    "padding": "0.75rem",
                    "border-radius": "0.5rem",
                },
            )
        )

    # TODO: This is left for reference if we ever want to bring back this styling
    # Perhaps we should remove it if it's unnecessary
    def __prepare_solution_cell(self) -> ipywidgets.Widget:
        """Prepare the cell to display the solution code with a redacted effect until revealed"""
        # Generate a unique ID for each solution cell
        uuid = f"solution_{id(self)}"

        styles = """
        <style>
            .solution-container {
                margin-top: 1.5rem;
                font-family: system-ui, -apple-system, sans-serif;
            }
            .solution-header {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 1rem;
                font-size: 1.1rem;
                font-weight: 500;
            }
            .solution-box {
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                overflow: hidden;
                background: #ffffff;
                padding: 0;  /* Remove padding from container */
            }
            .solution-code {
                position: relative;
            }
            .solution-code pre {
                margin: 0;
                font-family: ui-monospace, monospace;
                line-height: 1.5;
            }
            /* Style adjustments for the IPython Code class output */
            .solution-code .highlight {
                margin: 0;
                padding: 1rem;  /* Add padding to the actual code content */
            }
            .solution-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: repeating-linear-gradient(
                    45deg,
                    rgba(30, 35, 40, 0.98),    /* Darker base color with higher opacity */
                    rgba(30, 35, 40, 0.98) 10px,
                    rgba(45, 50, 55, 0.98) 10px,  /* Slightly lighter but still dark */
                    rgba(45, 50, 55, 0.98) 20px
                );
                transition: opacity 0.3s ease;
                opacity: 1;
            }
            .solution-button {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                padding: 0.75rem 1.5rem;
                background: #4b88ff;  /* Slightly softer blue */
                color: white;
                border: none;
                border-radius: 0.5rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                z-index: 10;
                font-size: 0.95rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .solution-button:hover {
                background: #3b7bff;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
                transform: translate(-50%, -52%);
            }
            .solution-button:disabled {
                background: #94a3b8;
                cursor: not-allowed;
            }
        </style>
        """

        solution_cell = ipywidgets.Output()

        # Return an empty output widget if no solution is provided
        if self.solution is None:
            return solution_cell

        # Solution cell with redacted effect
        solution_cell.append_display_data(
            HTML(
                f"""
            {styles}
            <div class="solution-container">
                <div class="solution-header">
                    <span>👉</span>
                    <span>Proposed solution</span>
                </div>
                <div class="solution-box">
                    <div class="solution-code">
                        <div id="{uuid}_content">
                            {Code(data=self.solution, language="python")._repr_html_()}
                        </div>
                        <div class="solution-overlay" id="{uuid}_overlay">
                            <button class="solution-button" onclick="
                                document.getElementById('{uuid}_overlay').style.opacity = '0';
                                document.getElementById('{uuid}_overlay').style.pointerEvents = 'none';
                                this.style.display = 'none';
                            ">
                                Reveal Solution
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        """
            )
        )

        return solution_cell

    def prepare_solution_cell(self) -> ipywidgets.Widget:
        """Prepare the cell to display the solution code with a collapsible accordion"""
        # Return an empty output widget if no solution is provided
        if self.solution is None:
            return ipywidgets.Output()

        # Create the solution content
        solution_output = ipywidgets.Output(
            layout=ipywidgets.Layout(padding="1rem", border="1px solid #e5e7eb")
        )
        with solution_output:
            ipython_display(Code(data=self.solution, language="python"))

        # Create header with emoji
        header_output = ipywidgets.Output()
        with header_output:
            ipython_display(
                HTML(
                    '<div style="display: flex; align-items: center; gap: 0.5rem;">'
                    '<span style="font-size: 1.1rem;">👉</span>'
                    '<span style="font-size: 1.1rem; font-weight: 500;">Proposed solution</span>'
                    "</div>"
                )
            )

        # Create the collapsible accordion (closed by default)
        accordion = ipywidgets.Accordion(
            children=[solution_output],
            selected_index=None,  # Start collapsed
            titles=("View solution",),
            layout=ipywidgets.Layout(
                margin="1.5rem 0 0 0",
                border="1px solid #e5e7eb",
                border_radius="0.5rem",
            ),
        )

        return ipywidgets.VBox(
            children=[header_output, accordion],
            layout=ipywidgets.Layout(
                margin="0",
                padding="0",
            ),
        )

    def prepare_output_cell(self) -> ipywidgets.Output:
        """Prepare the cell to display the test results"""
        output_cell = ipywidgets.Output()

        # Header with test function name
        function = self.ipytest_result.function
        title = "Test Results for " if function else "Test Results "
        output_cell.append_display_data(
            HTML(
                '<div style="overflow: hidden;">'
                f'<h2 style="font-size: 1.5rem; margin: 0;">{title}'
                '<code style="font-size: 1.1rem; background: #f3f4f6; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-family: ui-monospace, monospace;">'
                f"solution_{function.name}</code></h2>"
                if function is not None
                else f'<h2 style="font-size: 1.5rem; margin: 0;">{title}</h2></div>'
            )
        )

        match self.ipytest_result.status:
            case (
                IPytestOutcome.COMPILE_ERROR
                | IPytestOutcome.PYTEST_ERROR
                | IPytestOutcome.UNKNOWN_ERROR
            ):
                # We know that there is exactly one exception
                assert self.ipytest_result.exceptions is not None
                # We know that there is no test results
                assert self.ipytest_result.test_results is None

                exception = self.ipytest_result.exceptions[0]

                # Create a TestCaseResult for consistency
                error_result = TestCaseResult(
                    test_name=f"error::solution_{function.name}" if function else "::",
                    outcome=TestOutcome.TEST_ERROR,
                    exception=exception,
                )

                output_cell.append_display_data(HTML(error_result.to_html()))

                if self.openai_client:
                    ai_explains = AIExplanation(
                        ipytest_result=self.ipytest_result,
                        exception=exception,
                        openai_client=self.openai_client,
                    )

                    output_cell.append_display_data(ai_explains.render())

            case IPytestOutcome.FINISHED if self.ipytest_result.test_results:
                # Calculate test statistics
                total_tests = len(self.ipytest_result.test_results)
                passed_tests = sum(
                    1
                    for test in self.ipytest_result.test_results
                    if test.outcome == TestOutcome.PASS
                )
                failed_tests = total_tests - passed_tests

                # Display summary
                output_cell.append_display_data(
                    HTML(
                        '<div style="margin-bottom: 1rem; font-size: 0.95rem;">'
                        f'<div style="color: #059669; margin-bottom: 0.25rem;">'
                        f"✅ {passed_tests}/{total_tests} tests passed</div>"
                        f'<div style="color: #dc2626;">'
                        f"❌ {failed_tests}/{total_tests} tests failed</div>"
                        "</div>"
                    )
                )

                # Display individual test results
                for test in self.ipytest_result.test_results:
                    output_cell.append_display_data(HTML(test.to_html()))

                failed_tests = [
                    test
                    for test in self.ipytest_result.test_results
                    if test.outcome != TestOutcome.PASS
                ]

                if self.openai_client and failed_tests:
                    ai_explains = AIExplanation(
                        ipytest_result=self.ipytest_result,
                        exception=failed_tests[0].exception,
                        openai_client=self.openai_client,
                    )

                    output_cell.append_display_data(ai_explains.render())

            case IPytestOutcome.SOLUTION_FUNCTION_MISSING:
                output_cell.append_display_data(
                    HTML(
                        '<div class="test-result test-error" style="margin-top: 1rem;">'
                        '<div class="error-title">Solution Function Missing</div>'
                        "<p>Please implement the required solution function.</p>"
                        "</div>"
                    )
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
        self.tests: dict[str, TestCaseResult] = {}

    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo):
        """Called when an individual test item has finished execution."""
        if call.when == "call":
            test_result = TestCaseResult(
                test_name=item.nodeid,
                outcome=TestOutcome.FAIL if call.excinfo else TestOutcome.PASS,
                exception=call.excinfo.value if call.excinfo else None,
                traceback=call.excinfo.tb if call.excinfo else None,
            )

            if call.excinfo:
                test_result.formatted_exception = str(
                    call.excinfo.getrepr(
                        showlocals=True,
                        style="long",
                        funcargs=True,
                        abspath=False,
                        chain=True,
                    )
                )

            self.tests[item.nodeid] = test_result

    def pytest_exception_interact(
        self, call: pytest.CallInfo, report: pytest.TestReport
    ):
        """Called when an exception was raised which can potentially be interactively handled."""
        if (exc := call.excinfo) is not None:
            # TODO: extract a stack summary from the traceback to inspect if the function to test raise an exception
            #    print([frame.name for frame in traceback.extract_tb(exc.tb)])
            # If something else than the test_* name is in that list, then we have a solution function that raised an exception
            outcome = (
                TestOutcome.FAIL
                if exc.errisinstance(AssertionError)
                or exc.errisinstance(pytest.fail.Exception)
                else TestOutcome.TEST_ERROR
            )
            self.tests[report.nodeid] = TestCaseResult(
                test_name=report.nodeid,
                outcome=outcome,
                exception=exc.value,
                traceback=exc.tb,
            )

    def pytest_runtest_logreport(self, report: pytest.TestReport):
        """Called to log the report of a test item."""
        if test_result := self.tests.get(report.nodeid):
            test_result.stdout = report.capstdout
            test_result.stderr = report.capstderr

            if report.failed:
                test_result.report_output = str(report.longrepr)
