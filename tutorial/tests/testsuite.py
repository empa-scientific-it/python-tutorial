import io
from typing import Callable
from contextlib import redirect_stdout

import pytest
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import HTML, display


class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        """Override the abstract `function_to_test` fixture function"""
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])


@magics_class
class TestMagic(Magics):
    """
    Implements an IPython cell magic that can be used to automatically run a test case
    The test is defined by the class `TestCase` and applied to the function `function_name`
    on cells marked with `%%celltest function_name test_module.TestCase`
    """

    shell: InteractiveShell

    @magic_arguments()
    @argument(
        "test_function", type=str, help="The function to test in the following cell"
    )
    @argument("test", type=str, help="The test case class")
    @cell_magic
    def pytest_cell(self, line, cell) -> None:
        """The %%pytest_cell magic"""
        # Parse magic's arguments
        args = parse_argstring(self.pytest_cell, line)

        # Run cell
        self.shell.run_cell(cell)

        # Extract the function definition from the environment
        if (test_function := self.shell.user_ns.get(args.test_function)) is None:
            raise ValueError(
                f"There is no function called '{args.test_function}' in the scope"
            )

        # Run the test
        test_module, test_class = args.test.split("::")
        with redirect_stdout(io.StringIO()) as pytest_stdout:
            result = pytest.main(
                ["-q", f"tutorial/tests/{test_module}.py::{test_class}"],
                plugins=[FunctionInjectionPlugin(test_function)],
            )

        # Read pytest output
        pytest_output = pytest_stdout.getvalue()

        if result == pytest.ExitCode.OK:
            color, title, test_result = (
                "alert-success",
                "Tests <strong>PASSED</strong>",
                "&#x1F64C Congratulations, your solution was correct!",
            )
        else:
            color, title, test_result = (
                "alert-danger",
                "Tests <strong>FAILED</strong>",
                "&#x1F631 Your solution was not correct!",
            )

            # Print all pytest output
            print(pytest_output)

            # Print only a summary
            # lines = pytest_output.split("\n")
            # summary_start = next(
            #     i for i, line in enumerate(lines) if "short test summary info" in line
            # )
            # print(f"{lines[0]}\n" + "\n".join(lines[summary_start:]))

        display(
            HTML(
                f"""<div class="alert alert-box {color}"><h4>{title}</h4>{test_result}</div>"""
            )
        )


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # This class must then be registered with a manually created instance,
    # since its constructor has different arguments from the default:
    magics = TestMagic(ipython)
    ipython.register_magics(magics)
