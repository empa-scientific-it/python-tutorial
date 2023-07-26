"""A module to define the `%%ipytest` cell magic"""
import io
import pathlib
import re
import ast
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from typing import Callable, Dict, List, Set

import ipynbname
import ipywidgets
import pytest
from IPython.core.display import HTML, Javascript
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import display, Code
from IPython import get_ipython
from nbconvert import filters


def _name_from_line(line: str = None):
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


def get_module_name(line: str, globals_dict: Dict = None) -> str:
    """Fetch the test module name"""

    module_name = (
        _name_from_line(line)
        or _name_from_ipynbname()
        or _name_from_globals(globals_dict)
    )

    if not module_name:
        raise RuntimeError(
            "Test module is undefined. Did you provide an argument to %%ipytest?"
        )

    return module_name


class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        # Override the abstract `function_to_test` fixture function
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])


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
    stdout_filtered = list(filter(re.compile(".*>E\s").match, stdout_body.splitlines()))
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
            display(
                HTML(
                    "<h4>Proposed solution:</h4>"
                )
            )

        solution_code = ipywidgets.Output()
        with solution_code:
            display(
                Code(
                    language="python",
                    data=f"{solution_body}"
                )
            )

        solution_accordion = ipywidgets.Accordion(
            titles=("Click here to reveal", ),
            children=[solution_code]
        )

        solution_box = ipywidgets.Box(
            children=[solution_output, solution_accordion],
            layout={"display": "block" if (cell_exec_count > 2 or success) else "none", "padding": "0 20px 0 0"}
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


class ResultCollector:
    """A class that will collect the result of a test. If behaves a bit like a visitor pattern"""

    def __init__(self) -> None:
        self.tests: Dict[str, TestResult] = {}

    def pytest_runtest_logreport(self, report: pytest.TestReport):
        # Only collect the results if it did not fail
        if report.when == "teardown" and not report.nodeid in self.tests:
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


@pytest.fixture
def function_to_test():
    """Function to test, overridden at runtime by the cell magic"""


@magics_class
class TestMagic(Magics):
    """Class to add the test cell magic"""

    shell: InteractiveShell

    cells = {}

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
        result = self.shell.run_cell(cell)

        try:
            result.raise_error()

            # Retrieve the functions names defined in the current cell
            # Only functions with names starting with `solution_` will be candidates for tests
            functions_names = re.findall(r"^def\s+(solution_.*?)\s*\(", cell, re.M)

            # Get the functions objects from user namespace
            functions_to_run = {}
            for name, function in self.shell.user_ns.items():
                if name in functions_names and callable(function):
                    functions_to_run[name.removeprefix("solution_")] = function

            if not functions_to_run:
                raise ValueError("No function to test defined in the cell")

            # store execution count information for each cell
            ipython_info = get_ipython()
            cell_id = ipython_info.parent_header["metadata"]["cellId"]
            if cell_id in self.cells:
                self.cells[cell_id] += 1
            else:
                self.cells[cell_id] = 1
 
            # Find all reference solutions:
            # Parse the file using the AST module and retrieve all function definitions and imports
            # For each reference solution store the names of all other functions used inside of it
            tree = ast.parse(open(module_file, "r").read())
            function_defs = {}
            function_imports = {}
            called_function_names = {}

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_defs[node.name] = node
                elif isinstance(node, (ast.Import, ast.ImportFrom)) and hasattr(node, 'module'):
                    for n in node.names:
                        function_imports[n.name] = node.module
            
            for node in tree.body:
                if node in function_defs.values() and node.name.startswith("reference_"):
                    called_function_names[node.name] = retrieve_functions({**function_defs, **function_imports}, node, {node.name})

            outputs = []
            for name, function in functions_to_run.items():
                # Create the test collector
                result_collector = ResultCollector()
                # Run the tests
                with redirect_stderr(io.StringIO()) as pytest_stderr, redirect_stdout(
                    io.StringIO()
                ) as pytest_stdout:
                    result = pytest.main(
                        [
                            "-q",
                            f"{module_file}::test_{name}",
                        ],
                        plugins=[
                            FunctionInjectionPlugin(function),
                            result_collector,
                        ],
                    )
                    # Read pytest output to prevent it from being displayed
                    pytest_output = pytest_stdout.getvalue()
                    pytest_error = pytest_stderr.getvalue()

                # Find the respective reference solution for the executed function
                # Create a str containing its code and the code of all other functions used,
                # whether coming from the same file or an imported one
                solution_functions = [val for key, val in called_function_names.items() if key in f"reference_{name}"][0]
                solution_code = ""

                for f in solution_functions:
                    if f in function_defs:
                        solution_code += ast.unparse(function_defs[f]) + "\n\n"
                    elif f in function_imports:
                        function_file = pathlib.Path(f"{function_imports[f].replace('.', '/')}.py")
                        if function_file.exists():
                            function_file_tree = ast.parse(open(function_file, "r").read())
                            for node in function_file_tree.body:
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == f:
                                    solution_code += ast.unparse(node) + "\n\n"
                
                outputs.append(
                    TestResultOutput(
                        name,
                        False,
                        result == pytest.ExitCode.OK,
                        list(result_collector.tests.values()),
                        self.cells[cell_id],
                        solution_code,
                    )
                )

            display(*outputs)

            # hide cell outputs that were not generated by a function
            display(
                Javascript(
                    """      
                var output_divs = document.querySelectorAll(".jp-OutputArea-executeResult");
                for (let div of output_divs) {
                    div.setAttribute("style", "display: none;");
                }
            """
                )
            )

            # remove syntax error styling
            display(
                Javascript(
                    """      
                var output_divs = document.querySelectorAll(".jp-Cell-outputArea");
                for (let div of output_divs) {
                    var div_str = String(div.innerHTML);
                    if (div_str.includes("alert-success") | div_str.includes("alert-danger")) {
                        div.setAttribute("style", "padding-bottom: 0;");  
                    }
                }
            """
                )
            )

        except Exception:
            # Catches syntax errors and creates a custom warning
            display(
                TestResultOutput(
                    syntax_error=True,
                    success=False,
                )
            )

            display(
                Javascript(
                    """      
                var syntax_error_containers = document.querySelectorAll('div[data-mime-type="application/vnd.jupyter.stderr"]');
                for (let container of syntax_error_containers) {
                    var syntax_error_div = container.parentNode;
                    var container_div = syntax_error_div.parentNode;
                    const container_style = "position: relative; padding-bottom: " + syntax_error_div.clientHeight + "px;";
                    container_div.setAttribute("style", container_style);
                    syntax_error_div.setAttribute("style", "position: absolute; bottom: 10px;");
                }
            """
                )
            )


def retrieve_functions(all_functions: Dict, node: object, called_functions: Set[str]) -> Set[object]:
    """Recursively walk the AST tree to retrieve all function definitions in a file"""

    for n in ast.walk(node):
        if isinstance(n, ast.Call) and hasattr(n.func, 'id'):
            called_functions.add(n.func.id)
            if n.func.id in all_functions:
                called_functions = retrieve_functions(all_functions, all_functions[n.func.id], called_functions)
        for child in ast.iter_child_nodes(n):
            called_functions = retrieve_functions(all_functions, child, called_functions)
    return called_functions


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """

    ipython.register_magics(TestMagic)
