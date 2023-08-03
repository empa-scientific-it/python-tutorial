import ast
import pathlib
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Set

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

    test_runs = f"""
            <details style="overflow-y: auto; max-height: 200px;">
                <summary><u style="cursor: pointer;">Click here to expand</u></summary>
                <div style="padding-top: 15px;">{html_body}</div>
            </details>
        """
    return test_runs


class TestResultOutput(ipywidgets.VBox):
    """Class to display the test results in a structured way"""

    def __init__(
        self,
        test_outputs: List[TestResult],
        name: str = "",
        syntax_error: bool = False,
        success: bool = False,
        cell_exec_count: int = 0,
        solution_body: str = "",
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


class AstParser:
    """
    Helper class for extraction of function definitions and imports.
    To find all reference solutions:
    Parse the module file using the AST module and retrieve all function definitions and imports.
    For each reference solution store the names of all other functions used inside of it.
    """

    def __init__(self, module_file) -> None:
        self.module_file = module_file
        self.function_defs = {}
        self.function_imports = {}
        self.called_function_names = {}

        tree = ast.parse(open(self.module_file).read())

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

        solution_functions = [
            val
            for key, val in self.called_function_names.items()
            if key in f"reference_{name}"
        ][0]
        solution_code = ""

        for f in solution_functions:
            if f in self.function_defs:
                solution_code += ast.unparse(self.function_defs[f]) + "\n\n"
            elif f in self.function_imports:
                function_file = pathlib.Path(
                    f"{self.function_imports[f].replace('.', '/')}.py"
                )
                if function_file.exists():
                    function_file_tree = ast.parse(open(function_file).read())
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
