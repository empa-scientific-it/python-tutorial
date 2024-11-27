from typing import Callable, Dict

import pytest

from .helpers import TestCaseResult, TestOutcome


@pytest.fixture
def solution_globals():
    """A fixture to hold globals of the solution function"""


@pytest.fixture
def function_to_test():
    """Function to test, overridden at runtime by the cell magic"""


class FunctionInjectionPlugin:
    """A class to inject a function to test"""

    def __init__(self, function_to_test: Callable) -> None:
        self.function_to_test = function_to_test
        self.globals = function_to_test.__globals__

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        # Override the abstract `function_to_test` fixture function
        if "function_to_test" in metafunc.fixturenames:
            metafunc.parametrize("function_to_test", [self.function_to_test])
        # Make state available to tests
        if "solution_globals" in metafunc.fixturenames:
            metafunc.parametrize("solution_globals", [self.globals])


class ResultCollector:
    """A class that will collect the result of a test. If behaves a bit like a visitor pattern"""

    def __init__(self) -> None:
        self.tests: Dict[str, TestCaseResult] = {}

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
