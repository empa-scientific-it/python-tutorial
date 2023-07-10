import dataclasses
import io
import pathlib
import re
from contextlib import redirect_stderr, redirect_stdout
from typing import Callable, Dict, List, Optional

import ipynbname
import ipywidgets
import pytest
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import HTML, Javascript, display
from nbconvert import filters

import warnings
warnings.filterwarnings('ignore')


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


def find_solution(ns: Dict[str, Callable], postfix: str) -> Optional[Callable]:
    """Given a namespace, finds a solution matching a given pattern."""
    return [f for k, f in ns if k.endswith(postfix)][0]


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
    """Container class to store the test results when we collect them"""
    stdout: str
    stderr: str
    test_name: str
    success: bool


@dataclasses.dataclass
class OutputConfig:
    """Container class to store the information to display in the test output"""
    style: str
    name: str
    result: str


def format_success_failure(syntax_error: bool, success: bool, name: str) -> OutputConfig:
    """
    Depending on the test results, returns a fragment that represents
    either an error message, a success message, or a syntax error warning
    """
    if syntax_error:
        return OutputConfig(
            "alert-warning",
            f"Tests <strong>CANNOT RUN</strong> for this cell.",
            "&#129300 Careful, looks like you have a syntax error.",
        )

    if success:
        return OutputConfig(
            "alert-success",
            f"Tests <strong>PASSED</strong> for the function <code>{name}</code>",
            "&#x1F64C Congratulations, your solution was correct!",
        )
    else:
        return OutputConfig(
            "alert-danger",
            f"Tests <strong>FAILED</strong> for the function <code>{name}</code>",
            "&#x1F631 Your solution was not correct!",
        )


def format_long_stdout(text: str) -> str:
    """
    Format a long test stdout as a HTML by using the <details> element
    """

    def join_lines(text: str) -> str:
        text = text.splitlines()
        return "".join(
            [f"<p>{line}</p>" for line in text[-6:-1]]
        )

    separator = 59 * ' _'
    text = text.split(separator)[-1]
    text_lines = "".join(join_lines(text))
    test_runs = "".join(
        [
            f"""<details style="overflow-y: scroll; max-height: 200px;"><summary><u>Click here to expand</u></summary><div>{text_lines}</div></details></li>"""
        ]
    )
    return test_runs


class TestResultOutput(ipywidgets.VBox):
    """Class to display the test results in a structured way"""

    def __init__(self, name: str, syntax_error: bool, success: bool, test_outputs: List[TestResult]):
        output_config = format_success_failure(syntax_error, success, name)
        output_cell = ipywidgets.Output()

        with output_cell:
            custom_div = '<div style="border: 1px solid; border-color: lightgray; background-color: whitesmoke; margin: 5px; padding: 10px;">'
            display(HTML("<h3>Test results</h3>"))
            display(HTML(f"""<div class="alert alert-box {output_config.style}"><h4>{output_config.name}</h4>{output_config.result}</div>"""))

            if not syntax_error:
                if len(test_outputs) > 0 and test_outputs[0].stdout:
                    display(HTML(f"<h4>Code output:</h4> {custom_div}{test_outputs[0].stdout}</div>"))

                message = f"<h4>We tested your solution <code>solution_{name}</code> {len(test_outputs)} times with different inputs. "
                if success:
                    message += "All tests passed!</h4>"
                else:
                    message += "Below you find the details for each test run:</h4>"

                    for test in test_outputs:
                        test_name = re.search(r'\[.*?\]', test.test_name).group()
                        test_name = re.sub('\[|\]', '', test_name)
                        message += f"{custom_div}<h5>Test {test_name}</h5>"
                        message += format_long_stdout(filters.ansi.ansi2html(test.stderr))
                        message += f"</div>"
            else:
                message = f"<h4>Your code cannot run because of the following error:</h4>"

            display(HTML(message))

        super().__init__(children=[output_cell])


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
                str(call.excinfo.getrepr()),
                report.nodeid,
                not report.failed,
            )


@pytest.fixture
def function_to_test():
    """Function to test, overridden at runtime by the cell magic"""


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

            outputs = []
            for name, function in functions_to_run.items():
                # Create the test collector
                result_collector = ResultCollector()
                # Run the tests
                with redirect_stderr(io.StringIO()) as pytest_stderr, redirect_stdout(io.StringIO()) as pytest_stdout:
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

                outputs.append(
                    TestResultOutput(
                        name,
                        False,
                        result == pytest.ExitCode.OK,
                        list(result_collector.tests.values()),
                    )
                )

            display(*(outputs))

            # hide cell outputs that were not generated by a function 
            display(Javascript("""      
                var output_divs = document.querySelectorAll(".jp-OutputArea-executeResult");
                for (let div of output_divs) {
                    div.setAttribute("style", "display: none;");
                }
            """))

            # remove syntax error styling
            display(Javascript("""      
                var output_divs = document.querySelectorAll(".jp-Cell-outputArea");
                for (let div of output_divs) {
                    var div_str = String(div.innerHTML);
                    if (div_str.includes("alert-success") | div_str.includes("alert-danger")) {
                        div.setAttribute("style", "padding-bottom: 0;");  
                    }
                }
            """))

        except Exception as e:
            # Catches syntax errors and creates a custom warning
            display(TestResultOutput(
                None,
                True,
                False,
                None,
            ))

            display(Javascript("""      
                var syntax_error_containers = document.querySelectorAll('div[data-mime-type="application/vnd.jupyter.stderr"]');
                for (let container of syntax_error_containers) {
                    var syntax_error_div = container.parentNode;
                    var container_div = syntax_error_div.parentNode;
                    const container_style = "position: relative; padding-bottom: " + syntax_error_div.clientHeight + "px;";
                    container_div.setAttribute("style", container_style);
                    syntax_error_div.setAttribute("style", "position: absolute; bottom: 10px;");
                }
            """))


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    ipython.register_magics(TestMagic)
