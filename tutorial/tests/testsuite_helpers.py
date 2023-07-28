import re
from dataclasses import dataclass
from typing import Callable, List

import ipywidgets
import pytest
from IPython.core.display import HTML, Javascript
from IPython.display import Code, display
from nbconvert import filters


@dataclass
class TestResult:
    """Container class to store the test results when we collect them"""

    stdout: str
    stderr: str
    test_name: str
    success: bool


@dataclass
class OutputConfig:
    """Container class to store the information to display in the test output"""

    style: str
    name: str
    result: str


def format_success_failure(
    syntax_error: bool, success: bool, name: str
) -> OutputConfig:
    """
    Depending on the test results, returns a fragment that represents
    either an error message, a success message, or a syntax error warning
    """

    if syntax_error:
        return OutputConfig(
            "alert-warning",
            "Tests <strong>COULD NOT RUN</strong> for this cell.",
            "&#129300 Careful, looks like you have a syntax error.",
        )

    if not success:
        return OutputConfig(
            "alert-danger",
            f"Tests <strong>FAILED</strong> for the function <code>{name}</code>",
            "&#x1F631 Your solution was not correct!",
        )

    return OutputConfig(
        "alert-success",
        f"Tests <strong>PASSED</strong> for the function <code>{name}</code>",
        "&#x1F64C Congratulations, your solution was correct!",
    )


def format_long_stdout(text: str) -> str:
    """
    Format the error message lines of a long test stdout
    as an HTML that expands, by using the <details> element
    """

    stdout_body = re.split(r"_\s{3,}", text)[-1]
    stdout_filtered = list(
        filter(re.compile(r".*>E\s").match, stdout_body.splitlines())
    )
    html_body = "".join(f"<p>{line}</p>" for line in stdout_filtered)

    test_runs = f"""<details style="overflow-y: auto; max-height: 200px;"><summary><u>Click here to expand</u></summary><div>{html_body}</div></details></li>"""
    return test_runs


class TestResultOutput(ipywidgets.VBox):
    """Class to display the test results in a structured way"""

    def __init__(
        self,
        name: str = "",
        syntax_error: bool = False,
        success: bool = False,
        test_outputs: List[TestResult] = None,
        cell_exec_count: int = None,
        solution_body: str = None,
    ):
        output_config = format_success_failure(syntax_error, success, name)
        output_cell = ipywidgets.Output()

        # For each test, create an alert box with the appropriate message,
        # print the code output and display code errors in case of failure

        with output_cell:
            custom_div_style = '"border: 1px solid; border-color: lightgray; background-color: whitesmoke; margin: 5px; padding: 10px;"'
            display(HTML("<h3>Test results</h3>"))
            display(
                HTML(
                    f"""<div class="alert alert-box {output_config.style}"><h4>{output_config.name}</h4>{output_config.result}</div>"""
                )
            )

            if not syntax_error:
                if len(test_outputs) > 0 and test_outputs[0].stdout:
                    display(
                        HTML(
                            f"<h4>Code output:</h4> <div style={custom_div_style}>{test_outputs[0].stdout}</div>"
                        )
                    )

                display(
                    HTML(
                        f"""
                        <h4>We tested your solution <code>solution_{name}</code> with {'1 input' if len(test_outputs) == 1 else str(len(test_outputs)) + ' different inputs'}.
                    {"All tests passed!</h4>" if success else "Below you find the details for each test run:</h4>"}
                """
                    )
                )

                if not success:
                    for test in test_outputs:
                        test_name = test.test_name
                        if match := re.search(r"\[.*?\]", test_name):
                            test_name = re.sub(r"\[|\]", "", match.group())

                        display(
                            HTML(
                                f"""
                            <div style={custom_div_style}>
                                <h5>{"&#10004" if test.success else "&#10060"} Test {test_name}</h5>
                                {format_long_stdout(filters.ansi.ansi2html(test.stderr)) if not test.success else ""}
                            </div>
                        """
                            )
                        )
            else:
                display(
                    HTML(
                        "<h4>Your code cannot run because of the following error:</h4>"
                    )
                )

        # After 3 failed attempts or on success, reveal the proposed solution
        # using a Code box inside an Accordion to display the str containing all code

        solution_output = ipywidgets.Output()
        with solution_output:
            display(HTML("<h4>Proposed solution:</h4>"))

        solution_code = ipywidgets.Output()
        with solution_code:
            display(Code(language="python", data=f"{solution_body}"))

        solution_accordion = ipywidgets.Accordion(
            titles=("Click here to reveal",), children=[solution_code]
        )

        solution_box = ipywidgets.Box(
            children=[solution_output, solution_accordion],
            layout={
                "display": "block" if (cell_exec_count > 2 or success) else "none",
                "padding": "0 20px 0 0",
            },
        )

        # fix css styling
        display(
            Javascript(
                """
                    var divs = document.querySelectorAll(".jupyter-widget-Collapse-contents");
                    for (let div of divs) {
                        div.setAttribute("style", "padding: 0");
                    }
                """
            )
        )

        super().__init__(children=[output_cell, solution_box])


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
        self.tests: Dict[str, TestResult] = {}

    def pytest_runtest_logreport(self, report: pytest.TestReport):
        # Only collect the results if it did not fail
        if report.when == "teardown" and report.nodeid not in self.tests:
            self.tests[report.nodeid] = TestResult(
                report.capstdout, report.capstderr, report.nodeid, not report.failed
            )

    def pytest_exception_interact(
        self, node: pytest.Item, call: pytest.CallInfo, report: pytest.TestReport
    ):
        # We need to collect the results and the stderr if the test failed
        if report.failed:
            self.tests[node.nodeid] = TestResult(
                report.capstdout,
                str(call.excinfo.getrepr() if call.excinfo else ""),
                report.nodeid,
                False,
            )
